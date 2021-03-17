#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
import os
import requests


GRAPHQL_ENDPOINT = os.environ.get("GRAPHQL_ENDPOINT") or "http://graphql/graphql"
OFF_TOPIC_THRESHOLD = -0.55  # todo: put this in graphql and have it be configurable


def fetch_mentor_data(mentor: str) -> dict:
    res = requests.post(
        GRAPHQL_ENDPOINT,
        json={
            "query": f"""query {{
                mentor(id: "{mentor}") {{
                    answers {{
                        _id
                        status
                        transcript
                        subjects {{
                            name
                        }}
                        topics {{
                            name
                        }}
                        question {{
                            _id
                            question
                            type
                            name
                            paraphrases
                            topics {{
                                name
                            }}
                        }}
                    }}
                }}
            }}"""
        },
    )
    res.raise_for_status()
    tdjson = res.json()
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))
    data = tdjson["data"]["mentor"]
    return data


def update_training(mentor: str):
    res = requests.post(
        GRAPHQL_ENDPOINT,
        json={
            "query": f"""mutation {{
                updateMentorTraining(id: "{mentor}") {{
                    _id
                }}
            }}"""
        },
    )
    res.raise_for_status()


def create_user_question(
    mentor: str,
    question: str,
    answer_id: str,
    answer_type: str,
    confidence: float,
) -> str:
    res = requests.post(
        GRAPHQL_ENDPOINT,
        json={
            "query": f"""mutation {{
                userQuestionCreate(userQuestion: {{
                    mentor: "{mentor}",
                    question: "{question}",
                    classifierAnswer: "{answer_id}",
                    classifierAnswerType: "{answer_type}",
                    confidence: {confidence}
                }}) {{
                    _id
                }}
            }}"""
        },
    )
    res.raise_for_status()
    tdjson = res.json()
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))
    # TODO: should throw an error but need to figure out how to mock 2 different GQL queries...
    try:
        return tdjson["data"]["userQuestionCreate"]["_id"]
    except KeyError:
        return "error"
