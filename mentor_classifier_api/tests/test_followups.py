#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import path
import pytest
import responses
import json


from . import fixture_path


@pytest.fixture(autouse=True)
def python_path_env(monkeypatch, shared_root):
    monkeypatch.setenv("MODEL_ROOT", fixture_path("models"))
    monkeypatch.setenv("SHARED_ROOT", shared_root)


@responses.activate
@pytest.mark.parametrize(
    "category, mentor, expected_results",
    [
        (
            "About me",
            "mentor_1",
            {
                "entityType": "the USC Archery Club",
                "question": "What is the USC Archery Club?",
                "template": "acronym",
            },
        )
    ],
)
def test_followup(client, category, mentor, expected_results):
    with open(fixture_path(path.join("graphql", "category_answers.json"))) as f:
        data = json.load(f)
        responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    with open(fixture_path(path.join("graphql", "mentor_answers.json"))) as f:
        data = json.load(f)
        responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    res = client.post(f"/classifier/followups/category/{category}/{mentor}")
    data = res.json["data"]
    assert data["followups"][0] == expected_results
