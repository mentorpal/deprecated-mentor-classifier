#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from mentor_classifier.api import fetch_mentor_data
from mentor_classifier.utils import sanitize_string


class Mentor(object):
    def __init__(self, id):
        data = fetch_mentor_data(id)
        self.id = data["_id"]
        self.name = data["name"]
        self.firstName = data["firstName"]
        self.title = data["title"]
        self.mentorType = data["mentorType"]

        self.utterances_by_type = self.load_utterances_by_type(data)
        self.questions_by_id = self.load_questions(data)
        self.topics_by_id = self.load_topics(data)
        self.subjects_by_id = self.load_subjects(data)

        self.topics = []
        for subject in self.subjects_by_id:
            self.topics.append(subject["name"])
        for topic in self.topics_by_id:
            self.topics.append(topic["name"])

        self.questions_by_text = {}
        self.questions_by_answer = {}
        for qid in self.questions_by_id:
            q = self.questions_by_id[qid]
            self.questions_by_text[sanitize_string(q["question_text"])] = q
            for paraphrase in q["paraphrases"]:
                self.questions_by_text[sanitize_string(paraphrase)] = q
            self.questions_by_answer[sanitize_string(q["answer"])] = q

    def load_subjects(self, data=None):
        if data is None:
            data = fetch_mentor_data(self.id)
        subjects = []
        for subject in data.get("subjects", []):
            s = {
                "id": subject["_id"],
                "name": subject["name"],
                "topics": self.load_topics(subject),
                "questions": [],
            }
            for question in subject["questions"]:
                if question["_id"] in self.questions_by_id:
                    s["questions"].append(
                        {"id": question["_id"], "question_text": question["question"]}
                    )
            subjects.append(s)
        return subjects

    def load_topics(self, data=None):
        if data is None:
            data = fetch_mentor_data(self.id)
        topics = []
        for topic in data.get("topics", []):
            t = {
                "id": topic["_id"],
                "name": topic["name"],
                "questions": [],
            }
            for question in data.get("questions", []):
                if question["_id"] in self.questions_by_id:
                    for qtopic in question["topics"]:
                        if qtopic["_id"] == topic["_id"]:
                            t["questions"].append(
                                {
                                    "id": question["_id"],
                                    "question_text": question["question"],
                                }
                            )
            for answer in data.get("answers", []):
                question = answer["question"]
                if question["_id"] in self.questions_by_id:
                    for qtopic in question["topics"]:
                        if qtopic["_id"] == topic["_id"]:
                            t["questions"].append(
                                {
                                    "id": question["_id"],
                                    "question_text": question["question"],
                                }
                            )
            topics.append(t)
        return topics

    def load_questions(self, data=None):
        if data is None:
            data = fetch_mentor_data(self.id)
        questions = {}
        for answer in data.get("answers", []):
            question = answer["question"]
            if answer["status"] != "COMPLETE" or question["type"] == "UTTERANCE":
                continue
            q = {
                "id": question["_id"],
                "question_text": question["question"],
                "paraphrases": question["paraphrases"],
                "answer": answer["transcript"],
                "answer_id": answer["_id"],
                "topics": [],
            }
            for topic in question["topics"]:
                q["topics"].append(topic["name"])
            questions[question["_id"]] = q
        return questions

    def load_utterances_by_type(self, data=None):
        if data is None:
            data = fetch_mentor_data(self.id)
        utterances = {}
        for answer in data.get("answers", []):
            question = answer["question"]
            if answer["status"] != "COMPLETE" or question["type"] != "UTTERANCE":
                continue
            if question["name"] not in utterances:
                utterances[question["name"]] = []
            utterances[question["name"]].append([answer["_id"], answer["transcript"]])
        return utterances
