#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from dataclasses import asdict, dataclass, field, fields
from typing import Any, Dict, List, Type

from mentor_classifier.utils import sanitize_string


def dc_field_names(dc_class: Type) -> List[str]:
    """
    get the field names for a dataclass
    """
    return [f.name for f in fields(dc_class)]


def dict_to_dc(d: dict, dc_class: Type):
    """
    safe convert a dict to a dataclass of whatever type
    by extracting only the props from the dict that
    have matching fields in the dataclass type
    """
    if isinstance(d, dict):
        return dc_class(**{k: v for k, v in d.items() if k in dc_field_names(dc_class)})
    else:
        return d


def fix_dict_items(items: List[Any], dc_class: Type) -> List[Any]:
    return [
        x if not isinstance(x, dict) else dict_to_dc(x, dc_class) for x in items or []
    ]


@dataclass
class TopicConfig:
    _id: str = ""
    name: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class QuestionConfig:
    _id: str = ""
    question: str = ""
    type: str = ""
    name: str = ""
    paraphrases: List[str] = field(default_factory=list)
    topics: List[TopicConfig] = field(default_factory=list)

    def __post_init__(self):
        self.topics = fix_dict_items(self.topics, TopicConfig)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AnswerConfig:
    question: QuestionConfig
    _id: str = ""
    status: str = ""
    transcript: str = ""
    video: str = ""

    def __post_init__(self):
        self.question = dict_to_dc(self.question, QuestionConfig)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SubjectConfig:
    _id: str = ""
    name: str = ""
    questions: List[QuestionConfig] = field(default_factory=list)

    def __post_init__(self):
        self.questions = fix_dict_items(self.questions, QuestionConfig)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MentorConfig:
    _id: str = ""
    name: str = ""
    firstName: str = ""  # noqa: N815
    title: str = ""
    answers: List[AnswerConfig] = field(default_factory=list)
    subjects: List[SubjectConfig] = field(default_factory=list)

    def __post_init__(self):
        self.answers = fix_dict_items(self.answers, AnswerConfig)
        self.subjects = fix_dict_items(self.subjects, SubjectConfig)

    def to_dict(self) -> dict:
        return asdict(self)


def mentor_config_from_dict(d: dict) -> MentorConfig:
    return dict_to_dc(d, MentorConfig)


class Mentor(object):
    def __init__(self, id: str, data: MentorConfig):
        self.id = id
        self.name = data.name
        self.short_name = data.firstName
        self.title = data.title
        self.topics: List[str] = []
        self.subjects_by_id: Dict[str, Any] = {}
        self.topics_by_id: Dict[str, Any] = {}
        self.questions_by_id: Dict[str, Any] = {}
        self.questions_by_text: Dict[str, Any] = {}
        self.questions_by_answer: Dict[str, Any] = {}
        self.utterances_by_type: Dict[str, Any] = {
            "_IDLE_": [],
            "_INTRO_": [],
            "_OFF_TOPIC_": [],
            "_PROMPT_": [],
            "_FEEDBACK_": [],
            "_REPEAT_": [],
            "_REPEAT_BUMP_": [],
            "_PROFANITY_": [],
        }
        self.load_topics(data)
        self.load_questions(data)

    def load_topics(self, data: MentorConfig):
        for s in data.subjects or []:
            self.topics.append(s.name)
            subject_questions: List[str] = []
            subject_topics: List[str] = []
            subject = {
                "name": s.name,
                "questions": subject_questions,
                "topics": subject_topics,
            }
            for q in s.questions or []:
                subject_questions.append(q._id)
                for topic in q.topics or []:
                    if topic.name and topic.name not in self.topics:
                        self.topics.append(topic.name)
                    if topic._id and topic._id not in subject_topics:
                        subject_topics.append(topic._id)
                    if topic._id and topic._id not in self.topics_by_id:
                        self.topics_by_id[topic._id] = {
                            "name": topic.name or "",
                            "questions": [],
                        }
                    self.topics_by_id[topic._id]["questions"].append(q._id)
            self.subjects_by_id[s._id] = subject

    def load_questions(self, data: MentorConfig):
        for answer in data.answers or []:
            question = answer.question
            qid = question._id
            if answer.status != "COMPLETE":
                for sid in self.subjects_by_id:
                    if qid in self.subjects_by_id[sid]["questions"]:
                        self.subjects_by_id[sid]["questions"].remove(qid)
                for tid in self.topics_by_id:
                    if qid in self.topics_by_id[tid]["questions"]:
                        self.topics_by_id[tid]["questions"].remove(qid)
                continue
            if question.type == "UTTERANCE":
                self.utterances_by_type[question.name].append(
                    [answer._id, answer.transcript]
                )
                continue
            qtopics: List[str] = []
            q = {
                "id": qid,
                "question_text": question.question,
                "paraphrases": question.paraphrases,
                "answer": answer.transcript,
                "answer_id": answer._id,
                "video": answer.video,
                "topics": qtopics,
            }
            for sid in self.subjects_by_id:
                if qid in self.subjects_by_id[sid]["questions"]:
                    qtopics.append(self.subjects_by_id[sid]["name"])
            for tid in self.topics_by_id:
                if qid in self.topics_by_id[tid]["questions"]:
                    qtopics.append(self.topics_by_id[tid]["name"])
            self.questions_by_id[qid] = q
            self.questions_by_text[sanitize_string(q["question_text"])] = q
            for paraphrase in question.paraphrases:
                self.questions_by_text[sanitize_string(paraphrase)] = q
            self.questions_by_answer[sanitize_string(q["answer"])] = q


def mentor_from_dict(id: str, d: dict) -> Mentor:
    return Mentor(id, mentor_config_from_dict(d))
