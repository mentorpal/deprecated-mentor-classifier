from os import path
from sentence_transformers import SentenceTransformer


def find_or_load_sentence_transformer(file_path: str) -> SentenceTransformer:
    return SentenceTransformer(path.join(file_path, "distilbert-base-nli-mean-tokens"))