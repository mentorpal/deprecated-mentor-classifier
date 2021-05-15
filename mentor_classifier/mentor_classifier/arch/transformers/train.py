#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import RidgeClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score

from mentor_classifier import (
    QuestionClassifierTraining,
    QuestionClassifierTrainingResult,
    mentor_model_path,
    ARCH_TRANSFORMERS,
)
from mentor_classifier.mentor import Mentor
from .embeddings import TransformerEmbeddings
from ...api import update_training
from ...utils import sanitize_string


class TransformersQuestionClassifierTraining(QuestionClassifierTraining):
    def __init__(self, mentor, shared_root: str = "shared", output_dir: str = "out"):
        if isinstance(mentor, str):
            print("loading mentor id {}...".format(mentor))
            mentor = Mentor(mentor)
        assert isinstance(
            mentor, Mentor
        ), "invalid type for mentor (expected mentor.Mentor or string id for a mentor, encountered {}".format(
            type(mentor)
        )
        self.mentor = mentor
        self.model_path = mentor_model_path(output_dir, mentor.id, ARCH_TRANSFORMERS)
        self.transformer = TransformerEmbeddings()

    def train(self) -> QuestionClassifierTrainingResult:
        x_train, y_train = self.__load_training_data()
        x_train, y_train = self.__load_transformer_embeddings(x_train, y_train)
        classifier = self.train_ridge_classifier(x_train, y_train)
        training_accuracy = self.calculate_accuracy(
            classifier.predict(x_train), y_train
        )
        scores = cross_val_score(classifier, x_train, y_train, cv=2)
        # cv_accuracy = self.calculate_accuracy(
        #     cross_val_predict(self.classifier, x_train, y_train, cv=2), y_train
        # )
        update_training(self.mentor.id)
        os.makedirs(self.model_path, exist_ok=True)
        joblib.dump(classifier, os.path.join(self.model_path, "model.pkl"))
        joblib.dump(self.transformer, os.path.join(self.model_path, "transformer.pkl"))
        return QuestionClassifierTrainingResult(
            scores, training_accuracy, self.model_path
        )

    def __load_training_data(self):
        x_train = []
        y_train = []
        for key in self.mentor.questions_by_id:
            question = self.mentor.questions_by_id[key]
            current_question = sanitize_string(question["question_text"])
            answer_id = question["answer_id"]
            x_train.append(current_question)  # Add current question to training sample.
            y_train.append(answer_id)
            for paraphrase in question[
                "paraphrases"
            ]:  # Add paraphrases to training sample.
                x_train.append(sanitize_string(paraphrase))
                y_train.append(answer_id)
        return x_train, y_train

    def __load_transformer_embeddings(self, x_train, y_train):
        return np.array(self.transformer.get_embeddings(x_train)), np.array(y_train)

    def train_ridge_classifier(self, x_train, y_train, alpha=1.0):
        classifier = RidgeClassifier(alpha=alpha)
        classifier.fit(x_train, y_train)
        return classifier

    def train_lr_classifier(
        self,
        x_train,
        y_train,
        solver="lbfgs",
        multi_class="multinomial",
        max_iter=1000,
        c=0.1,
    ):
        classifier = LogisticRegression(
            solver=solver, multi_class=multi_class, max_iter=max_iter, C=c
        )
        classifier.fit(x_train, y_train)
        return classifier

    @staticmethod
    def calculate_accuracy(predictions, labels):
        return accuracy_score(labels, predictions)

    @staticmethod
    def calculate_relevant_accuracy(predictions, labels):
        cnt = 0
        for pred, label in zip(predictions, labels):
            if pred in label:
                cnt += 1
        return cnt / len(predictions)
