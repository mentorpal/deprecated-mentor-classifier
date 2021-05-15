#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from mentor_classifier import (
    ArchClassifierFactory,
    QuestionClassifierTraining,
    QuestionClassifierPrediction,
    register_classifier_factory,
    ARCH_TRANSFORMERS,
)
from .predict import TransformersQuestionClassifierPrediction
from .train import TransformersQuestionClassifierTraining


class TransformerClassifierFactory(ArchClassifierFactory):
    def new_training(
        self, mentor, shared_root: str = "shared", output_dir: str = "out"
    ) -> QuestionClassifierTraining:
        return TransformersQuestionClassifierTraining(
            mentor=mentor, shared_root=shared_root, output_dir=output_dir
        )

    def new_prediction(
        self, mentor, shared_root, data_path
    ) -> QuestionClassifierPrediction:
        return TransformersQuestionClassifierPrediction(
            mentor=mentor, shared_root=shared_root, data_path=data_path
        )


register_classifier_factory(ARCH_TRANSFORMERS, TransformerClassifierFactory())
