#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
import os
import requests
from typing import Dict, List, TypedDict, Tuple

import pandas as pd
from numpy.ndarray import tolist

from sentence_transformers import SentenceTransformer
from mentor_classifier.sentence_transformers import find_or_load_sentence_transformer
from mentor_classifier.ner import FollowupQuestion, NamedEntities
from .types import AnswerInfo
from torch import Tensor
from torch.Tensor import numpy, cpu, detach


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
GQL_SINGLE_ANSWER = """
query SingleAnswer() {
  me {
        singleAnswer() {
            answerText
            questionText
        }
    }
}
"""

GQL_EMBEDDINGS = """
query_Embeddings() {
  me {
        embedding() {
            answer,
            question,
            answer_embedding,
            question_embedding,
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


def query_category_answers(category: str) -> GQLQueryBody:
    return {"query": GQL_CATEGORY_ANSWERS, "variables": {"category": category}}


def query_single_answer() -> GQLQueryBody:
    return {"query": GQL_SINGLE_ANSWER, "variables": {}}


def query_embeddings() -> GQLQueryBody:
    return {"query": GQL_EMBEDDINGS, "variables": {}}


def mutation_create_answer_embedding(
    question: str, answer: str, question_embedding: str, answer_embedding: str
) -> GQLQueryBody:
    return {
        "query": GQL_CREATE_EMBEDDING,
        "variables": {
            "embedding": {
                "question": question,
                "answer": answer,
                "questionEmbedding": question_embedding,
                "answerEmbedding": answer_embedding,
            }
        },
    }


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


def fetch_answer(
    cookies: Dict[str, str] = {}, headers: Dict[str, str] = {}
) -> Tuple[str, str]:
    tdjson = __auth_gql(query_single_answer(), cookies=cookies, headers=headers)
    data = tdjson.get("data") or {}
    answer_data = data.get("me").get("singleAnswer")
    question = answer_data.get("questionText")
    answer = answer_data.get("answerText")
    return question, answer


def create_embeddings(cookies: Dict[str, str] = {}, headers: Dict[str, str] = {}):
    question, answer = fetch_answer()
    transformer = find_or_load_sentence_transformer(
        path.join(shared_root, "sentence-transformer")
    )
    question_embedding = transformer.encode(question).cpu().detach().numpy().tolist()
    answer_embedding = transformer.encode(answer).cpu().detach().numpy().tolist()
    json_question = json.dumps(question_embedding)
    json_answer = json.dumps(answer_embedding)
    tdjson = __auth_gql(
        mutation_create_answer_embedding(question, answer, json_question, json_answer),
        cookies=cookies,
        headers=headers,
    )
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))


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


def fetch_category(
    category: str, cookies: Dict[str, str] = {}, headers: Dict[str, str] = {}
) -> dict:
    tdjson = __auth_gql(
        query_category_answers(category), cookies=cookies, headers=headers
    )
    return tdjson.get("data") or {}


def generate_followups(
    category: str, cookies: Dict[str, str] = {}, headers: Dict[str, str] = {}
) -> List[FollowupQuestion]:
    data = fetch_category(category, cookies=cookies, headers=headers)
    me = data.get("me")
    if me is None:
        raise NameError("me not found")
    category_answer = me.get("categoryAnswers", [])
    recorded = [
        AnswerInfo(
            answer_text=answer_data.get("answerText") or "",
            question_text=answer_data.get("questionText") or "",
        )
        for answer_data in category_answer
        ]
    followups = NamedEntities(recorded).generate_questions()
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
