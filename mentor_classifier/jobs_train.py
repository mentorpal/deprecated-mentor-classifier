import random
from spacy.util import minibatch, compounding
from typing import List, Tuple, Dict, Union
from spacy import Language
from spacy.training import Example
from spacy.tokens import DocBin
import csv
from os import path

class CustomSpacy():
    train: List[Tuple[str,Dict[str,List[Tuple[Union[int, str]]]]]]
    model: Language

    def __init__(self, nlp: Language, data_path: str):
        self.model = nlp
        self.train = self.load_training(data_path)
    
    def load_training(self, data_path: str) -> List[Tuple[str,Dict[str,List[Tuple[Union[int, str]]]]]]:
        training = DocBin()
        with open(data_path) as f:
            csv_reader = csv.reader(f, delimiter=",")
            next(csv_reader)
            for row in csv_reader:
                context = row[1]
                start_index = int(row[2])
                end_index = int(row[3])
                doc = self.model.make_doc(context)
                span = doc.char_span(start_index, end_index, label = "JOB", alignment_mode = "contract")
                ents = []
                if span is None:
                    break
                ents.append(span)
                doc.ents = ents
                training.add(doc)
        training.to_disk(path.join(path.abspath("../../"), "train.spacy"))
        return training

   
    def new_model(self)-> Language:
        nlp = self.model
        nlp.initialize(lambda: self.train)
        ner=nlp.get_pipe("ner")
        ner.add_label("JOB")
        pipe_exceptions = ["ner"]
        unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
        with nlp.disable_pipes(*unaffected_pipes):
            for i in range(20):
                random.shuffle(self.train)
                batches = minibatch(self.train, size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    nlp.update(batch)          
        self.model = nlp
        return nlp
