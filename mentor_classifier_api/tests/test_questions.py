#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
import os

import pytest
import responses

from . import fixture_path


@pytest.fixture(scope="module")
def shared_root(word2vec) -> str:
    return os.path.dirname(word2vec)


@pytest.fixture(autouse=True)
def python_path_env(monkeypatch, shared_root):
    monkeypatch.setenv("MODEL_ROOT", fixture_path("models"))
    monkeypatch.setenv("SHARED_ROOT", shared_root)


def test_returns_400_response_when_mentor_not_set(client):
    res = client.get("/classifier/questions/?query=test")
    assert res.status_code == 400
    assert res.json == {"mentor": ["required field"]}


def test_returns_400_response_when_question_not_set(client):
    res = client.get("/classifier/questions/?mentor=test")
    assert res.status_code == 400
    assert res.json == {"query": ["required field"]}


@responses.activate
@pytest.mark.parametrize(
    "input_mentor,input_question,expected_results",
    [
        (
            "clint",
            "What is your name?",
            {
                "query": "What is your name?",
                "answer_id": "Q1",
                "answer_text": "Clint Anderson",
                "confidence": 1,
            },
        ),
        (
            "clint",
            "How old are you?",
            {
                "query": "How old are you?",
                "answer_id": "Q2",
                "answer_text": "37 years old",
                "confidence": 1,
            },
        ),
        (
            "clint",
            "What's your name?",
            {
                "query": "What's your name?",
                "answer_id": "Q1",
                "answer_text": "Clint Anderson",
                "confidence": 0.12711383125936865,
            },
        ),
        (
            "clint",
            "How many years old are you?",
            {
                "query": "How many years old are you?",
                "answer_id": "Q2",
                "answer_text": "37 years old",
                "confidence": -0.42817784731913755,
            },
        ),
    ],
)
def test_evaluate_classifies_user_questions(
    client, input_mentor, input_question, expected_results
):
    with open(fixture_path("graphql/{}.json".format(input_mentor))) as f:
        data = json.load(f)
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    res = client.get(
        f"/classifier/questions/?mentor={input_mentor}&query={input_question}"
    )
    assert res.json["query"] == expected_results["query"]
    assert res.json["answer_id"] == expected_results["answer_id"]
    assert res.json["answer_text"] == expected_results["answer_text"]
    assert res.json["confidence"] == expected_results["confidence"]
