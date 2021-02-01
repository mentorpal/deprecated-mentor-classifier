#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from mentor_classifier.api import fetch_mentor_data
from mentor_classifier.utils import sanitize_string

import logging

class Mentor(object):
    def __init__(self, id, data=None):
        logging.warning(f"init mentor for id {id}")
        self.id = id
        self.load(data)

    def load(self, data=None):
        logging.warning(f"loading data for mentor: {data}")
        if data is None:
            logging.warning(f"fetching data for mentor {self.id}")
            data = fetch_mentor_data(self.id)
        logging.warning(f"data={data}")
        self.topics = ["Background", "About Me"]  # TODO
        # self.topics = []
        self.questions_by_id = {}
        self.questions_by_text = {}
        self.questions_by_answer = {}
        for answer in data["answers"]:
            if answer["status"] != "Complete":
                continue
            question = answer["question"]
            id = question["_id"]
            q = {
                "id": id,
                "question": question["question"],
                "answer": answer["transcript"],
                "video": answer["video"],
            }
            q["topics"] = ["Background", "About Me"]  # TODO
            # q["topics"] = [question["subject"]["name"]]
            # if question["subject"]["name"] not in self.topics:
            #     self.topics.append(question["subject"]["name"])
            # for topic in question["topics"]:
            #     q["topics"].append(topic["name"])
            #     if topic["name"] not in self.topics:
            #         self.topics.append(topic["name"])
            self.questions_by_id[id] = q
            self.questions_by_text[sanitize_string(question["question"])] = q
            self.questions_by_answer[sanitize_string(answer["transcript"])] = q
