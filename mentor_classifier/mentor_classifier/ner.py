#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from sentence_transformers import util, SentenceTransformer
from dataclasses import dataclass
import logging
from os import path
from string import Template
from typing import List, Dict
from spacy.matcher import PhraseMatcher
from spacy import Language
import spacy
from mentor_classifier.spacy_model import find_or_load_spacy
from mentor_classifier.types import AnswerInfo
from mentor_classifier.utils import get_shared_root
from mentor_classifier.sentence_transformer import find_or_load_sentence_transformer
from spacy.symbols import VERB

QUESTION_TEMPLATES = {
    "person": Template("Can you tell me more about $entity?"),
    "place": Template("What was $entity like?"),
    "acronym": Template("What is $entity?"),
    "job": Template("What does a(n) $entity do?"),
}


@dataclass
class FollowupQuestion:
    question: str
    entity_type: str
    template: str


class NamedEntities:
    def __init__(self, answers: List[AnswerInfo], shared_root: str = ""):
        self.people: List[str] = []
        self.places: List[str] = []
        self.acronyms: List[str] = []
        self.model: Language
        self.transformer: SentenceTransformer
        self.load(answers, shared_root or get_shared_root())

    def load(self, answers: List[AnswerInfo], shared_root: str):
        self.model = find_or_load_spacy(path.join(shared_root, "spacy-model"))
        self.transformer = find_or_load_sentence_transformer(
            path.join(shared_root, "sentence-transformer")
        )
        for answer in answers:
            answer_doc = self.model(answer.answer_text)
            if answer_doc.ents:
                for ent in answer_doc.ents:
                    if ent.label_ == "PERSON":
                        self.people.append(ent.text)
                    if ent.label_ == "ORG":
                        self.acronyms.append(ent.text)
                    if ent.label_ == "GPE" or ent.label_ == "LOC":
                        self.places.append(ent.text)

    def to_dict(self) -> Dict[str, List[str]]:
        entities = {
            "acronyms": self.acronyms,
            "people": self.people,
            "places": self.places,
        }
        return entities

    def find_verbs(self, answers: List[AnswerInfo]):
        verbs = set()
        for answer in answers: 
            doc = self.model(answer.answer_text)
            for token in doc:
                if token.pos == VERB:
                    verbs.add(token)
        return list(verbs)
    
    def add_followups(
        self,
        entity_name: str,
        entity_vals: List[str],
        followups: List[FollowupQuestion],
    ) -> None:
        if entity_name not in QUESTION_TEMPLATES:
            logging.warning("invalid entity name")
            return  # no template for this entity
        template = QUESTION_TEMPLATES[entity_name]
        for e in entity_vals:
            followups.append(
                FollowupQuestion(
                    question=template.substitute(entity=e),
                    entity_type=e,
                    template=entity_name,
                )
            )

    def remove_duplicates(
        self, entity_vals: List[str], answered: List[str]
    ) -> List[str]:
        matcher = PhraseMatcher(self.model.vocab)
        terms = entity_vals
        patterns = [self.model.make_doc(text) for text in terms]
        matcher.add("TerminologyList", patterns)
        ent_set = set(entity_vals)
        for question in answered:
            doc = self.model(question)
            matches = matcher(doc)
            if not matches == []:
                for match_id, start, end in matches:
                    span = doc[start:end]
                    if span.text in ent_set:
                        ent_set.remove(span.text)
        return list(ent_set)

    def remove_similar(
        self,
        followups: List[FollowupQuestion],
        answered: List[str],
        similarity_threshold,
    ) -> None :
        followups_text = [followup.question for followup in followups]
        questions = answered + followups_text
        paraphrases = util.paraphrase_mining(self.transformer, questions)
        for paraphrase in paraphrases:
            score, i, j = paraphrase
            if score > similarity_threshold:
                if questions[i] in followups:
                    i = followups_text.index(question[i])
                    del followups_text[i]
                    del followups[i]
                elif questions[j] in followups:
                    followups_text.index(question[j])
                    del followups_text[j]
                    del followups[j]

    def generate_questions(self, answered: List[AnswerInfo]) -> List[FollowupQuestion]:
        followups: List[FollowupQuestion] = []
        direct = [question.question_text for question in answered]
        paraphrases = [
            paraphrase for question in answered for paraphrase in question.paraphrases
        ]
        answered_list = direct + paraphrases
        self.people = self.remove_duplicates(self.people, answered_list)
        self.places = self.remove_duplicates(self.places, answered_list)
        self.acronyms = self.remove_duplicates(self.acronyms, answered_list)
        self.add_followups("person", self.people, followups)
        self.add_followups("place", self.places, followups)
        self.add_followups("acronym", self.acronyms, followups)
        # self.remove_similar(followups, answered_list, 0.95)
        return followups
