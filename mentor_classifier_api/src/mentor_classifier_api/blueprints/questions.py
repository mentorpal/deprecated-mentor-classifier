#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
from flask import Blueprint, jsonify, request

from cerberus import Validator

from mentor_classifier.classifier import Classifier

import re

questions_blueprint = Blueprint("questions", __name__)
under_pat = re.compile(r"_([a-z])")


@questions_blueprint.route("/", methods=["GET", "POST"])
@questions_blueprint.route("", methods=["GET", "POST"])
def answer():
    if not "query" in request.args:
        return (
            jsonify({"query": ["required field"]}),
            400,
        )
    if not "mentor" in request.args:
        return (
            jsonify({"mentor": ["required field"]}),
            400,
        )
    question = request.args["query"].strip()
    mentor = request.args["mentor"].strip()
    model_root = os.environ.get("MODEL_ROOT") or "models"
    mentor_models = os.path.join(model_root, mentor)
    if not os.path.isdir(mentor_models):
        return (
            jsonify({"message": f"No models found for mentor {mentor}."}),
            404,
        )
    shared_root = os.environ.get("SHARED_ROOT") or "shared"
    classifier = Classifier(mentor, shared_root, model_root)
    answer_id, answer, confidence = classifier.evaluate(question)
    return (
        jsonify(
            {
                "query": question,
                "answer_id": answer_id,
                "answer_text": answer,
                "confidence": confidence,
                "classifier": "",
            }
        ),
        200,
    )
