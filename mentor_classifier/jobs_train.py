from typing import List, Tuple, Dict, Union
from mentor_classifier.spacy_model import find_or_load_spacy
from spacy import Language
import csv

class CustomSpacy():
    train: List(Tuple(str,Dict[str,List(Tuple(Union[int, str]))]))
    model: Language

    def __init__(self, shared_root: str, data_path: str):
        model = find_or_load_spacy(shared_root)
        train = self.load_training(data_path)
    
    @staticmethod
    def load_training(data_path: str) -> List(Tuple(str,Dict[str,List(Tuple(Union[int, str]))])):
        training = []
        with open(data_path) as f:
            csv_reader = csv.reader(f, delimiter=",")
            next(csv_reader)
            for row in csv_reader:
                context = row[1]
                start_index = row[2]
                end_index = row[3]
                entry = (context, {"entities":(start_index, end_index, "JOB")})
                training.append(entry)
        return training