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

from mentor_classifier.lr.train import train
from .helpers import fixture_path


@pytest.fixture(scope="module")
def data_root() -> str:
    return fixture_path("data_out")


@pytest.fixture(scope="module")
def shared_root(word2vec) -> str:
    return path.dirname(word2vec)


@responses.activate
@pytest.mark.parametrize("mentor_id", [("clint")])
def test_trains_and_outputs_models(
    tmpdir, data_root: str, shared_root: str, mentor_id: str
):
    with open(fixture_path("graphql/{}.json".format(mentor_id))) as f:
        data = json.load(f)
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    scores, accuracy, model_path = train(mentor_id, shared_root, data_root)
    assert model_path == path.join(data_root, mentor_id)
    assert path.exists(path.join(model_path, "model.pkl"))
    assert path.exists(path.join(model_path, "w2v.txt"))
