#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
from flask import Blueprint, jsonify, request

from cerberus import Validator

from mentor_pipeline import AnswerPIPELINEInput
from mentor_pipeline.svm import SVMAnswerPIPELINE
from mentor_pipeline.svm.utils import dict_to_config

import json
import re

eval_blueprint = Blueprint("evaluate", __name__)
under_pat = re.compile(r"_([a-z])")


def underscore_to_camel(name: str) -> str:
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def to_camelcase(d: dict) -> dict:
    new_d = {}
    for k, v in d.items():
        new_d[underscore_to_camel(k)] = to_camelcase(v) if isinstance(v, dict) else v
    return new_d


@eval_blueprint.route("/", methods=["POST"])
@eval_blueprint.route("", methods=["POST"])
def evaluate():
    validator = Validator(
        {
            "mentor": {"required": True, "type": "string"},
            "input": {"required": True, "type": "string"},
            "question": {
                "required": False,
                "type": "string",
            },
            "config": {
                "required": False,
                "type": "dict",
                "schema": {
                    "question": {"type": "string", "required": False},
                    "questions": {"type": "list", "required": False},
                },
            },
        },
        allow_unknown=True,
        purge_unknown=True,
    )
    if not validator(request.json or {}):
        return jsonify(validator.errors), 400
    args = validator.document
    model_root = os.environ.get("MODEL_ROOT") or "models"
    question_models = os.path.join(model_root, args.get("mentor"))
    config_data = {}
    input_sentence = args.get("input")
    exp_num = int(args.get("question", -1))
    if not os.path.isdir(question_models):
        if not args.get("config"):
            return (
                jsonify(
                    {
                        "message": f"No models found for mentor {args.get('mentor')}. Config data is required"
                    }
                ),
                404,
            )
        else:
            question_models = os.path.join(model_root, "default")
            config_data = args.get("config")
    version_path = os.path.join(question_models, "build_version.json")
    version = None
    if os.path.isfile(version_path):
        with open(version_path) as f:
            version = json.load(f)
    shared_root = os.environ.get("SHARED_ROOT") or "shared"
    pipeline = SVMAnswerPIPELINE(model_root=question_models, shared_root=shared_root)
    _model_op = pipeline.evaluate(
        AnswerPIPELINEInput(
            input_sentence=input_sentence,
            config_data=dict_to_config(config_data),
            question=exp_num,
        )
    )
    return (
        jsonify({"output": to_camelcase(_model_op.to_dict()), "version": version}),
        200,
    )
