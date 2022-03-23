#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from typing import Dict

from flask import Blueprint, jsonify, request

from mentor_classifier.api import generate_followups

followups_blueprint = Blueprint("followups", __name__)


# this is a helper function and should go somewhere easy to share
def get_auth_headers() -> Dict[str, str]:
    return (
        {"Authorization": request.headers["Authorization"]}
        if "Authorization" in request.headers
        else {}
    )


@followups_blueprint.route("followups/category/<category>/<mentor>", methods=["POST"])
def followup(category: str, mentor: str):
    data = generate_followups(
        category, mentor, cookies=request.cookies, headers=get_auth_headers()
    )
    questions = [
        {
            "question": question.question,
            "entityType": question.entity,
            "template": question.template,
        }
        for question in data
    ]
    return jsonify(
        {
            "data": {"followups": questions},
        }
    )
