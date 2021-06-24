#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
from mentor_classifier.api import fetch_training_data
from flask import Blueprint, make_response

from os.path import expanduser

# HOME = expanduser("~")

fetch_blueprint = Blueprint("fetch", __name__)


@fetch_blueprint.route("/<mentor>", methods=["GET"])
def get_data(mentor: str):
    data = fetch_training_data(mentor)
    data_csv = data.to_csv(index=False)
    import logging

    logging.warning("\n\n\n\nin bp, what is data_csv?")
    logging.warning(type(data_csv))
    logging.warning(data_csv)
    # data.to_csv(os.path.join(HOME, "Downloads", "mentor.csv"), index=False)
    output = make_response(data_csv)
    output.headers["Content-Disposition"] = "attachment; filename=mentor.csv"
    output.headers["Content-type"] = "text/csv"
    return (
        output,
        200,
    )
