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
from .types import Answer
from string import Template
from dataclasses import dataclass
from jobs_train import CustomSpacy

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
    def __init__(self, answers: List[Answer], shared_root: str):
        self.people: List[str] = []
        self.places: List[str] = []
        self.acronyms: List[str] = []
        self.jobs: List[str] = []
        self.load(answers, shared_root)

    def load(self, answers: List[Answer], shared_root: str):
        nlp = find_or_load_spacy("/Users/erice/Desktop/mentor-classifier/shared/installed/spacy-model/updated/model-best")
        for answer in answers:
            answer_doc = nlp(answer.transcript)
            if answer_doc.ents:
                for ent in answer_doc.ents:
                    if ent.label_ == "PERSON":
                        self.people.append(ent.text)
                        logging.warning(ent.text)
                    if ent.label == "ORG":
                        self.acronyms.append(ent.text)
                        logging.warning(ent.text)
                    if ent.label == "GPE":
                        self.places.append(ent.text)
                        logging.warning(ent.text)
                    if ent.label == "JOB":
                        logging.warning(ent.text)
                        self.jobs.append(ent.text)
            else:
                logging.warning("No named entities found.")

    def to_dict(self) -> Dict[str, List[str]]:
        entities = {
            "acronyms": self.acronyms,
            "people": self.people,
            "places": self.places,
        }
        return entities

    def generate_questions(self) -> List[FollowupQuestion]:
        questions = []
        for person in self.people:
            question_str = QUESTION_TEMPLATES["person"].substitute(entity=person)
            question = FollowupQuestion(question_str, person, "person")
            questions.append(question)
        for place in self.places:
            question_str = QUESTION_TEMPLATES["place"].substitute(entity=place)
            question = FollowupQuestion(question_str, place, "place")
            questions.append(question)
        for acronym in self.acronyms:
            question_str = QUESTION_TEMPLATES["acronym"].substitute(entity=acronym)
            question = FollowupQuestion(question_str, acronym, "acronym")
            questions.append(question)
        for job in self.jobs:
            question_str = QUESTION_TEMPLATES["job"].substitute(entity=job)
            question = FollowupQuestion(question_str, job, "job")
            questions.append(question)
        return questions
