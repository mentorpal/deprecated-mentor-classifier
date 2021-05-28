#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import path
from typing import List

import json
import pytest
import responses

from mentor_classifier.mentor import Media
from mentor_classifier.api import OFF_TOPIC_THRESHOLD
from mentor_classifier import ClassifierFactory
from .helpers import fixture_path


@pytest.fixture(scope="module")
def data_root() -> str:
    return fixture_path("data")


@pytest.fixture(scope="module")
def shared_root(word2vec) -> str:
    return path.dirname(word2vec)


@responses.activate
@pytest.mark.parametrize(
    "mentor_id,question,expected_answer_id,expected_answer,expected_media",
    [
        (
            "clint",
            "What is your name?",
            "A1",
            "Clint Anderson",
            [
                {"type": "video", "tag": "web", "url": "q1_web.mp4"},
                {"type": "video", "tag": "mobile", "url": "q1_mobile.mp4"},
            ],
        ),
        ("clint", "How old are you?", "A2", "37 years old", []),
        (
            "clint",
            "Who are you?",
            "A1",
            "Clint Anderson",
            [
                {"type": "video", "tag": "web", "url": "q1_web.mp4"},
                {"type": "video", "tag": "mobile", "url": "q1_mobile.mp4"},
            ],
        ),
        ("clint", "What's your age?", "A2", "37 years old", []),
    ],
)
def test_gets_answer_for_exact_match_and_paraphrases(
    tmpdir,
    data_root: str,
    shared_root: str,
    mentor_id: str,
    question: str,
    expected_answer_id: str,
    expected_answer: str,
    expected_media: List[Media],
):
    with open(fixture_path("graphql/{}.json".format(mentor_id))) as f:
        data = json.load(f)
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    if not path.exists(path.join(data_root, mentor_id)):
        training = ClassifierFactory().new_training(mentor_id, shared_root, data_root)
        training.train()
    classifier = ClassifierFactory().new_prediction(mentor_id, shared_root, data_root)
    result = classifier.evaluate(question)
    assert result.answer_id == expected_answer_id
    assert result.answer_text == expected_answer
    assert result.answer_media == expected_media
    assert result.highest_confidence == 1
    assert result.feedback_id is not None


@responses.activate
@pytest.mark.parametrize(
    "mentor_id,question,expected_answer_id,expected_answer,expected_media",
    [
        (
            "clint",
            "What's your name?",
            "A1",
            "Clint Anderson",
            [
                {"type": "video", "tag": "web", "url": "q1_web.mp4"},
                {"type": "video", "tag": "mobile", "url": "q1_mobile.mp4"},
            ],
        ),
        (
            "clint",
            "Tell me your name",
            "A1",
            "Clint Anderson",
            [
                {"type": "video", "tag": "web", "url": "q1_web.mp4"},
                {"type": "video", "tag": "mobile", "url": "q1_mobile.mp4"},
            ],
        ),
    ],
)
def test_predicts_answer(
    tmpdir,
    data_root: str,
    shared_root: str,
    mentor_id: str,
    question: str,
    expected_answer_id: str,
    expected_answer: str,
    expected_media: List[Media],
):
    with open(fixture_path("graphql/{}.json".format(mentor_id))) as f:
        data = json.load(f)
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    if not path.exists(path.join(data_root, mentor_id)):
        training = ClassifierFactory().new_training(mentor_id, shared_root, data_root)
        training.train()
    classifier = ClassifierFactory().new_prediction(mentor_id, shared_root, data_root)
    result = classifier.evaluate(question)
    assert result.answer_id == expected_answer_id
    assert result.answer_text == expected_answer
    assert result.answer_media == expected_media
    assert result.highest_confidence != 1
    assert result.feedback_id is not None


@responses.activate
@pytest.mark.xfail
@pytest.mark.parametrize(
    "mentor_id,question,expected_answer_id,expected_answer,expected_media",
    [
        (
            "clint",
            "According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.",
            "A6",
            "Ask me something else",
            [],
        ),
    ],
)
def test_gets_off_topic(
    tmpdir,
    data_root: str,
    shared_root: str,
    mentor_id: str,
    question: str,
    expected_answer_id: str,
    expected_answer: str,
    expected_media: List[Media],
):
    with open(fixture_path("graphql/{}.json".format(mentor_id))) as f:
        data = json.load(f)
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    if not path.exists(path.join(data_root, mentor_id)):
        training = ClassifierFactory().new_training(mentor_id, shared_root, data_root)
        training.train()
    classifier = ClassifierFactory().new_prediction(mentor_id, shared_root, data_root)
    result = classifier.evaluate(question)
    assert result.highest_confidence < OFF_TOPIC_THRESHOLD
    assert result.answer_id == expected_answer_id
    assert result.answer_text == expected_answer
    assert result.answer_media == expected_media
    assert result.feedback_id is not None
