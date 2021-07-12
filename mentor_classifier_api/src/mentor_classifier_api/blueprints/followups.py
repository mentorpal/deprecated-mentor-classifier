#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from flask import Blueprint, jsonify
from mentor_classifier.api import generate_followups

followups_blueprint = Blueprint("followups", __name__)


@followups_blueprint.route("/followups/category/<category>", methods=["GET"])
def followup(category: str):
    data = generate_followups(category)
    questions = []
    for question in data:
        question_dict = {
            "question": question.question,
            "entityType": question.entity_type,
            "template": question.template,
        }
        questions.append(question_dict)
    return jsonify(
        {
            "data": {"followups": questions},
        }
    )
