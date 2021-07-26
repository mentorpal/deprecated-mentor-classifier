#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#

from dataclasses import dataclass
import logging
from os import path
from string import Template
from typing import List, Dict
from spacy.matcher import PhraseMatcher
from spacy import Language
from spacy.tokens.span import Span
from spacy.tokens import Doc
from spacy.symbols import VERB

from mentor_classifier.spacy_model import find_or_load_spacy
from mentor_classifier.types import AnswerInfo
from mentor_classifier.utils import get_shared_root

from sentence_transformers import util, SentenceTransformer
from mentor_classifier.sentence_transformer import find_or_load_sentence_transformer
from mentor_classifier.stopwords import STOPWORDS


QUESTION_TEMPLATES = {
    "person": Template("Can you tell me more about $entity?"),
    "place": Template("What was $entity like?"),
    "acronym": Template("What is $entity?"),
    "job": Template("What does a(n) $entity do?"),
}


@dataclass
class FollowupQuestion:
    question: str
    entity: str
    template: str
    weight: float = 0
    verb: str = ""


# this should be a dictionary for easier removal
@dataclass
class EntityObject:
    span: Span
    doc: Doc
    answer: Doc
    text: str
    weight: float = 0
    verb: str = ""


class NamedEntities:
    def __init__(self, answers: List[AnswerInfo], shared_root: str = ""):
        self.people: List[EntityObject] = []
        self.places: List[EntityObject] = []
        self.acronyms: List[EntityObject] = []
        self.model: Language
        self.transformer: SentenceTransformer
        self.load(answers, shared_root or get_shared_root())

    def load(self, answers: List[AnswerInfo], shared_root: str):
        self.model = find_or_load_spacy(path.join(shared_root, "spacy-model"))
        self.transformer = find_or_load_sentence_transformer(
            path.join(shared_root, "sentence-transformer")
        )
        person_set = set()
        acronym_set = set()
        place_set = set()
        for answer in answers:
            answer_doc = self.model(answer.answer_text)
            for sent in answer_doc.sents:
                if sent.ents:
                    for ent in sent.ents:
                        if (ent.label_ == "PERSON") and (ent.text not in person_set):
                            self.people.append(
                                EntityObject(ent, sent, answer_doc, ent.text)
                            )
                            person_set.add(ent.text)
                        if (ent.label_ == "ORG") and (ent.text not in acronym_set):
                            self.acronyms.append(
                                EntityObject(ent, sent, answer_doc, ent.text)
                            )
                            acronym_set.add(ent.text)
                        if (ent.label_ == "GPE" or ent.label_ == "LOC") and (
                            ent.text not in place_set
                        ):
                            self.places.append(
                                EntityObject(ent, sent, answer_doc, ent.text)
                            )
                            place_set.add(ent.text)

    def answer_blob(self, answers: List[AnswerInfo]):
        text_list = [answer.answer_text for answer in answers]
        answer_text = " ".join(text_list)
        for word in answer_text:
            if word in STOPWORDS:
                answer_text.replace(word, " ")
        return self.transformer.encode(answer_text, convert_to_tensor=True)

    def check_relevance(
        self,
        entity_vals: List[EntityObject],
        category_answers: List[AnswerInfo],
        entity_type: str,
    ) -> List[EntityObject]:
        blob = self.answer_blob(category_answers)
        for entity in entity_vals:
            verbs = [token for token in entity.doc if token.pos == VERB]
            if verbs == []:
                entity.weight = -1
                continue
            else:
                token = entity.answer[entity.span.start].head
                while not (token.pos == VERB or token.is_sent_start or token.is_punct):
                    if token == token.head:
                        break
                    token = token.head
                if token.pos == VERB:
                    verb = token.text
                else:
                    verb = verbs[0].text
                entity.verb = verb
                verb_tensor = self.transformer.encode(verb, convert_to_tensor=True)
                entity.weight = float(util.pytorch_cos_sim(blob, verb_tensor))
        return entity_vals

    def to_dict(self) -> Dict[str, List[str]]:
        entities = {
            "acronyms": [acronym.text for acronym in self.acronyms],
            "people": [person.text for person in self.people],
            "places": [place.text for place in self.places],
        }
        return entities

    def add_followups(
        self,
        entity_name: str,
        entity_vals: List[EntityObject],
        followups: List[FollowupQuestion],
    ) -> None:
        if entity_name not in QUESTION_TEMPLATES:
            logging.warning("invalid entity name")
            return  # no template for this entity
        template = QUESTION_TEMPLATES[entity_name]
        for e in entity_vals:
            followups.append(
                FollowupQuestion(
                    question=template.substitute(entity=e.text),
                    entity=e.text,
                    template=entity_name,
                    weight=e.weight,
                    verb=e.verb,
                )
            )

    def clean_ents(
        self,
        entity_vals: List[EntityObject],
        category_answers: List[AnswerInfo],
        all_answered: List[AnswerInfo],
        entity_type: str,
    ) -> List[EntityObject]:
        deduped = self.remove_duplicates(entity_vals, all_answered)
        relevant = self.check_relevance(deduped, category_answers, entity_type)
        return relevant

    def remove_duplicates(
        self, entity_vals: List[EntityObject], all_answered: List[AnswerInfo]
    ) -> List[EntityObject]:
        answered = [question.question_text for question in all_answered]
        matcher = PhraseMatcher(self.model.vocab)
        terms = [ent.text for ent in entity_vals]
        patterns = [self.model.make_doc(text) for text in terms]
        matcher.add("TerminologyList", patterns)
        for question in answered:
            doc = self.model(question)
            matches = matcher(doc)
            if not matches == []:
                for match_id, start, end in matches:
                    span = doc[start:end]
                    while span.text in terms:
                        i = terms.index(span.text)
                        del entity_vals[i]
                        del terms[i]
        return entity_vals

    def generate_questions(
        self, category_answers: List[AnswerInfo], all_answered: List[AnswerInfo]
    ) -> List[FollowupQuestion]:
        followups: List[FollowupQuestion] = []
        self.people = self.clean_ents(
            self.people, category_answers, all_answered, "person"
        )
        self.places = self.clean_ents(
            self.places, category_answers, all_answered, "place"
        )
        self.acronyms = self.clean_ents(
            self.acronyms, category_answers, all_answered, "acronym"
        )
        self.add_followups("person", self.people, followups)
        self.add_followups("place", self.places, followups)
        self.add_followups("acronym", self.acronyms, followups)
        import random

        random.shuffle(followups)
        followups.sort(key=lambda followup: followup.weight, reverse=True)
        return followups
