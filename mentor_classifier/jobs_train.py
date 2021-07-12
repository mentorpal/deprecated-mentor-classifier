import random
from spacy.util import minibatch, compounding
from typing import List, Tuple, Dict, Union
from mentor_classifier.spacy_model import find_or_load_spacy
from spacy import Language
import csv

class CustomSpacy():
    train: List(Tuple(str,Dict[str,List(Tuple(Union[int, str]))]))
    model: Language

    def __init__(self, nlp: Language, data_path: str):
        self.model = nlp
        self.train = self.load_training(data_path)
    
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
    
    def new_model(self):
        nlp = self.model
        ner=nlp.get_pipe("ner")
        ner.add_label("JOB")
        pipe_exceptions = ["ner"]
        unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
        with nlp.disable_pipes(*unaffected_pipes):
            random.shuffle(self.train)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(self.train, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                            texts,  # batch of texts
                            annotations,  # batch of annotations
                            drop=0.5,  # dropout - make it harder to memorise data
                            losses=losses,
                        )
        self.model = nlp
        return nlp
