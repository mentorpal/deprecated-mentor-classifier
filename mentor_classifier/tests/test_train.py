#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import path

import json
import pytest
import responses
from responses import matchers

from mentor_classifier import ClassifierFactory, ARCH_DEFAULT
from .helpers import fixture_path

from mentor_classifier.api import GQL_UPDATE_MENTOR_TRAINING, GQL_QUERY_MENTOR


@pytest.fixture(scope="module")
def data_root() -> str:
    return fixture_path("data_out")


@responses.activate
@pytest.mark.parametrize("mentor_id", [("clint")])
def test_trains_and_outputs_models(data_root: str, shared_root: str, mentor_id: str):
    update_mentor_response = {"data": {"updateMentorTraining": {"_id": mentor_id}}}
    with open(fixture_path("graphql/{}.json".format(mentor_id))) as f:
        query_mentor_response = json.load(f)
    responses.add(
        responses.POST,
        "http://graphql/graphql",
        json=query_mentor_response,
        status=200,
        match=[
            matchers.json_params_matcher(
                {"query": GQL_QUERY_MENTOR, "variables": {"id": mentor_id}}
            )
        ],
    )
    responses.add(
        responses.POST,
        "http://graphql/graphql",
        json=update_mentor_response,
        status=200,
        match=[
            matchers.json_params_matcher(
                {"query": GQL_UPDATE_MENTOR_TRAINING, "variables": {"id": mentor_id}}
            )
        ],
    )
    result = (
        ClassifierFactory()
        .new_training(mentor_id, shared_root, data_root)
        .train(shared_root)
    )
    assert result.model_path == path.join(data_root, mentor_id, ARCH_DEFAULT)
    assert path.exists(path.join(result.model_path, "model.pkl"))
    assert path.exists(path.join(result.model_path, "w2v.txt"))
