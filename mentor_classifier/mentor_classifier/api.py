#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
import os
import requests

from typing import TypedDict


class GQLQueryBody(TypedDict):
    query: str
    variables: dict


GRAPHQL_ENDPOINT = os.environ.get("GRAPHQL_ENDPOINT") or "http://graphql/graphql"
OFF_TOPIC_THRESHOLD = -0.55  # todo: put this in graphql and have it be configurable
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


def __auth_gql(query: GQLQueryBody) -> dict:
    res = requests.post(
        GRAPHQL_ENDPOINT,
        json=query,
    )
    res.raise_for_status()
    return res.json()


def query_mentor(mentor: str) -> GQLQueryBody:
    return {"query": GQL_QUERY_MENTOR, "variables": {"id": mentor}}


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
                "confidence": confidence,
            }
        },
    }


def fetch_mentor_data(mentor: str) -> dict:
    tdjson = __auth_gql(query_mentor(mentor))
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))
    data = tdjson["data"]["mentor"]
    return data


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
