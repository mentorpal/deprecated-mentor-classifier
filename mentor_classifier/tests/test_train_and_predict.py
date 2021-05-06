#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import path

import pytest
import responses

from mentor_classifier import ClassifierFactory, ARCH_LR
from .helpers import (
    fixture_path,
    load_mentor_csv,
    load_test_csv,
    run_model_against_testset,
)


@pytest.fixture(scope="module")
def data_root() -> str:
    return fixture_path("data_out")


@pytest.fixture(scope="module")
def shared_root(word2vec) -> str:
    return path.dirname(word2vec)


@responses.activate
@pytest.mark.parametrize(
    "mentor_id,arch,expected_training_accuracy",
    [
        (
            "clint",
            ARCH_LR,
            0.5,
        )
    ],
)
def test_train_and_predict(
    mentor_id: str,
    arch: str,
    expected_training_accuracy: float,
    tmpdir,
    shared_root: str,
):
    mentor = load_mentor_csv(fixture_path("csv/{}/{}.csv".format(mentor_id, mentor_id)))
    test_set = load_test_csv(fixture_path(f"csv/{mentor_id}/test.csv"))
    data = {"data": {"mentor": mentor.to_dict()}}
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    result = (
        ClassifierFactory()
        .new_training(
            mentor=mentor_id, shared_root=shared_root, data_path=tmpdir, arch=arch
        )
        .train()
    )
    assert result.accuracy == expected_training_accuracy

    classifier = ClassifierFactory().new_prediction(
        mentor=mentor_id, shared_root=shared_root, data_path=tmpdir, arch=arch
    )

    test_results = run_model_against_testset(classifier, test_set)

    print(test_results.errors)
    print(
        f"percentage passed = {test_results.passing_tests}/{len(test_results.results)}"
    )
    assert len(test_results.errors) == 0
