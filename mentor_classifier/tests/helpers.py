#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import path
from .types import (
    Mentor,
    MentorQuestion,
    _MentorTestSet,
    _MentorTestSetEntry,
    _MentorTestSetResult,
    _MentorTestResultEntry,
    ComparisonType,
)
from mentor_classifier import QuestionClassifierPrediction


def load_mentor_csv(path: str) -> Mentor:
    result = Mentor()
    with open(path) as f:
        lines = f.readlines()
        lines.pop(0)

        for line in lines:
            mentor_question = parse_mentor_question(line)
            result.add_mentor_question(mentor_question)

    return result


def load_test_csv(path: str) -> _MentorTestSet:
    result = _MentorTestSet()

    with open(path) as f:
        lines = f.readlines()
        lines.pop(0)

        for line in lines:
            result.tests.append(parse_testset_entry(line))

    return result


def parse_testset_entry(csv_line: str) -> _MentorTestSetEntry:
    columns = csv_line.split(",")
    return _MentorTestSetEntry(
        question=columns[0],
        expected_answer=columns[1],
        expected_confidence=float(columns[2]),
    )


def parse_mentor_question(csv_line: str) -> MentorQuestion:
    columns = csv_line.split(",")
    paraphrases = columns[2].split("|") if columns[2] else []
    return MentorQuestion(
        question_id=columns[0],
        question=columns[1],
        paraphrases=paraphrases,
        answer=columns[3],
        topic=columns[4],
    )


def fixture_path(p: str) -> str:
    return path.abspath(path.join(".", "tests", "fixtures", p))


def run_model_against_testset(
    evaluator: QuestionClassifierPrediction, test_set: _MentorTestSet
) -> _MentorTestSetResult:
    result = _MentorTestSetResult()

    for test_set_entry in test_set.tests:
        current_result_entry = _MentorTestResultEntry(test_set_entry)
        test_result = evaluator.evaluate(test_set_entry.question)

        if test_result.answer_text != test_set_entry.expected_answer:
            current_result_entry.passing = False
            result.errors.append(
                f"expected {test_set_entry.expected_answer} in response to {test_set_entry.question}, but got {test_result.answer_text} instead"
            )

        if test_set_entry.comparison_type == ComparisonType.GTE:
            if test_result.highest_confidence < test_set_entry.expected_confidence:
                current_result_entry.passing = False
                result.errors.append(
                    f"expected a confidence of at least {test_set_entry.expected_confidence}, but recieved a confidence of {test_result.highest_confidence}, for question/answer: {test_set_entry.question}/{test_result.answer_text}"
                )

        result.results.append(current_result_entry)

    return result
