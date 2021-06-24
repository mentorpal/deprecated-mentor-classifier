# import os
from mentor_classifier.api import fetch_training_data
from flask import Blueprint, make_response

# from os.path import expanduser

# HOME = expanduser("~")

fetch_blueprint = Blueprint("fetch", __name__)


@fetch_blueprint.route("/<mentor>", methods=["GET"])
def get_data(mentor: str):
    data = fetch_training_data(mentor)
    data_csv = data.to_csv(index=False)
    # data.to_csv(os.path.join(HOME, "Downloads", "mentor.csv"), index=False)
    output = make_response(data_csv)
    output.headers["Content-Disposition"] = "attachment; filename=mentor.csv"
    output.headers["Content-type"] = "text/csv"
    return (
        output,
        200,
    )
