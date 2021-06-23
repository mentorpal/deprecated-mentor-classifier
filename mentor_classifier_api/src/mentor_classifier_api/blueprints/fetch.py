import os
from flask import Blueprint

from mentor_classifier.api import fetch_training_data

fetch_blueprint = Blueprint("fetch", __name__)

@fetch_blueprint.route('/<mentor>', methods=["GET"])
def get_data(mentor:str):
    data = fetch_training_data(mentor)
    return (
        data,
        200,
    )
