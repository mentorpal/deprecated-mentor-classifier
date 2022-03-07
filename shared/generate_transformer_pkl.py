#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import sys
from os import path

if __name__ == "__main__":
    pkl = f"{sys.argv[-1]}/transformer.pkl"
    if path.exists(pkl):
        print(f"{pkl} exists, skipping")
    else:
        print(f"generating {pkl}")
        # loading these takes 10+sec so only do it here:
        from mentor_classifier.arch.lr_transformer.embeddings import (
            TransformerEmbeddings,
        )
        import joblib

        transformer = TransformerEmbeddings(sys.argv[-1])
        joblib.dump(transformer, pkl)
        print(f"{pkl} created")
