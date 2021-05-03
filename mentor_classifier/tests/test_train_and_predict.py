#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import path
from typing import List

import pytest
import responses

from mentor_classifier import ClassifierFactory
from .helpers import fixture_path, load_mentor_csv


@pytest.fixture(scope="module")
def data_root() -> str:
    return fixture_path("data_out")


@pytest.fixture(scope="module")
def shared_root(word2vec) -> str:
    return path.dirname(word2vec)


@responses.activate
@pytest.mark.parametrize(
    "mentor_id,expected_training_accuracy,sample_questions,expected_sample_answers",
    [
        (
            "clint",
            0.5,
            [
                "What's your name?",
                "Who are you?",
                "Give me your name.",
                "Give me your age.",
                "what do the penguins do?",
            ],
            [
                "Clint Anderson",
                "Clint Anderson",
                "Clint Anderson",
                "37 years old",
                "Penguins do important things",
            ],
        )
    ],
)
def test_train_and_predict(
    mentor_id: str,
    expected_training_accuracy: float,
    sample_questions: List[str],
    expected_sample_answers: List[str],
    tmpdir,
    shared_root: str,
):
    mentor = load_mentor_csv(fixture_path("csv/{}.csv".format(mentor_id)))
    data = {"data": {"mentor": mentor.to_dict()}}
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    result = (
        ClassifierFactory()
        .new_training(mentor=mentor_id, shared_root=shared_root, data_path=tmpdir)
        .train()
    )
    assert result.accuracy == expected_training_accuracy

    classifier = ClassifierFactory().new_prediction(
        mentor=mentor_id, shared_root=shared_root, data_path=tmpdir
    )

    for sample_question, expected_sample_answer in zip(
        sample_questions, expected_sample_answers
    ):
        prediction_result = classifier.evaluate(sample_question)
        assert expected_sample_answer == prediction_result.answer_text
