import spacy
from spacy.matcher import Matcher
from typing import List
from mentor_classifier.ner import FollowupQuestion
from mentor_classifier.types import AnswerInfo
from mentor_classifier.spacy_model import find_or_load_spacy
from mentor_classifier.utils import get_shared_root
from os import path

def remove_duplicates(followups: List[FollowupQuestion], answered: List[AnswerInfo]):
    shared_root = get_shared_root()
    nlp = find_or_load_spacy(path.join(shared_root, "spacy-model"))
    matcher = Matcher(nlp.vocab)
    patterns = [{"LOWER": followup.question} for followup in followups]
    matcher.add(patterns)
    deduplicated = [question for question in answered if matcher(nlp(question.question_text)) == []]
    return deduplicated


