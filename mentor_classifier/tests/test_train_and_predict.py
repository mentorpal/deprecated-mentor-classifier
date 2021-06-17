#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import path

import pytest
import logging
import responses

from mentor_classifier import ClassifierFactory, ARCH_LR, ARCH_TRANSFORMERS
from .helpers import (
    fixture_mentor_data,
    fixture_path,
    load_mentor_csv,
    load_test_csv,
    run_model_against_testset,
)
from .types import _MentorTrainAndTestConfiguration


@pytest.fixture(scope="module")
def data_root() -> str:
    return fixture_path("data_out")


@pytest.fixture(scope="module")
def shared_root(word2vec) -> str:
    return path.dirname(word2vec)


@responses.activate
@pytest.mark.parametrize(
    "training_configuration",
    [
        _MentorTrainAndTestConfiguration(
            mentor_id="clint", arch=ARCH_LR, expected_training_accuracy=0.5
        )
    ],
)
def test_train_and_predict(
    training_configuration: _MentorTrainAndTestConfiguration,
    tmpdir,
    shared_root: str,
):
    mentor = load_mentor_csv(
        fixture_mentor_data(training_configuration.mentor_id, "data.csv")
    )
    test_set = load_test_csv(
        fixture_mentor_data(training_configuration.mentor_id, "test.csv")
    )
    data = {"data": {"mentor": mentor.to_dict()}}
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    result = (
        ClassifierFactory()
        .new_training(
            mentor=training_configuration.mentor_id,
            shared_root=shared_root,
            data_path=tmpdir,
            arch=training_configuration.arch,
        )
        .train()
    )
    assert result.accuracy == training_configuration.expected_training_accuracy

    classifier = ClassifierFactory().new_prediction(
        mentor=training_configuration.mentor_id,
        shared_root=shared_root,
        data_path=tmpdir,
        arch=training_configuration.arch,
    )

    test_results = run_model_against_testset(classifier, test_set)

    logging.warning(test_results.errors)
    logging.warning(
        f"percentage passed = {test_results.passing_tests}/{len(test_results.results)}"
    )
    assert len(test_results.errors) == 0


@responses.activate
@pytest.mark.parametrize(
    "training_configuration",
    [
        _MentorTrainAndTestConfiguration(
            mentor_id="clint", arch=ARCH_TRANSFORMERS, expected_training_accuracy=0.5
        )
    ],
)
def test_train_and_predict_transformers(
    training_configuration: _MentorTrainAndTestConfiguration,
    tmpdir,
    shared_root: str,
):
    mentor = load_mentor_csv(
        fixture_mentor_data(training_configuration.mentor_id, "data.csv")
    )
    test_set = load_test_csv(
        fixture_mentor_data(training_configuration.mentor_id, "test.csv")
    )
    data = {"data": {"mentor": mentor.to_dict()}}
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    result = (
        ClassifierFactory()
        .new_training(
            mentor=training_configuration.mentor_id,
            shared_root=shared_root,
            data_path=tmpdir,
            arch=training_configuration.arch,
        )
        .train()
    )
    assert result.accuracy >= training_configuration.expected_training_accuracy

    classifier = ClassifierFactory().new_prediction(
        mentor=training_configuration.mentor_id,
        shared_root=shared_root,
        data_path=tmpdir,
        arch=training_configuration.arch,
    )

    test_results = run_model_against_testset(classifier, test_set)

    logging.warning(test_results.errors)
    logging.warning(
        f"percentage passed = {test_results.passing_tests}/{len(test_results.results)}"
    )
    assert len(test_results.errors) == 0


@pytest.mark.only
@responses.activate
@pytest.mark.parametrize(
    "training_configuration,compare_configuration,example",
    [
        (
        _MentorTrainAndTestConfiguration(
            mentor_id="clint", arch=ARCH_LR, expected_training_accuracy=1
        ),
        _MentorTrainAndTestConfiguration(
            mentor_id="clint", arch=ARCH_TRANSFORMERS, expected_training_accuracy=1
        ),
         "who you is?",
        )
    ],
)

def test_confidence(
    training_configuration: _MentorTrainAndTestConfiguration,
    compare_configuration: _MentorTrainAndTestConfiguration,
    tmpdir,
    shared_root: str,
    example: str
):
    mentor = load_mentor_csv(
        fixture_mentor_data(training_configuration.mentor_id, "data.csv")
    )
    data = {"data": {"mentor": mentor.to_dict()}}
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    lr_result = (
        ClassifierFactory()
        .new_training(
            mentor=training_configuration.mentor_id,
            shared_root=shared_root,
            data_path=tmpdir,
            arch=training_configuration.arch,
        )
        .train()
    )
    hf_result = (
        ClassifierFactory()
        .new_training(
            mentor=compare_configuration.mentor_id,
            shared_root=shared_root,
            data_path=tmpdir,
            arch=compare_configuration.arch,
        )
        .train()
    )
    hf_classifier = ClassifierFactory().new_prediction(
        mentor=compare_configuration.mentor_id,
        shared_root=shared_root,
        data_path=tmpdir,
        arch=compare_configuration.arch,
    )
    lr_classifier = ClassifierFactory().new_prediction(
        mentor=training_configuration.mentor_id,
        shared_root=shared_root,
        data_path=tmpdir,
        arch=training_configuration.arch,
    )
    hf_result = hf_classifier.evaluate(example)
    lr_result = lr_classifier.evaluate(example)
    assert hf_result.highest_confidence >= lr_result.highest_confidence
