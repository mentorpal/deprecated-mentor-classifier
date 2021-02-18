from typing import Dict
from .predict import Classifier

class Dao:
    def __init__(self, shared_root: str, data_root: str):
        self.shared_root = shared_root
        self.data_root = data_root
        self.cache: Dict[str, Classifier] = {}


    def find_classifier(self, mentor_id: str) -> Classifier:
        if mentor_id in self.cache:
            return self.cache[mentor_id]
        c = Classifier(mentor_id, self.shared_root, self.data_root)
        self.cache[mentor_id] = c
        return c