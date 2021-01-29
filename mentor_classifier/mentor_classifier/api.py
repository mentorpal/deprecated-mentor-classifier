#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
import os
import requests

GRAPHQL_ENDPOINT = os.environ.get("GRAPHQL_ENDPOINT") or "http://graphql/graphql"


def __fetch_mentor_data(mentor: str, url=GRAPHQL_ENDPOINT) -> dict:
    if not url.startswith("http"):
        with open(url) as f:
            return json.load(f)
    res = requests.post(
        url,
        json={
            "query": f'query {{ mentor(id: "{mentor}") {{ answers {{ question {{ _id question subject {{ name }} topics {{ name }} }} transcript video }} }} }}'
        },
    )
    res.raise_for_status()
    return res.json()


def fetch_mentor_data(mentor: str, url=GRAPHQL_ENDPOINT) -> dict:
    tdjson = __fetch_mentor_data(mentor, url)
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))
    data = tdjson["data"]["mentor"]
    return data
