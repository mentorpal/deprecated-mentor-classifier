#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
import os
import requests
from typing import Dict, List, TypedDict

import pandas as pd

from mentor_classifier.ner import FollowupQuestion, NamedEntities
from .types import AnswerInfo


class GQLQueryBody(TypedDict):
    query: str
    variables: dict


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
query CategoryAnswers($category: String!) {
  me {
        categoryAnswers(category: $category) {
            answerText
            questionText
        }
    }
}
"""

GQL_QUERY_MENTOR_ME = """
query Mentor() {
    me {
        mentor(){
            answers() {
                _id
                question {
                    _id
                    question
                    paraphrases
                    type
                    name
                    mentor
                    mentorType
                    minVideoLength
            }
            transcript
            status
            media {
                type
                tag
                url
            }
        }
    }
}
"""


def __auth_gql(
    query: GQLQueryBody, cookies: Dict[str, str] = {}, headers: Dict[str, str] = {}
) -> dict:
    res = requests.post(GRAPHQL_ENDPOINT, json=query, cookies=cookies, headers=headers)
    res.raise_for_status()
    return res.json()


def query_mentor(mentor: str) -> GQLQueryBody:
    return {"query": GQL_QUERY_MENTOR, "variables": {"id": mentor}}


def query_me() -> GQLQueryBody:
    return {"query": GQL_QUERY_MENTOR_ME, "variables": {}}


def query_category_answers(category: str) -> GQLQueryBody:
    return {"query": GQL_CATEGORY_ANSWERS, "variables": {"category": category}}


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


def fetch_me_data(cookies: Dict[str, str] = {}, headers: Dict[str, str] = {}) -> dict:
    tdjson = __auth_gql(query_me(), cookies=cookies, headers=headers)
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))
    data = tdjson["data"]["me"]["mentor"]
    return data


def fetch_category(
    category: str, cookies: Dict[str, str] = {}, headers: Dict[str, str] = {}
) -> dict:
    tdjson = __auth_gql(
        query_category_answers(category), cookies=cookies, headers=headers
    )
    return tdjson.get("data") or {}


def generate_followups(
    category: str,
    cookies: Dict[str, str] = {},
    headers: Dict[str, str] = {},
) -> List[FollowupQuestion]:
    data = fetch_category(category, cookies=cookies, headers=headers)
    me = data.get("me")
    if me is None:
        raise NameError("me not found")
    category_answer = me.get("categoryAnswers", [])
    category_answers = [
        AnswerInfo(
            answer_text=answer_data.get("answerText") or "",
            question_text=answer_data.get("questionText") or "",
        )
        for answer_data in category_answer
    ]
    all_answered = fetch_mentor_questions(cookies=cookies, headers=headers)
    followups = NamedEntities(category_answers).generate_questions(
        category_answers, all_answered
    )
    return followups


def fetch_mentor_questions(
    cookies: Dict[str, str] = {}, headers: Dict[str, str] = {}
) -> List[AnswerInfo]:
    data = fetch_me_data(cookies=cookies, headers=headers)
    answered = [
        AnswerInfo(answer["question"]["question"], answer["transcript"])
        for answer in data.get("answers", [])
    ]
    return answered


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
