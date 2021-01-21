#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
import numpy as np

from tensorflow.keras.models import load_model
from sklearn.externals import joblib
from tensorflow.keras.preprocessing.sequence import pad_sequences

from mentor_pipeline.mentor import Mentor
from mentor_pipeline.utils import sanitize_string
from .nltk_preprocessor import NLTKPreprocessor
from .word2vec import find_or_load_word2vec


class Classifier:
    def __init__(self, mentor, shared_root, data_path):
        if isinstance(mentor, str):
            print("loading mentor id {}...".format(mentor))
            mentor = Mentor(mentor)
        assert isinstance(
            mentor, Mentor
        ), "invalid type for mentor (expected mentor.Mentor or string id for a mentor, encountered {}".format(
            type(mentor)
        )
        self.mentor = mentor
        self.model_path = os.path.join(data_path, mentor.id)
        self.w2v_model = find_or_load_word2vec(path.join(shared_root, "word2vec.bin"))
        self.logistic_model, self.topic_model = self.__load_model(self.model_path)

    def evaluate(self, question, canned_question_match_disabled=False):
        if not canned_question_match_disabled:
            sanitized_question = sanitize_string(question)
            if sanitized_question in self.mentor.questions_by_text:
                question = self.mentor.questions_by_text[sanitized_question]
                answer_id = question["id"]
                answer = question["answer"]
                return answer_id, answer, 1.0
        preprocessor = NLTKPreprocessor()
        processed_question = preprocessor.transform(question)
        w2v_vector, lstm_vector = self.w2v_model.w2v_for_question(processed_question)
        padded_vector = pad_sequences(
            [lstm_vector],
            maxlen=25,
            dtype="float32",
            padding="post",
            truncating="post",
            value=0.0,
        )
        topic_vector = self.__get_topic_vector(padded_vector)
        predicted_answer = self.__get_prediction(w2v_vector, topic_vector)
        return predicted_answer

    def __load_model(self, model_path):
        logistic_model = None
        topic_model = None
        word2vec = None
        print("loading model from path {}...".format(model_path))
        if not os.path.exists(model_path) or not os.listdir(model_path):
            print("Local checkpoint {0} does not exist.".format(model_path))
        try:
            path = os.path.join(model_path, "lstm_topic_model.h5")
            topic_model = load_model(path)
        except BaseException:
            print(
                "Unable to load topic model from {0}. Classifier needs to be retrained before asking questions.".format(
                    path
                )
            )
        try:
            path = os.path.join(model_path, "fused_model.pkl")
            logistic_model = joblib.load(path)
        except BaseException:
            print(
                "Unable to load logistic model from {0}. Classifier needs to be retrained before asking questions.".format(
                    path
                )
            )
        return logistic_model, topic_model

    def __get_topic_vector(self, lstm_vector):
        if self.topic_model is None:
            try:
                self.topic_model = load_model(
                    os.path.join(self.model_path, "lstm_topic_model.h5")
                )
            except BaseException:
                raise Exception(
                    "Could not find topic model under {0}. Please train classifier first.".format(
                        self.model_path
                    )
                )

        predicted_vector = self.topic_model.predict(lstm_vector)
        return predicted_vector[0]

    def __get_prediction(self, w2v_vector, topic_vector):
        model_path = self.model_path
        if self.logistic_model is None:
            try:
                self.logistic_model = joblib.load(
                    os.path.join(model_path, "fused_model.pkl")
                )
            except BaseException:
                raise Exception(
                    "Could not find logistic model under {0}. Please train classifier first.".format(
                        model_path
                    )
                )
        test_vector = np.concatenate((w2v_vector, topic_vector))
        test_vector = test_vector.reshape(1, -1)
        prediction = self.logistic_model.predict(test_vector)
        decision = self.logistic_model.decision_function(test_vector)
        confidence_scorces = (
            sorted(decision[0]) if decision.ndim >= 2 else sorted(decision)
        )
        highest_confidence = confidence_scorces[-1]
        if highest_confidence < -0.88:
            return "_OFF_TOPIC_", "_OFF_TOPIC_", highest_confidence
        if not len(prediction) >= 1 and prediction[0]:
            raise Exception(
                f"Prediction should be a list with at least one element (answer text) but found {prediction}"
            )
        answer_text = prediction[0]
        answer_id = self.mentor.questions_by_answer(sanitize_string(answer_text))
        if not answer_id:
            raise Exception(
                f"No answer id found for answer text (classifier_data may be out of sync with trained model): {answer_text}"
            )
        return answer_id, answer_text, highest_confidence
