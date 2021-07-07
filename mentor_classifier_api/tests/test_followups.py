# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from io import StringIO
from flask import jsonify
from typing import Union, List
import pytest
import responses

from . import fixture_path


@pytest.fixture(autouse=True)
def python_path_env(monkeypatch, shared_root):
    monkeypatch.setenv("MODEL_ROOT", fixture_path("models"))
    monkeypatch.setenv("SHARED_ROOT", shared_root)

@responses.activate
@pytest.mark.parametrize(
    "input_mentor, category",
    [("clint", 
    "About me")],
)
def test_fetch_data(
    client,
    input_mentor,
    category
):
    res = client.get(f"/classifier/followups/{input_mentor}/{category}")
    expected_data = jsonify(
        {
            "errors": {},
            "data": {
                "followups": [
                    {
                        "question": "what is it like being a nurse?",
                        # this shape allows us to extend the metadata for each question in the future, e.g.
                        "entityType": "profession",
                        "template": "what is it like being a <entity:profession>?",
                    },
                    {
                        "question": "when did you decide to become a nurse?",
                    },
                ]
            },
        }
    )
    actual_data = res.data.decode("utf-8")
    assert actual_data == expected_data.data.decode("utf-8")