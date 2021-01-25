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

import json
import re

eval_blueprint = Blueprint("evaluate", __name__)
under_pat = re.compile(r"_([a-z])")


@eval_blueprint.route("/", methods=["POST"])
@eval_blueprint.route("", methods=["POST"])
def evaluate():
    validator = Validator(
        {
            "mentor": {"required": True, "type": "string"},
            "question": {"required": True, "type": "string"},
        },
        allow_unknown=True,
        purge_unknown=True,
    )
    if not validator(request.json or {}):
        return jsonify(validator.errors), 400
    args = validator.document
    model_root = os.environ.get("MODEL_ROOT") or "models"
    mentor = args.get("mentor")
    mentor_models = os.path.join(model_root, mentor)
    input_question = args.get("question")
    if not os.path.isdir(mentor_models):
        return (
            jsonify({"message": f"No models found for mentor {mentor}."}),
            404,
        )
    shared_root = os.environ.get("SHARED_ROOT") or "shared"
    classifier = Classifier(mentor, shared_root, model_root)
    answer_id, answer, confidence = classifier.evaluate(input_question)
    return (
        jsonify({"answerId": answer_id, "answer": answer, "confidence": confidence}),
        200,
    )
