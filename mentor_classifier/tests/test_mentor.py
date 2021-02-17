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
from .helpers import (
    fixture_path,
)


@responses.activate
@pytest.mark.parametrize(
    "mentor_id,expected_data",
    [
        (
            "clint",
            {
                "id": "clint",
                "name": "Clint Anderson",
                "short_name": "Clint",
                "title": "Nuclear Electrician's Mate",
                "topics": ["Background", "About Me", "Advice", "Weird", "Utterances"],
                "subjects_by_id": {
                    "background": {
                        "name": "Background",
                        "questions": ["Q1"],
                        "topics": ["about_me"],
                    },
                    "advice": {
                        "name": "Advice",
                        "questions": ["Q2"],
                        "topics": ["weird"],
                    },
                    "utterances": {
                        "name": "Utterances",
                        "questions": ["Q4", "Q5", "Q6"],
                        "topics": [],
                    },
                },
                "topics_by_id": {
                    "about_me": {
                        "name": "About Me",
                        "questions": ["Q1"],
                    },
                    "weird": {
                        "name": "Weird",
                        "questions": [],
                    },
                },
                "utterances_by_type": {
                    "_IDLE_": [["Q4", None]],
                    "_INTRO_": [["Q5", "Hi I'm Clint"]],
                    "_OFF_TOPIC_": [["Q6", "Ask me something else"]],
                    "_PROMPT_": [],
                    "_FEEDBACK_": [],
                    "_REPEAT_": [],
                    "_REPEAT_BUMP_": [],
                    "_PROFANITY_": [],
                },
                "questions_by_id": {
                    "Q1": {
                        "id": "Q1",
                        "question_text": "What is your name?",
                        "answer": "Clint Anderson",
                        "video": "https://video.mentorpal.org/videos/mentors/clint/Q1.mp4",
                        "topics": ["Background", "About Me"],
                        "paraphrases": ["Who are you?"],
                    },
                    "Q2": {
                        "id": "Q2",
                        "question_text": "How old are you?",
                        "answer": "37 years old",
                        "video": "https://video.mentorpal.org/videos/mentors/clint/Q2.mp4",
                        "topics": ["Advice"],
                        "paraphrases": ["What's your age?"],
                    },
                },
                "questions_by_text": {
                    "what is your name": {
                        "id": "Q1",
                        "question_text": "What is your name?",
                        "answer": "Clint Anderson",
                        "video": "https://video.mentorpal.org/videos/mentors/clint/Q1.mp4",
                        "topics": ["Background", "About Me"],
                        "paraphrases": ["Who are you?"],
                    },
                    "who are you": {
                        "id": "Q1",
                        "question_text": "What is your name?",
                        "answer": "Clint Anderson",
                        "video": "https://video.mentorpal.org/videos/mentors/clint/Q1.mp4",
                        "topics": ["Background", "About Me"],
                        "paraphrases": ["Who are you?"],
                    },
                    "how old are you": {
                        "id": "Q2",
                        "question_text": "How old are you?",
                        "answer": "37 years old",
                        "video": "https://video.mentorpal.org/videos/mentors/clint/Q2.mp4",
                        "topics": ["Advice"],
                        "paraphrases": ["What's your age?"],
                    },
                    "whats your age": {
                        "id": "Q2",
                        "question_text": "How old are you?",
                        "answer": "37 years old",
                        "video": "https://video.mentorpal.org/videos/mentors/clint/Q2.mp4",
                        "topics": ["Advice"],
                        "paraphrases": ["What's your age?"],
                    },
                },
                "questions_by_answer": {
                    "clint anderson": {
                        "id": "Q1",
                        "question_text": "What is your name?",
                        "answer": "Clint Anderson",
                        "video": "https://video.mentorpal.org/videos/mentors/clint/Q1.mp4",
                        "topics": ["Background", "About Me"],
                        "paraphrases": ["Who are you?"],
                    },
                    "37 years old": {
                        "id": "Q2",
                        "question_text": "How old are you?",
                        "answer": "37 years old",
                        "video": "https://video.mentorpal.org/videos/mentors/clint/Q2.mp4",
                        "topics": ["Advice"],
                        "paraphrases": ["What's your age?"],
                    },
                },
            },
        )
    ],
)
def test_loads_mentor_from_api(mentor_id, expected_data):
    with open(fixture_path("graphql/{}.json".format(mentor_id))) as f:
        data = json.load(f)
    responses.add(
        responses.POST,
        "http://graphql/graphql",
        json=data,
        status=200,
    )
    m = Mentor(mentor_id)
    assert m.id == expected_data["id"]
    assert m.name == expected_data["name"]
    assert m.short_name == expected_data["short_name"]
    assert m.title == expected_data["title"]
    assert m.topics == expected_data["topics"]
    assert m.subjects_by_id == expected_data["subjects_by_id"]
    assert m.topics_by_id == expected_data["topics_by_id"]
    assert m.utterances_by_type == expected_data["utterances_by_type"]
    assert m.questions_by_id == expected_data["questions_by_id"]
    assert m.questions_by_text == expected_data["questions_by_text"]
    assert m.questions_by_answer == expected_data["questions_by_answer"]
