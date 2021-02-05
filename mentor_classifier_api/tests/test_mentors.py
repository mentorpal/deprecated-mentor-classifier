#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
import os

import pytest
import responses

from . import fixture_path


@responses.activate
@pytest.mark.parametrize(
    "input_mentor,expected_results",
    [
        (
            "clint",
            {
                "id": "clint",
                "name": "Clint Anderson",
                "short_name": "Clint",
                "title": "Nuclear Electrician's Mate",
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
                "questions_by_id": {
                    "Q1": {
                        "id": "Q1",
                        "question_text": "What is your name?",
                        "answer": "Clint Anderson",
                        "video": "https://video.mentorpal.org/videos/mentors/clint/Q1.mp4",
                        "topics": ["Background", "About Me"],
                    },
                    "Q2": {
                        "id": "Q2",
                        "question_text": "How old are you?",
                        "answer": "37 years old",
                        "video": "https://video.mentorpal.org/videos/mentors/clint/Q2.mp4",
                        "topics": ["Advice"],
                    },
                },
                "utterances_by_type": {
                    "_IDLE_": [["idle", ""]],
                    "_INTRO_": [["intro", "hi there!"]],
                    "_OFF_TOPIC_": [["off_topic", "I don't know"]],
                    "_PROMPT_": [["prompt", "ask me about my job"]],
                    "_FEEDBACK_": [["feedback", "no"]],
                    "_REPEAT_": [["repeat", "you already asked that!"]],
                    "_REPEAT_BUMP_": [
                        ["repeat_bump", "you asked that, how about this?"]
                    ],
                    "_PROFANITY_": [["profanity", "watch your mouth!"]],
                },
            },
        )
    ],
)
def test_get_mentor_data(
    client,
    input_mentor,
    expected_results,
):
    with open(fixture_path("graphql/{}.json".format(input_mentor))) as f:
        data = json.load(f)
    responses.add(
        responses.POST,
        "http://graphql/graphql",
        json=data,
        status=200,
    )
    res = client.get(f"/classifier/mentors/{input_mentor}/data")
    assert res.json["id"] == expected_results["id"]
    assert res.json["name"] == expected_results["name"]
    assert res.json["short_name"] == expected_results["short_name"]
    assert res.json["title"] == expected_results["title"]
    assert res.json["topics_by_id"] == expected_results["topics_by_id"]
    assert res.json["questions_by_id"] == expected_results["questions_by_id"]
    assert res.json["utterances_by_type"] == expected_results["utterances_by_type"]
