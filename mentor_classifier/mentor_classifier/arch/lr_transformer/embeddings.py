#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from mentor_classifier.sentence_transformer import find_or_load_sentence_transformer
from sentence_transformers import SentenceTransformer
import joblib
import sys
from os import path
from typing import List, Union


class TransformerEmbeddings:
    def __init__(self, shared_root: str):
        self.transformer: SentenceTransformer = find_or_load_sentence_transformer(
            path.join(shared_root, "sentence-transformer")
        )

    def get_embeddings(self, data: Union[str, List[str]]):
        embeddings = self.transformer.encode(data, show_progress_bar=True)
        return embeddings


if __name__ == "__main__":
    pkl = f"{sys.argv[-1]}/transformer.pkl"
    if path.exists(pkl):
        print(f"{pkl} exists, skipping")
    else:
        print(f"generating {pkl}")
        transformer = TransformerEmbeddings(sys.argv[-1])
        joblib.dump(transformer, pkl)
        print(f"{pkl} created")
