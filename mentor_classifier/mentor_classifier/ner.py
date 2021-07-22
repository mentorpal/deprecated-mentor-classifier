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

from mentor_classifier.spacy_model import find_or_load_spacy
from mentor_classifier.types import AnswerInfo
from mentor_classifier.utils import get_shared_root
from spacy.tokens.span import Span as entity
from spacy.tokens import Doc, VERB

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


#this should be a dictionary for easier removal
@dataclass
class EntityObject:
    span: entity
    doc: Doc
    text: str
    weight: float


class NamedEntities:
    def __init__(self, answers: List[AnswerInfo], shared_root: str = ""):
        self.people: List[EntityObject] = []
        self.places: List[EntityObject] = []
        self.acronyms: List[EntityObject] = []
        self.model: Language
        self.load(answers, shared_root or get_shared_root())

    def load(self, answers: List[AnswerInfo], shared_root: str):
        self.model = find_or_load_spacy(path.join(shared_root, "spacy-model"))
        for answer in answers:
            answer_doc = self.model(answer.answer_text)
            if answer_doc.ents:
                for ent in answer_doc.ents:
                    if ent.label_ == "PERSON":
                        self.people.append(EntityObject(ent, answer_doc, ent.text))
                    if ent.label_ == "ORG":
                        self.acronyms.append(EntityObject(ent, answer_doc, ent.text))
                    if ent.label_ == "GPE" or ent.label_ == "LOC":
                        self.places.append(EntityObject(ent, answer_doc, ent.text))

            else:
                logging.warning("No named entities found.")

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
                    entity_type=e,
                    template=entity_name,
                )
            )

    def clean_ents(
        self, entity_vals: List[EntityObject], answered: List[str], entity_type: str
    ) -> List[EntityObject]:
        deduped = self.remove_duplicates(entity_vals, answered)
        relevant = self.check_relevance(deduped, entity_type)
        return relevant

    def remove_duplicates(
        self, entity_vals: List[EntityObject], answered: List[str]
    ) -> List[EntityObject]:
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

    def check_relevance(self, entity_vals: List[EntityObject], entity_type: str) -> List[EntityObject]:
        for entity in ent_vals:
            token = entity.doc[entity.span]
            verb = token.head
            while not verb.pos == VERB:
                verb = verb.head 
            if not verb.text in KEY_VERBS[entity_type]:
                del entity_vals[entity]
        return entity_vals

    def generate_questions(self, answered: List[AnswerInfo]) -> List[FollowupQuestion]:
        followups: List[FollowupQuestion] = []
        answered_list = [question.question_text for question in answered]
        self.people = self.clean_ents(self.people, answered_list)
        self.places = self.clean_ents(self.places, answered_list)
        self.acronyms = self.clean_ents(self.acronyms, answered_list)
        self.add_followups("person", self.people, followups)
        self.add_followups("place", self.places, followups)
        self.add_followups("acronym", self.acronyms, followups)
        return followups
