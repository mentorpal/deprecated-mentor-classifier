#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import pytest
import responses
from mentor_classifier.types import AnswerInfo
from mentor_classifier.ner import NamedEntities

@pytest.mark.only
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
        ("What is your job", "The Network Security Engineer provides support of the information systems security controls.", "What does a(n) Network Security Engineer do?"),
    ],
)
def test_questions(
    question: str,
    answer: str,
    expected_followup: str,
    shared_root: str,
):
    answer_info = AnswerInfo(question_text=question, answer_text=answer)
    answer_info_list = [answer_info]
    ents = NamedEntities(answer_info_list, shared_root)
    questions = ents.generate_questions()
    actual_question = questions[0].question
    assert actual_question == expected_followup
