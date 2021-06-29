#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
import responses
import pytest

from mentor_classifier.mentor import Mentor
from .helpers import fixture_path

@responses.activate
@pytest.mark.parametrize(
    "mentor_id,expected_data",
    [
        (
            "clint",
            {
                "topics": ["Advice", "Background", "Utterances", "About Me", "Weird"],
                "utterances_by_type": {
                    "_IDLE_": [
                        [
                            "A4",
                            None,
                            [
                                {"type": "video", "tag": "web", "url": "idle_web.mp4"},
                                {
                                    "type": "video",
                                    "tag": "mobile",
                                    "url": "idle_mobile.mp4",
                                },
                            ],
                        ]
                    ],
                    "_INTRO_": [["A5", "Hi I'm Clint", []]],
                    "_OFF_TOPIC_": [["A6", "Ask me something else", []]],
                },
                "questions_by_id": {
                    "Q1": {
                        "id": "Q1",
                        "question_text": "What is your name?",
                        "answer": "Clint Anderson",
                        "answer_id": "A1",
                        "topics": ["About Me"],
                        "paraphrases": ["Who are you?"],
                        "media": [
                            {"type": "video", "tag": "web", "url": "q1_web.mp4"},
                            {"type": "video", "tag": "mobile", "url": "q1_mobile.mp4"},
                        ],
                    },
                    "Q2": {
                        "id": "Q2",
                        "question_text": "How old are you?",
                        "answer": "37 years old",
                        "answer_id": "A2",
                        "topics": [],
                        "paraphrases": ["What's your age?"],
                        "media": [],
                    },
                },
                "questions_by_text": {
                    "what is your name": {
                        "id": "Q1",
                        "question_text": "What is your name?",
                        "answer": "Clint Anderson",
                        "answer_id": "A1",
                        "topics": ["About Me"],
                        "paraphrases": ["Who are you?"],
                        "media": [
                            {"type": "video", "tag": "web", "url": "q1_web.mp4"},
                            {"type": "video", "tag": "mobile", "url": "q1_mobile.mp4"},
                        ],
                    },
                    "who are you": {
                        "id": "Q1",
                        "question_text": "What is your name?",
                        "answer": "Clint Anderson",
                        "answer_id": "A1",
                        "topics": ["About Me"],
                        "paraphrases": ["Who are you?"],
                        "media": [
                            {"type": "video", "tag": "web", "url": "q1_web.mp4"},
                            {"type": "video", "tag": "mobile", "url": "q1_mobile.mp4"},
                        ],
                    },
                    "how old are you": {
                        "id": "Q2",
                        "question_text": "How old are you?",
                        "answer": "37 years old",
                        "answer_id": "A2",
                        "topics": [],
                        "paraphrases": ["What's your age?"],
                        "media": [],
                    },
                    "whats your age": {
                        "id": "Q2",
                        "question_text": "How old are you?",
                        "answer": "37 years old",
                        "answer_id": "A2",
                        "topics": [],
                        "paraphrases": ["What's your age?"],
                        "media": [],
                    },
                },
                "questions_by_answer": {
                    "clint anderson": {
                        "id": "Q1",
                        "question_text": "What is your name?",
                        "answer": "Clint Anderson",
                        "answer_id": "A1",
                        "topics": ["About Me"],
                        "paraphrases": ["Who are you?"],
                        "media": [
                            {"type": "video", "tag": "web", "url": "q1_web.mp4"},
                            {"type": "video", "tag": "mobile", "url": "q1_mobile.mp4"},
                        ],
                    },
                    "37 years old": {
                        "id": "Q2",
                        "question_text": "How old are you?",
                        "answer": "37 years old",
                        "answer_id": "A2",
                        "topics": [],
                        "paraphrases": ["What's your age?"],
                        "media": [],
                    },
                },
            },
        )
    ],
)
def test_loads_mentor_from_api(mentor_id, expected_data):
    with open(fixture_path("graphql/{}.json".format(mentor_id))) as f:
        data = json.load(f)
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    m = Mentor(mentor_id)
    assert m.id == mentor_id
    assert m.topics == expected_data["topics"]
    assert m.utterances_by_type == expected_data["utterances_by_type"]
    assert m.questions_by_id == expected_data["questions_by_id"]
    assert m.questions_by_text == expected_data["questions_by_text"]
    assert m.questions_by_answer == expected_data["questions_by_answer"]
