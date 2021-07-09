#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
import os
from os import path
import requests
import pandas as pd
from typing import TypedDict, List
from mentor_classifier.ner import FollowupQuestion, NamedEntities
from .types import Answer


class GQLQueryBody(TypedDict):
    query: str
    variables: dict


SHARED_ROOT = os.environ.get("SHARED_ROOT") or path.join(
    path.abspath(path.join("..", "shared")), "installed"
)

OFF_TOPIC_THRESHOLD_DEFAULT = (
    -0.55
)  # todo: this should probably be specific to the classifier arch?


def get_off_topic_threshold() -> float:
    try:
        return (
            float(str(os.environ.get("OFF_TOPIC_THRESHOLD") or ""))
            if "OFF_TOPIC_THRESHOLD" in os.environ
            else OFF_TOPIC_THRESHOLD_DEFAULT
        )
    except ValueError:
        return OFF_TOPIC_THRESHOLD_DEFAULT


GRAPHQL_ENDPOINT = os.environ.get("GRAPHQL_ENDPOINT") or "http://graphql/graphql"
GQL_QUERY_MENTOR = """
query Mentor($id: ID!) {
    mentor(id: $id) {
        subjects {
            name
        }
        topics {
            name
        }
        questions {
            question {
                _id
            }
            topics {
                name
            }
        }
        answers {
            _id
            status
            transcript
            question {
                _id
                question
                type
                name
                paraphrases
            }
            media {
                type
                tag
                url
            }
        }
    }
}
"""
GQL_UPDATE_MENTOR_TRAINING = """
mutation UpdateMentorTraining($id: ID!) {
    updateMentorTraining(id: $id) {
        _id
    }
}
"""
GQL_CREATE_USER_QUESTION = """
mutation UserQuestionCreate($userQuestion: UserQuestionCreateInput!) {
    userQuestionCreate(userQuestion: $userQuestion) {
        _id
    }
}
"""
GQL_CATEGORY_ANSWERS = """
query CategoryAnswers($category: ID!) {
  me {
    categoryAnswers(category: $category) {
      answerText
      questionText
    }
}
"""


def __auth_gql(query: GQLQueryBody) -> dict:
    res = requests.post(
        GRAPHQL_ENDPOINT,
        json=query,
    )
    res.raise_for_status()
    return res.json()


def query_mentor(mentor: str) -> GQLQueryBody:
    return {"query": GQL_QUERY_MENTOR, "variables": {"id": mentor}}


def query_category_answers(category: str) -> GQLQueryBody:
    return {"query": GQL_CATEGORY_ANSWERS, "variables": {"id": category}}


def mutation_update_training(mentor: str) -> GQLQueryBody:
    return {"query": GQL_UPDATE_MENTOR_TRAINING, "variables": {"id": mentor}}


def mutation_create_user_question(
    mentor: str, question: str, answer_id: str, answer_type: str, confidence: float
) -> GQLQueryBody:
    return {
        "query": GQL_CREATE_USER_QUESTION,
        "variables": {
            "userQuestion": {
                "mentor": mentor,
                "question": question,
                "classifierAnswer": answer_id,
                "classifierAnswerType": answer_type,
                "confidence": float(confidence),
            }
        },
    }


def fetch_training_data(mentor: str) -> pd.DataFrame:
    data = fetch_mentor_data(mentor)
    data_dict = {}
    data_list = []
    for answer in data.get("answers", []):
        question = answer["question"]
        q = {
            "id": question["_id"],
            "question_text": question["question"],
            "paraphrases": question["paraphrases"],
            "answer": answer["transcript"],
            "answer_id": answer["_id"],
            "media": answer.get("media", []),
            "topics": [],
        }
        data_dict[question["_id"]] = q
    for question in data.get("questions", []):
        dict_question = data_dict.get(question["question"]["_id"], None)
        if dict_question is not None:
            for topic in question["topics"]:
                data_dict[dict_question["id"]]["topics"].append(topic["name"])
    for key in data_dict:
        question = data_dict[key]
        topics = question["topics"]
        topic_str = "|".join(topics)
        current_question = question["question_text"]
        paraphrases = question["paraphrases"]
        paraphrase_str = "|".join(paraphrases)
        answer = question["answer"]
        answer_id = key
        data_list.append(
            [answer_id, current_question, paraphrase_str, answer, topic_str]
        )
    data_df = pd.DataFrame(
        data_list, columns=["id", "question", "paraphrases", "answer", "topic"]
    )
    return data_df


def fetch_mentor_data(mentor: str) -> dict:
    tdjson = __auth_gql(query_mentor(mentor))
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))
    data = tdjson["data"]["mentor"]
    return data


def fetch_category(category: str):
    tdjson = __auth_gql(query_category_answers(category))
    data = tdjson["data"]
    data = tdjson["data"]
    return data


def generate_followups(
    category: str, shared_root=SHARED_ROOT
) -> List[FollowupQuestion]:
    data = fetch_category(category)
    recorded = []
    id = 0
    me = data.get("me")
    category_answer = me.get("categoryAnswers", [])
    for answer_data in category_answer:
        answer_text = answer_data["answerText"]
        question_text = answer_data["questionText"]
        answer = Answer(
            _id=f"A{id}",
            status="COMPLETE",
            transcript=answer_text,
            question=question_text,
        )
        recorded.append(answer)
        id = id + 1
    followups = NamedEntities(recorded, shared_root).generate_questions()
    return followups


def update_training(mentor: str):
    tdjson = __auth_gql(mutation_update_training(mentor))
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))


def create_user_question(
    mentor: str,
    question: str,
    answer_id: str,
    answer_type: str,
    confidence: float,
) -> str:
    tdjson = __auth_gql(
        mutation_create_user_question(
            mentor, question, answer_id, answer_type, confidence
        )
    )
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))
    try:
        return tdjson["data"]["userQuestionCreate"]["_id"]
    except KeyError:
        return "error"
