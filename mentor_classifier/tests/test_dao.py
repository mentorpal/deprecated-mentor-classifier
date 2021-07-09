#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
from os import path
from shutil import copytree

import responses
import pytest

from mentor_classifier.dao import Dao
from mentor_classifier import ClassifierFactory
from .helpers import fixture_path


@pytest.fixture(scope="module")
def data_root() -> str:
    return fixture_path("data")


@responses.activate
@pytest.mark.parametrize("mentor_id", [("clint")])
def test_find_classifier_caches(data_root: str, shared_root: str, mentor_id: str):
    with open(fixture_path("graphql/{}.json".format(mentor_id))) as f:
        data = json.load(f)
        responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    dao = Dao(shared_root=shared_root, data_root=data_root)
    c1 = dao.find_classifier(mentor_id)
    c2 = dao.find_classifier(mentor_id)
    assert c1 == c2


@responses.activate
@pytest.mark.parametrize("mentor_id", [("clint")])
def test_find_classifier_returns_updated_classifier_if_model_has_changed(
    tmp_path, data_root: str, shared_root: str, mentor_id: str
):
    with open(fixture_path("graphql/{}.json".format(mentor_id))) as f:
        data = json.load(f)
        responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    test_data_root = tmp_path / "data"
    copytree(path.join(data_root, mentor_id), path.join(test_data_root, mentor_id))
    dao = Dao(shared_root=shared_root, data_root=test_data_root)
    c1 = dao.find_classifier(mentor_id)
    ClassifierFactory().new_training(
        mentor=mentor_id, shared_root=shared_root, data_path=test_data_root
    ).train(shared_root)
    c2 = dao.find_classifier(mentor_id)
    assert c1 != c2
