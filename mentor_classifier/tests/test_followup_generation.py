#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from mentor_classifier.types import AnswerInfo

import pytest
import responses

from .helpers import (
    fixture_mentor_data,
)
from mentor_classifier.ner import NamedEntities
from typing import List
import csv


@responses.activate
@pytest.mark.parametrize(
    "question, answer, expected_followup",
    [
        ("Where did you live?", "I lived in the U.K.", "What was U.K. like?"),
        (
            "Who is your brother?",
            "He is Ben",
            "Can you tell me more about Ben?",
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
    ents = NamedEntities(answer_info_list, "Clint Anderson", shared_root)
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
                "Where did you go to school?",
                "What is that?",
            ],
            [
                "I lived in the U.K.",
                "He is Clint Anderson.",
                "I work at USC.",
                "The U.K. was cool.",
                "I went to UC Berkeley",
                "I went to University of California Berkeley",
            ],
            [
                "What is USC?",
                "What is University of California Berkeley?",
                "Can you tell me more about Clint Anderson?",
            ],
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
    ents = NamedEntities(answer_info_list, "Clint Anderson", shared_root)
    followups = ents.generate_questions(answer_info_list, answer_info_list)
    question_text = [followup.question for followup in followups]
    assert question_text == expected_followups


def load_scored(mentor, category):
    data = fixture_mentor_data(mentor, category + "_scored.csv")
    good = set()
    bad = set()
    with open(data) as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for row in csv_reader:
            if row[3] == "1":
                good.add(row[0])
            else:
                bad.add(row[0])
    return good, bad


def k_precision(category, mentor, file_name, good, bad, k):
    import logging
    data = fixture_mentor_data(mentor, file_name)
    logging.warning(data)
    pos = 0
    neg = 0
    with open(data) as f:
        i = 0
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if i < k:
                if row[0] in good:
                    pos = pos + 1
                i = i + 1
            else:
                if row[0] in good:
                    neg = neg + 1
        precision = pos / k
    return precision


# test for comparing lists sorted with different algorithms
@responses.activate
@pytest.mark.parametrize(
    "mentor_id, category_id,test_file, expected_precision, k",
    [("clint_long", "background", "background_followups.csv", 0.7, 20)],
)
def test_sort(
    mentor_id: str,
    category_id: str,
    test_file: str,
    expected_precision: float,
    k: int,
    shared_root: str,
):
    good, bad = load_scored(mentor_id, category_id)
    precision = k_precision(category_id, mentor_id, test_file, good, bad, k)
    assert precision >= expected_precision
