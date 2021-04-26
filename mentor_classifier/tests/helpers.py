#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import path
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Tuple


@dataclass
class MentorQuestion:
    questionId: str
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
    question: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    paraphrases: Optional[List[str]] = None


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

    def addMentorQuestion(self, mentorQuestion: MentorQuestion):
        questionRef = Question(_id=mentorQuestion.questionId)
        topic = Topic(mentorQuestion.topic)
        questionAndTopics = QuestionAndTopics(question=questionRef, topics=[topic])
        if topic not in self.topics:
            self.topics.append(topic)
        self.questions.append(questionAndTopics)
        question = Question(
            _id=mentorQuestion.questionId,
            question=mentorQuestion.question,
            type=None,
            name=None,
            paraphrases=mentorQuestion.paraphrases,
        )
        answer = Answer(
            _id="A" + str(len(self.answers) + 1),
            status="COMPLETE",
            transcript=mentorQuestion.answer,
            question=question,
        )
        self.answers.append(answer)


def loadMentorCSV(path: str) -> Mentor:
    result = Mentor()
    with open(path) as f:
        lines = f.readlines()
        lines.pop(0)

        for line in lines:
            mentorQuestion = parseMentorQuestion(line)
            result.addMentorQuestion(mentorQuestion)

    return result


def parseMentorQuestion(csvLine: str) -> MentorQuestion:
    columns = csvLine.split(",")
    paraphrases = None
    if columns[2] != "":
        paraphrases = columns[2].split("|")
    return MentorQuestion(
        questionId=columns[0],
        question=columns[1],
        paraphrases=paraphrases,
        answer=columns[3],
        topic=columns[4],
    )


def fixture_path(p: str) -> str:
    return path.abspath(path.join(".", "tests", "fixtures", p))
