#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from mentor_pipeline.api import fetch_mentor_data
from mentor_pipeline.utils import sanitize_string


class Mentor(object):
    def __init__(self, id, data=None):
        self.id = id
        self.load(data)

    def load(self, data=None):
        if data is None:
            data = fetch_mentor_data(self.id)
        self.name = data["name"]
        self.title = data["title"]
        self.topics = []
        for subject in data["subjects"]:
            self.topics.append(subject["name"])
        self.questions_by_id = {}
        self.questions_by_text = {}
        self.questions_by_answer = {}
        for question in data["questions"]:
            # TODO: paraphrases
            id = question["id"]
            q = {
                "question": question["question"],
                "answer": question["transcript"],
                "video": question["video"],
            }
            q["topics"] = [question["subject"]["name"]]
            for topic in question["topics"]:
                q["topics"].append(topic["name"])
                if topic["name"] not in self.topics:
                    self.topics.append(topic["name"])
            self.questions_by_id[id] = q
            self.questions_by_text[sanitize_string(question["question"])] = q
            self.questions_by_answer[sanitize_string(question["answer"])] = q
