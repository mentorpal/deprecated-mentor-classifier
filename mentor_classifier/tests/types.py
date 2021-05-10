#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from dataclasses import dataclass, field, asdict
from typing import List
from enum import Enum


class ComparisonType(Enum):
    EQ = 0
    GTE = 1
    LT = 2


@dataclass
class _MentorTrainAndTestConfiguration:
    mentor_id: str
    arch: str
    expected_training_accuracy: float


@dataclass
class _MentorTestSetEntry:
    question: str
    expected_answer: str
    expected_confidence: float
    comparison_type: ComparisonType = ComparisonType.GTE


@dataclass
class _MentorTestSet:
    tests: List[_MentorTestSetEntry] = field(default_factory=list)


@dataclass
class _MentorTestResultEntry:
    entry: _MentorTestSetEntry
    passing: bool = True


@dataclass
class _MentorTestSetResult:
    passing_tests: int = 0
    results: List[_MentorTestResultEntry] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class MentorQuestion:
    question_id: str
    question: str
    paraphrases: List[str]
    answer: str
    topic: str


@dataclass
class Subject:
    name: str


@dataclass
class Topic:
    name: str


@dataclass
class Question:
    _id: str
    question: str = ""
    type: str = ""
    name: str = ""
    paraphrases: List[str] = field(default_factory=list)


@dataclass
class Answer:
    _id: str
    status: str
    transcript: str
    question: Question


@dataclass
class QuestionAndTopics:
    question: Question
    topics: List[Topic]


@dataclass
class Mentor:
    subjects: List[Subject] = field(default_factory=list)
    topics: List[Topic] = field(default_factory=list)
    questions: List[QuestionAndTopics] = field(default_factory=list)
    answers: List[Answer] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    def add_mentor_question(self, mentor_question: MentorQuestion):
        question_ref = Question(_id=mentor_question.question_id)
        topic = Topic(mentor_question.topic)
        question_and_topics = QuestionAndTopics(question=question_ref, topics=[topic])
        if topic not in self.topics:
            self.topics.append(topic)
        self.questions.append(question_and_topics)
        question = Question(
            _id=mentor_question.question_id,
            question=mentor_question.question,
            type="",
            name="",
            paraphrases=mentor_question.paraphrases,
        )
        answer = Answer(
            _id=f"A{str(len(self.answers) + 1)}",
            status="COMPLETE",
            transcript=mentor_question.answer,
            question=question,
        )
        self.answers.append(answer)
