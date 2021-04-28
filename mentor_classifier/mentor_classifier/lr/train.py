#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import joblib
import logging
import os
from typing import List, Tuple


import numpy as np
from sklearn import metrics
from sklearn.linear_model import RidgeClassifier
from sklearn.model_selection import cross_val_score, cross_val_predict


from mentor_classifier.api import update_training
from mentor_classifier.mentor import Mentor
from .nltk_preprocessor import NLTKPreprocessor
from .word2vec import W2V


class ClassifierTraining:
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
        self.w2v = W2V(os.path.join(shared_root, "word2vec.bin"))
        self.model_path = os.path.join(output_dir, mentor.id)

    """
    Trains the classifier updating trained weights to be saved later with save()
    Returns:
        scores: (float array) cross validation scores for training data
        accuracy: (float) accuracy score for training data
    """

    def train(self) -> Tuple[List[float], float, str]:
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        training_data, num_rows_having_paraphrases = self.__load_training_data()
        train_vectors = self.__load_training_vectors(training_data)
        train_vectors = self.__load_topic_vectors(train_vectors)
        (
            x_train,
            y_train,
        ) = self.__load_xy_vectors(train_vectors)
        (scores, accuracy, self.logistic_model) = self.__train_lr(
            x_train,
            y_train,
            num_rows_having_paraphrases,
        )
        update_training(self.mentor.id)
        return scores, accuracy, self.model_path

    def save(self, to_path=None):
        to_path = to_path or self.model_path
        os.makedirs(to_path, exist_ok=True)
        joblib.dump(self.logistic_model, os.path.join(to_path, "model.pkl"))
        with open(os.path.join(to_path, "w2v.txt"), "w") as f:
            f.write(self.w2v.get_w2v_file_path())

    def __load_training_data(self):
        preprocessor = NLTKPreprocessor()
        train_data = []
        num_rows_having_paraphrases = 0
        for key in self.mentor.questions_by_id:
            question = self.mentor.questions_by_id[key]
            topics = question["topics"]
            current_question = question["question_text"]
            num_rows_having_paraphrases += len(question["paraphrases"])
            answer = question["answer"]
            answer_id = key
            # add question to dataset
            processed_question = preprocessor.transform(current_question)
            # tokenize the question
            train_data.append(
                [current_question, processed_question, topics, answer_id, answer]
            )
            # look for paraphrases and add them to dataset
            for paraphrase in question["paraphrases"]:
                processed_paraphrase = preprocessor.transform(paraphrase)
                train_data.append(
                    [paraphrase, processed_paraphrase, topics, answer_id, answer]
                )
        return train_data, num_rows_having_paraphrases

    def __load_training_vectors(self, train_data):
        train_vectors = []
        # for each data point, get w2v vector for the question and store in train_vectors.
        # instance=<question, processed_question, topic, answer_id, answer_text>
        for instance in train_data:
            w2v_vector, lstm_vector = self.w2v.w2v_for_question(instance[1])
            train_vectors.append(
                [instance[0], w2v_vector.tolist(), instance[2], instance[4]]
            )
        return train_vectors

    def __load_topic_vectors(self, train_vectors):
        # Generate the sparse topic train_vectors
        for i in range(len(train_vectors)):
            # vector=train_vectors[i][1]
            current_topics = train_vectors[i][2]
            topic_vector = [0] * len(self.mentor.topics)
            for j in range(len(self.mentor.topics)):
                if self.mentor.topics[j] in current_topics:
                    topic_vector[j] = 1
            train_vectors[i][2] = topic_vector

        return train_vectors

    def __load_xy_vectors(self, train_data):
        x_train = []
        y_train = []
        x_train = [train_data[i][1] for i in range(len(train_data))]
        y_train = [train_data[i][3] for i in range(len(train_data))]
        x_train = np.asarray(x_train)
        return x_train, y_train

    def __train_lr(
        self,
        x_train,
        y_train,
        num_rows_having_paraphrases,
    ):
        logistic_model = RidgeClassifier(alpha=1.0)
        logistic_model.fit(x_train, y_train)
        if num_rows_having_paraphrases < 1:
            logging.warning(
                "Classifier data had no questions with paraphrases. This makes cross validation checks fail, so they will be skipped"
            )
            return [], -1, logistic_model
        scores = cross_val_score(logistic_model, x_train, y_train, cv=2)
        predicted = cross_val_predict(logistic_model, x_train, y_train, cv=2)
        accuracy = metrics.accuracy_score(y_train, predicted)
        return scores, accuracy, logistic_model


def train(
    mentor: str,
    shared_root: str = "shared",
    output_dir: str = "out",
    save_model: bool = True,
):
    m = Mentor(mentor)
    classifier = ClassifierTraining(m, shared_root, output_dir)
    result = classifier.train()
    if save_model:
        classifier.save()
    return result
