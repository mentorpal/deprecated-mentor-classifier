#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
from json import JSONDecodeError
from functools import wraps
from jsonschema import validate, ValidationError
from flask import request
from werkzeug.exceptions import BadRequest
import logging

log = logging.getLogger()


def validate_json_payload_decorator(json_schema):
    def validate_json_wrapper(f):
        @wraps(f)
        def json_validated_function(*args, **kwargs):
            if not json_schema:
                raise Exception("'json_schema' param not provided to validator")
            body = request.form.get("body", {})
            if body:
                try:
                    json_body = json.loads(body)
                except JSONDecodeError as err:
                    raise err
            else:
                json_body = request.json
            if not json_body:
                raise BadRequest("missing required param body")
            try:
                validate(instance=json_body, schema=json_schema)
                return f(json_body, *args, **kwargs)
            except ValidationError as err:
                log.error(err)
                raise err

        return json_validated_function

    return validate_json_wrapper
