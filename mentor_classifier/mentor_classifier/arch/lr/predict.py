#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import logging
import os
import joblib
import random

from mentor_classifier.api import (
    create_user_question,
    OFF_TOPIC_THRESHOLD,
)
from mentor_classifier import (
    QuestionClassifierPrediction,
    QuestionClassiferPredictionResult,
    mentor_model_path,
    ARCH_LR,
)
from mentor_classifier.mentor import Mentor
from mentor_classifier.utils import file_last_updated_at, sanitize_string
from .nltk_preprocessor import NLTKPreprocessor
from .word2vec import W2V


class LRQuestionClassifierPrediction(QuestionClassifierPrediction):
    def __init__(self, mentor, shared_root, data_path):
        if isinstance(mentor, str):
            logging.info("loading mentor id {}...".format(mentor))
            mentor = Mentor(mentor)
        assert isinstance(
            mentor, Mentor
        ), "invalid type for mentor (expected mentor.Mentor or string id for a mentor, encountered {}".format(
            type(mentor)
        )
        self.mentor = mentor
        self.model_file = mentor_model_path(data_path, mentor.id, ARCH_LR, "model.pkl")
        self.w2v_model = W2V(os.path.join(shared_root, "word2vec.bin"))
        self.model = self.__load_model()

    def evaluate(
        self, question, canned_question_match_disabled=False
    ) -> QuestionClassiferPredictionResult:
        if not canned_question_match_disabled:
            sanitized_question = sanitize_string(question)
            if sanitized_question in self.mentor.questions_by_text:
                q = self.mentor.questions_by_text[sanitized_question]
                answer_id = q["answer_id"]
                answer = q["answer"]
                answer_media = q["media"]
                feedback_id = create_user_question(
                    self.mentor.id,
                    question,
                    answer_id,
                    "PARAPHRASE"
                    if sanitized_question != sanitize_string(q["question_text"])
                    else "EXACT",
                    1.0,
                )
                return QuestionClassiferPredictionResult(
                    answer_id, answer, answer_media, 1.0, feedback_id
                )

        preprocessor = NLTKPreprocessor()
        processed_question = preprocessor.transform(question)
        w2v_vector, lstm_vector = self.w2v_model.w2v_for_question(processed_question)

        (
            answer_id,
            answer_text,
            answer_media,
            highest_confidence,
        ) = self.__get_prediction(w2v_vector)
        feedback_id = create_user_question(
            self.mentor.id,
            question,
            answer_id,
            "OFF_TOPIC" if highest_confidence < OFF_TOPIC_THRESHOLD else "CLASSIFIER",
            highest_confidence,
        )
        if highest_confidence < OFF_TOPIC_THRESHOLD:
            answer_id, answer_text, answer_media = self.__get_offtopic()
        return QuestionClassiferPredictionResult(
            answer_id, answer_text, answer_media, highest_confidence, feedback_id
        )

    def get_last_trained_at(self) -> float:
        return file_last_updated_at(self.model_file)

    def __load_model(self):
        logging.info("loading model from path {}...".format(self.model_file))
        return joblib.load(self.model_file)

    def __get_prediction(self, w2v_vector):
        if not self.model:
            self.model = joblib.load(self.model_file)
        test_vector = w2v_vector.reshape(1, -1)
        prediction = self.model.predict(test_vector)
        decision = self.model.decision_function(test_vector)
        confidence_scores = (
            sorted(decision[0]) if decision.ndim >= 2 else sorted(decision)
        )
        highest_confidence = confidence_scores[-1]
        if not (prediction and prediction[0]):
            raise Exception(
                f"Prediction should be a list with at least one element (answer text) but found {prediction}"
            )
        answer_text = prediction[0]
        answer_key = sanitize_string(answer_text)
        answer_id = (
            self.mentor.questions_by_answer[answer_key].get("answer_id", "")
            if answer_key in self.mentor.questions_by_answer
            else ""
        )
        answer_media = (
            self.mentor.questions_by_answer[answer_key].get("media", [])
            if answer_key in self.mentor.questions_by_answer
            else []
        )
        if not answer_id:
            raise Exception(
                f"No answer id found for answer text (classifier_data may be out of sync with trained model): {answer_text}"
            )
        return answer_id, answer_text, answer_media, highest_confidence

    def __get_offtopic(self):
        try:
            i = random.randint(
                0, len(self.mentor.utterances_by_type["_OFF_TOPIC_"]) - 1
            )
            return (
                self.mentor.utterances_by_type["_OFF_TOPIC_"][i][0],
                self.mentor.utterances_by_type["_OFF_TOPIC_"][i][1],
                self.mentor.utterances_by_type["_OFF_TOPIC_"][i][2],
            )
        except KeyError:
            return (
                "_OFF_TOPIC_",
                "_OFF_TOPIC_",
            )
