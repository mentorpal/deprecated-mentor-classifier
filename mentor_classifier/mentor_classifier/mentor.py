#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from dataclasses import dataclass

from mentor_classifier.api import fetch_mentor_data
from mentor_classifier.utils import sanitize_string


@dataclass
class Media:
    type: str
    tag: str
    url: str


class Mentor(object):
    def __init__(self, id):
        self.id = id
        self.topics = []
        self.utterances_by_type = {}
        self.questions_by_id = {}
        self.questions_by_text = {}
        self.questions_by_answer = {}
        self.answer_id_by_answer = {}
        self.load()

    def load(self):
        data = fetch_mentor_data(self.id)
        for subject in data.get("subjects", []):
            self.topics.append(subject["name"])
        for topic in data.get("topics", []):
            self.topics.append(topic["name"])
        for answer in data.get("answers", []):
            question = answer["question"]
            if answer["status"] == "INCOMPLETE":
                continue
            if answer["status"] != "COMPLETE":
                if not answer["transcript"]:
                    continue
                if data.get("mentorType", "") == "VIDEO":
                    if (
                        not answer["webMedia"]
                        or not answer["mobileMedia"]
                        or not answer["webMedia"].get("url", "")
                        or not answer["mobileMedia"].get("url", "")
                    ):
                        continue
            if question["type"] == "UTTERANCE":
                if question["name"] not in self.utterances_by_type:
                    self.utterances_by_type[question["name"]] = []
                self.utterances_by_type[question["name"]].append(
                    [answer["_id"], answer["transcript"], answer.get("media", [])]
                )
                continue
            q = {
                "id": question["_id"],
                "question_text": question["question"],
                "paraphrases": question["paraphrases"],
                "answer": answer["transcript"],
                "answer_id": answer["_id"],
                "media": answer.get("media", []),
                "topics": [],
            }
            self.answer_id_by_answer[answer["_id"]] = answer["transcript"]
            self.questions_by_id[question["_id"]] = q
        for question in data.get("questions", []):
            q = self.questions_by_id.get(question["question"]["_id"], None)
            if q is not None:
                for topic in question["topics"]:
                    self.questions_by_id[q["id"]]["topics"].append(topic["name"])
                self.questions_by_text[sanitize_string(q["question_text"])] = q
                for paraphrase in q["paraphrases"]:
                    self.questions_by_text[sanitize_string(paraphrase)] = q
                self.questions_by_answer[sanitize_string(q["answer"])] = q
