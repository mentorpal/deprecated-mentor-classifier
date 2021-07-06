from os import path

import pytest
import logging
import responses

from mentor_classifier import ClassifierFactory, ARCH_LR
from .helpers import (
    fixture_mentor_data,
    fixture_path,
    load_mentor_csv,
)
from mentor_classifier.ner import find_ents
from .helpers import get_answers

@pytest.mark.only
@responses.activate
@pytest.mark.parametrize(
    "mentor_id",
    [
       "clint"
    ],
)
def test_ner(
   mentor_id: str
):
    mentor = load_mentor_csv(
        fixture_mentor_data(mentor_id, "data.csv")
    )
    answers = get_answers(mentor)
    ents = find_ents(answers)
    import logging
    logging.warning(mentor)
    assert 0 == 1