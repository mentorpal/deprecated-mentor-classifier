#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import logging
from os import path
from typing import List, Dict
from mentor_classifier.spacy_model import find_or_load_spacy
from .types import AnswerInfo
from string import Template
from dataclasses import dataclass


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
    def __init__(self, answers: List[AnswerInfo], shared_root: str):
        self.people: List[str] = []
        self.places: List[str] = []
        self.acronyms: List[str] = []
        self.load(answers, shared_root)

    def load(self, answers: List[AnswerInfo], shared_root: str):
        nlp = find_or_load_spacy(path.join(shared_root, "spacy-model"))
        for answer in answers:
            answer_doc = nlp(answer.answer_text)
            if answer_doc.ents:
                for ent in answer_doc.ents:
                    if ent.label_ == "PERSON":
                        self.people.append(ent.text)
                    if ent.label == "ORG":
                        self.acronyms.append(ent.text)
                    if ent.label == "GPE":
                        self.places.append(ent.text)
            else:
                logging.warning("No named entities found.")

    def to_dict(self) -> Dict[str, List[str]]:
        entities = {
            "acronyms": self.acronyms,
            "people": self.people,
            "places": self.places,
        }
        return entities

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

    def generate_questions(self) -> List[FollowupQuestion]:
        questions: List[FollowupQuestion] = []
        self.add_followups("person", self.people, questions)
        self.add_followups("place", self.places, questions)
        self.add_followups("acronym", self.acronyms, questions)
        return questions
