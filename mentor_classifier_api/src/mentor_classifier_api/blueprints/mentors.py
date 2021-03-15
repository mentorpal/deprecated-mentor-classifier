#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from flask import Blueprint, jsonify

from mentor_classifier.mentor import Mentor

import re

mentors_blueprint = Blueprint("mentors", __name__)
under_pat = re.compile(r"_([a-z])")


@mentors_blueprint.route("/<mentor_id>/data", methods=["GET"])
def fetch_mentor(mentor_id: str):
    m = Mentor(mentor_id)
    return jsonify(
        {
            "id": m.id,
            "name": m.name,
            "firstName": m.firstName,
            "title": m.title,
            "mentorType": m.mentorType,
            "subjects_by_id": m.subjects_by_id,
            "topics_by_id": m.topics_by_id,
            "questions_by_id": m.questions_by_id,
            "utterances_by_type": m.utterances_by_type,
        }
    )
