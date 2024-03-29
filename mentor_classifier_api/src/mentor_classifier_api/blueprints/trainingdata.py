#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from mentor_classifier.api import fetch_training_data
from flask import Blueprint, make_response


trainingdata_blueprint = Blueprint("trainingdata", __name__)


@trainingdata_blueprint.route("/<mentor>", methods=["GET"])
def get_data(mentor: str):
    data_csv = fetch_training_data(mentor)
    output = make_response(data_csv)
    output.headers[
        "Content-Disposition"
    ] = f"attachment; filename={mentor}-trainingdata.csv"
    output.headers["Content-type"] = "text/csv"
    return (
        output,
        200,
    )
