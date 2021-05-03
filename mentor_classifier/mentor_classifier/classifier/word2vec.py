#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved. 
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import numpy as np

from gensim.models import KeyedVectors
from gensim.models.keyedvectors import Word2VecKeyedVectors
from os import path
from typing import Dict

WORD2VEC_MODELS: Dict[str, Word2VecKeyedVectors] = {}


class W2V(object):
    def __init__(self, file_path: str):
        self.__w2v_file_path = file_path
        self.__w2v_model = find_or_load_word2vec(file_path)

    def get_w2v_file_path(self):
        return self.__w2v_file_path

    def w2v_for_question(self, question):
        current_vector = np.zeros(300, dtype="float32")
        lstm_vector = []
        for word in question:
            try:
                word_vector = self.__w2v_model[word]
            except BaseException:
                word_vector = np.zeros(300, dtype="float32")
            lstm_vector.append(word_vector)
            current_vector += word_vector
        return current_vector, lstm_vector


def find_or_load_word2vec(file_path: str) -> Word2VecKeyedVectors:
    abs_path = path.abspath(file_path)
    if abs_path not in WORD2VEC_MODELS:
        WORD2VEC_MODELS[abs_path] = KeyedVectors.load_word2vec_format(
            abs_path, binary=True
        )
    return WORD2VEC_MODELS[abs_path]


def load_word2vec_model(path: str) -> Word2VecKeyedVectors:
    return KeyedVectors.load_word2vec_format(path, binary=True)
