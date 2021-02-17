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
        self.id = id
        self.name = data["name"]
        self.short_name = data["firstName"]
        self.title = data["title"]
        self.topics = []
        self.subjects_by_id = {}
        self.topics_by_id = {}
        self.questions_by_id = {}
        self.questions_by_text = {}
        self.questions_by_answer = {}
        self.utterances_by_type = {
            "_IDLE_": [],
            "_INTRO_": [],
            "_OFF_TOPIC_": [],
            "_PROMPT_": [],
            "_FEEDBACK_": [],
            "_REPEAT_": [],
            "_REPEAT_BUMP_": [],
            "_PROFANITY_": [],
        }
        self.load_topics(data)
        self.load_questions(data)

    def load_topics(self, data):
        for s in data.get("subjects", []):
            self.topics.append(s["name"])
            subject = {"name": s["name"], "questions": [], "topics": []}
            for q in s.get("questions", []):
                subject["questions"].append(q["_id"])
                for topic in q.get("topics", []):
                    if topic["name"] not in self.topics:
                        self.topics.append(topic["name"])
                    if topic["_id"] not in subject["topics"]:
                        subject["topics"].append(topic["_id"])
                    if topic["_id"] not in self.topics_by_id:
                        self.topics_by_id[topic["_id"]] = {
                            "name": topic["name"],
                            "questions": [],
                        }
                    self.topics_by_id[topic["_id"]]["questions"].append(q["_id"])
            self.subjects_by_id[s["_id"]] = subject

    def load_questions(self, data):
        for answer in data["answers"]:
            question = answer["question"]
            qid = question["_id"]
            if answer["status"] != "COMPLETE":
                for sid in self.subjects_by_id:
                    if qid in self.subjects_by_id[sid]["questions"]:
                        self.subjects_by_id[sid]["questions"].remove(qid)
                for tid in self.topics_by_id:
                    if qid in self.topics_by_id[tid]["questions"]:
                        self.topics_by_id[tid]["questions"].remove(qid)
                continue
            if question["type"] == "UTTERANCE":
                self.utterances_by_type[question["name"]].append(
                    [qid, answer["transcript"]]
                )
                continue
            q = {
                "id": qid,
                "question_text": question["question"],
                "paraphrases": question["paraphrases"],
                "answer": answer["transcript"],
                "video": answer["video"],
                "topics": [],
            }
            for sid in self.subjects_by_id:
                if qid in self.subjects_by_id[sid]["questions"]:
                    q["topics"].append(self.subjects_by_id[sid]["name"])
            for tid in self.topics_by_id:
                if qid in self.topics_by_id[tid]["questions"]:
                    q["topics"].append(self.topics_by_id[tid]["name"])
            self.questions_by_id[qid] = q
            self.questions_by_text[sanitize_string(q["question_text"])] = q
            for paraphrase in question["paraphrases"]:
                self.questions_by_text[sanitize_string(paraphrase)] = q
            self.questions_by_answer[sanitize_string(q["answer"])] = q
