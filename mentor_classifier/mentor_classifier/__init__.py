#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from abc import ABC, abstractmethod
from importlib import import_module
from typing import List, Dict
from os import environ
import os
from dataclasses import dataclass

from mentor_classifier.mentor import Media


def mentor_model_path(models_path: str, mentor_id: str, arch: str, p: str = "") -> str:
    return (
        os.path.join(models_path, mentor_id, arch, p)
        if p
        else os.path.join(models_path, mentor_id, arch)
    )


@dataclass
class QuestionClassifierTrainingResult:
    scores: List[float]
    accuracy: float
    model_path: str


@dataclass
class QuestionClassiferPredictionResult:
    answer_id: str
    answer_text: str
    answer_media: List[Media]
    highest_confidence: float
    feedback_id: str


class QuestionClassifierTraining(ABC):
    @abstractmethod
    def train(self) -> QuestionClassifierTrainingResult:
        raise NotImplementedError()


class QuestionClassifierPrediction(ABC):
    @abstractmethod
    def evaluate(
        self, question, canned_question_match_disabled=False
    ) -> QuestionClassiferPredictionResult:
        raise NotImplementedError()

    @abstractmethod
    def get_last_trained_at(self) -> float:
        raise NotImplementedError()


class ArchClassifierFactory(ABC):
    @abstractmethod
    def new_training(
        self, mentor: str, shared_root: str = "shared", output_dir: str = "out"
    ) -> QuestionClassifierTraining:
        raise NotImplementedError()

    @abstractmethod
    def new_prediction(
        self, mentor: str, shared_root: str, data_path: str
    ) -> QuestionClassifierPrediction:
        raise NotImplementedError()


_factories_by_arch: Dict[str, ArchClassifierFactory] = {}


def register_classifier_factory(arch: str, fac: ArchClassifierFactory) -> None:
    _factories_by_arch[arch] = fac


ARCH_LR = "mentor_classifier.arch.lr"
ARCH_LR_TRANSFORMER = "mentor_classifier.arch.transformers"
ARCH_DEFAULT = ARCH_LR


class ClassifierFactory:
    def _find_arch_fac(self, arch: str) -> ArchClassifierFactory:
        arch = arch or environ.get("CLASSIFIER_ARCH") or ARCH_DEFAULT
        if arch not in _factories_by_arch:
            import_module(arch)
        f = _factories_by_arch[arch]
        return f

    def new_prediction(
        self, mentor: str, shared_root: str, data_path: str, arch=""
    ) -> QuestionClassifierPrediction:
        return self._find_arch_fac(arch).new_prediction(
            mentor=mentor, shared_root=shared_root, data_path=data_path
        )

    def new_training(
        self, mentor: str, shared_root: str, data_path: str, arch=""
    ) -> QuestionClassifierTraining:
        return self._find_arch_fac(arch).new_training(
            mentor=mentor, shared_root=shared_root, output_dir=data_path
        )
