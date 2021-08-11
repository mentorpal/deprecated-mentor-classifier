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
from typing import List, Dict, Set
from spacy.matcher import PhraseMatcher
from spacy import Language
from spacy.tokens.span import Span
from spacy.tokens import Doc
from spacy.symbols import VERB, nsubj

from mentor_classifier.spacy_model import find_or_load_spacy
from mentor_classifier.types import AnswerInfo
from mentor_classifier.utils import get_shared_root

from sentence_transformers import util, SentenceTransformer
import torch
from torch import Tensor
from mentor_classifier.sentence_transformer import find_or_load_sentence_transformer
from mentor_classifier.stopwords import STOPWORDS
import functools
import time
import csv

SIMILARITY_THRESHOLD = 0.92
POP_WEIGHT = -0.5
POP_THRESHOLD = 0.4
I_WEIGHT = 1

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
        self.people: Dict[str, EntityObject] = {}
        self.places: Dict[str, EntityObject] = {}
        self.acronyms: Dict[str, EntityObject] = {}
        self.model: Language
        self.transformer: SentenceTransformer
        self.pop_culture: Set[str] = set()
        self.answers = Tensor
        self.load(answers, shared_root or get_shared_root())

    def load(self, answers: List[AnswerInfo], shared_root: str):
        self.model = find_or_load_spacy(path.join(shared_root, "spacy-model"))
        self.transformer = find_or_load_sentence_transformer(
            path.join(shared_root, "sentence-transformer")
        )
        self.load_pop_culture()
        self.answers = self.answer_blob(answers)
        for answer in answers:
            answer_doc = self.model(answer.answer_text)
            for sent in answer_doc.sents:
                if sent.ents:
                    for ent in sent.ents:
                        if ent.label_ == "PERSON":
                            self.people[ent.text] = EntityObject(
                                ent, sent, answer_doc, ent.text
                            )
                        if ent.label_ == "ORG":
                            self.acronyms[ent.text] = EntityObject(
                                ent, sent, answer_doc, ent.text
                            )
                        if ent.label_ == "GPE" or ent.label_ == "LOC":
                            self.places[ent.text] = EntityObject(
                                ent, sent, answer_doc, ent.text
                            )

    def load_pop_culture(self):
        path = "/Users/erice/Desktop/mentor-classifier/mentor_classifier/tests/fixtures/data/pop_culture.csv"
        with open(path) as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                self.pop_culture.add(row[0])

    def answer_blob(self, answers: List[AnswerInfo]) -> Tensor:
        text_list = [answer.answer_text for answer in answers]
        tensors = []
        for answer in text_list:
            for word in answer:
                if word in STOPWORDS:
                    answer.replace(word, " ")
            tensors.append(self.transformer.encode(answer, convert_to_tensor=True))
        length = len(tensors)
        tensor = tensors[0]
        for i in range(1,length):
            tensor.add(tensors[i])
        return torch.div(tensor, length)

    def org_weight(self, blob: Tensor, entity: EntityObject):
        org_tensor = self.transformer.encode(entity.text, convert_to_tensor=True)
        weight = float(util.pytorch_cos_sim(blob, org_tensor))
        return weight

    def check_relevance(
        self,
        entity_vals: Dict[str, EntityObject],
        entity_type: str,
    ) -> Dict[str, EntityObject]:
        blob = self.answers
        for entity in entity_vals.keys():
            ent = entity_vals[entity]
            self.check_pop_culture(ent, blob)
            verbs = [token for token in ent.doc if token.pos == VERB]
            if verbs == []:
                ent.weight = -1
                continue
            else:
                token = ent.answer[ent.span.start]
                while not (token.pos == VERB or token.is_sent_start or token.is_punct):
                    token = token.head
                    if token.pos == VERB:
                        ent.verb = token.text
                        for child in token.children:
                            if child.dep == nsubj and child.text == "I":
                                ent.weight = ent.weight + I_WEIGHT
                    if token == token.head:
                        break
                if ent.verb == "":
                    ent.verb = verbs[0].text
                verb_tensor = self.transformer.encode(ent.verb, convert_to_tensor=True)
                ent.weight = ent.weight + float(util.pytorch_cos_sim(blob, verb_tensor))
        return entity_vals

    def add_followups(
        self,
        entity_name: str,
        entity_vals: Dict[str, EntityObject],
        followups: Dict[str, FollowupQuestion],
    ) -> None:
        if entity_name not in QUESTION_TEMPLATES:
            logging.warning("invalid entity name")
            return  # no template for this entity
        template = QUESTION_TEMPLATES[entity_name]
        for e in entity_vals.keys():
            ent = entity_vals[e]
            question = template.substitute(entity=ent.text)
            followups[question] = FollowupQuestion(
                question=question,
                entity=ent.text,
                template=entity_name,
                weight=ent.weight,
                verb=ent.verb,
            )

    def clean_ents(
        self,
        entity_vals: Dict[str, EntityObject],
        all_answered: List[AnswerInfo],
        entity_type: str,
    ) -> Dict[str, EntityObject]:
        deduped = self.remove_duplicates(entity_vals, all_answered)
        relevant = self.check_relevance(deduped, entity_type)
        return relevant

    def check_pop_culture(self, ent: EntityObject, blob: Tensor) -> None:
        lemma = ent.span.lemma_
        sim = self.org_weight(blob, ent)
        if lemma in self.pop_culture and sim <= POP_THRESHOLD:
            ent.weight = ent.weight + POP_WEIGHT

    def remove_duplicates(
        self, entity_vals: Dict[str, EntityObject], all_answered: List[AnswerInfo]
    ) -> Dict[str, EntityObject]:
        answered = "".join([question.question_text for question in all_answered])
        terms = [entity_vals[ent].text for ent in entity_vals.keys()]
        for term in terms:
            if term in answered:
                entity_vals.pop(term)
        return entity_vals

    # Very slow
    # def remove_similar(
    #     self,
    #     followups: Dict[str, FollowupQuestion],
    #     answered: List[AnswerInfo],
    #     similarity_threshold: float = SIMILARITY_THRESHOLD,
    # ) -> Dict[str, FollowupQuestion]:
    #     followups_text = [followups[followup].question for followup in followups.keys()]
    #     answered_text = [question.question_text for question in answered]
    #     questions = answered_text + followups_text
    #     paraphrases = util.paraphrase_mining(self.transformer, questions)
    #     for paraphrase in paraphrases:
    #         score, i, j = paraphrase
    #         if score > similarity_threshold:
    #             if questions[i] in followups:
    #                 followups.pop(questions[i])
    #             elif questions[j] in followups:
    #                 followups.pop(questions[j])
    #     return followups

    def generate_questions(
        self, category_answers: List[AnswerInfo], all_answered: List[AnswerInfo]
    ) -> List[FollowupQuestion]:
        followups: Dict[str, FollowupQuestion] = {}
        self.people = self.clean_ents(
            self.people, all_answered, "person"
        )
        self.places = self.clean_ents(
            self.places,all_answered, "place"
        )
        self.acronyms = self.clean_ents(
            self.acronyms, all_answered, "acronym"
        )
        self.add_followups("person", self.people, followups)
        self.add_followups("place", self.places, followups)
        self.add_followups("acronym", self.acronyms, followups)
        # followups = self.remove_similar(followups, all_answered)
        followups_list = list(followups.values())
        # import random 
        # random.shuffle(followups_list)
        followups_list.sort(key=lambda followup: followup.weight, reverse=True)
        return followups_list
