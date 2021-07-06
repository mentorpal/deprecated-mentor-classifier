import spacy 
import logging
from typing import List, Dict


def find_ents(answers: List[str]) -> Dict[str, List[str]]:
    nlp = spacy.load('en_core_web_sm')
    entities = {
        "people":[],
        "places":[],
        "acronyms":[],
        #"jobs":[]

    }
    for answer in answers:
        answer = nlp(answer)
        if answer.ents: 
            for ent in answer.ents:
                if ent.label_ == "PERSON":
                    entities["people"].append(ent.text)
                if ent.label == "ORG":
                    entities["acronyms"].append(ent.text)
                if ent.label == "GPE":
                    entities["places"].append(ent.text)
        else:
            logging.warning('No named entities found.')

    return entities 

    