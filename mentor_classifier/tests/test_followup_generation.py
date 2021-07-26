#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from mentor_classifier.types import Answer, AnswerInfo

import pytest
import responses

from .helpers import (
    fixture_mentor_data,
    load_mentor_csv,
)
from mentor_classifier.ner import NamedEntities
from .helpers import get_answers
from typing import List, Dict


@responses.activate
@pytest.mark.parametrize(
    "mentor_id, expected_answer",
    [("clint", {"people": ["Clint Anderson"], "places": [], "acronyms": []})],
)
def test_recognizes_named_entities(
    mentor_id: str,
    expected_answer: Dict[str, List[str]],
    shared_root: str,
):
    mentor = load_mentor_csv(fixture_mentor_data(mentor_id, "data.csv"))
    answers: List[Answer] = get_answers(mentor)
    answer_info: List[AnswerInfo] = [
        AnswerInfo(
            question_text=answer.question.question, answer_text=answer.transcript
        )
        for answer in answers
    ]
    ents = NamedEntities(answer_info, shared_root)
    assert NamedEntities.to_dict(ents) == expected_answer


@responses.activate
@pytest.mark.parametrize(
    "mentor_id, expected_question",
    [("clint", "Can you tell me more about Clint Anderson?")],
)
def test_generates_followups(
    mentor_id: str,
    expected_question: str,
    shared_root: str,
):
    mentor = load_mentor_csv(fixture_mentor_data(mentor_id, "data.csv"))
    answers = get_answers(mentor)
    answer_info_list: List[AnswerInfo] = [
        AnswerInfo(
            question_text=answer.question.question, answer_text=answer.transcript
        )
        for answer in answers
    ]
    ents = NamedEntities(answer_info_list, shared_root)
    questions = ents.generate_questions(answer_info_list, answer_info_list)
    actual_question = questions[0].question
    assert actual_question == expected_question


@responses.activate
@pytest.mark.parametrize(
    "question, answer, expected_followup",
    [
        ("Where did you live?", "I lived in the U.K.", "What was U.K. like?"),
        (
            "Who is your brother?",
            "He is Clint Anderson",
            "Can you tell me more about Clint Anderson?",
        ),
        ("Where do you work?", "I work at USC", "What is USC?"),
    ],
)
def test_covers_all_entities(
    question: str,
    answer: str,
    expected_followup: str,
    shared_root: str,
):
    answer_info = AnswerInfo(question_text=question, answer_text=answer)
    answer_info_list = [answer_info]
    ents = NamedEntities(answer_info_list, shared_root)
    questions = ents.generate_questions(answer_info_list, answer_info_list)
    actual_question = questions[0].question
    assert actual_question == expected_followup


@responses.activate
@pytest.mark.parametrize(
    "questions, answers, expected_followups",
    [
        (
            [
                "Where did you live?",
                "Who is your brother?",
                "Where do you work?",
                "What was U.K. like?",
            ],
            [
                "I lived in the U.K.",
                "He is Clint Anderson.",
                "I work at USC.",
                "The U.K. was cool.",
            ],
            ["What is USC?", "Can you tell me more about Clint Anderson?"],
        )
    ],
)
def test_deduplication(
    questions: List[str],
    answers: List[str],
    expected_followups: List[str],
    shared_root: str,
):
    answer_info_list = [
        AnswerInfo(questions[x], answers[x]) for x in range(len(questions))
    ]
    ents = NamedEntities(answer_info_list, shared_root)
    followups = ents.generate_questions(answer_info_list, answer_info_list)
    question_text = [followup.question for followup in followups]
    assert question_text == expected_followups
