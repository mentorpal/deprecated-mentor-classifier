from os import environ, path

import pylru

from mentor_classifier.mentor import Mentor
from mentor_classifier.api import fetch_mentor_data
from .predict import Classifier, get_classifier_last_trained_at


class Entry:
    def __init__(self, classifier: Classifier):
        self.classifier = classifier
        self.last_trained_at = self.classifier.get_last_trained_at()


class Dao:
    def __init__(self, shared_root: str, data_root: str):
        self.shared_root = shared_root
        self.data_root = data_root
        self.cache = pylru.lrucache(int(environ.get("CACHE_MAX_SIZE", "100")))

    def find_classifier(self, mentor_id: str) -> Classifier:
        if mentor_id in self.cache:
            e = self.cache[mentor_id]
            if e and e.last_trained_at >= get_classifier_last_trained_at(
                path.join(self.data_root, mentor_id)
            ):
                return e.classifier
        mentor = Mentor(mentor_id, fetch_mentor_data(mentor_id))
        c = Classifier(mentor, self.shared_root, self.data_root)
        self.cache[mentor_id] = Entry(c)
        return c
