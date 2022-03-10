#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

from logging.config import dictConfig  # NOQA

from flask import Flask  # NOQA
from flask_cors import CORS  # NOQA
from .config_default import Config  # NOQA


def create_app():
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    from mentor_classifier_api.blueprints.questions import questions_blueprint

    app.register_blueprint(questions_blueprint, url_prefix="/classifier/questions")

    from mentor_classifier_api.blueprints.ping import ping_blueprint

    app.register_blueprint(ping_blueprint, url_prefix="/classifier/ping")

    from mentor_classifier_api.blueprints.train import train_blueprint

    app.register_blueprint(train_blueprint, url_prefix="/classifier/train")

    from mentor_classifier_api.blueprints.healthcheck import healthcheck_blueprint

    app.register_blueprint(healthcheck_blueprint, url_prefix="/classifier/healthcheck")

    from mentor_classifier_api.blueprints.trainingdata import trainingdata_blueprint

    app.register_blueprint(
        trainingdata_blueprint, url_prefix="/classifier/trainingdata/"
    )

    from mentor_classifier_api.blueprints.followups import followups_blueprint

    app.register_blueprint(followups_blueprint, url_prefix="/classifier/")

    return app
