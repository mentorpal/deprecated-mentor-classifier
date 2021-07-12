#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from io import StringIO
import json
import os

import pytest
import responses
import pandas as pd
import pandas.testing

from . import fixture_path


@pytest.fixture(autouse=True)
def python_path_env(monkeypatch, shared_root):
    monkeypatch.setenv("MODEL_ROOT", fixture_path("models"))
    monkeypatch.setenv("SHARED_ROOT", shared_root)


@responses.activate
@pytest.mark.parametrize(
    "input_mentor,",
    ["clint"],
)
def test_fetch_data(
    client,
    input_mentor,
):
    with open(fixture_path("graphql/{}.json".format(input_mentor))) as f:
        data = json.load(f)
        responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    res = client.post(f"/classifier/trainingdata/{input_mentor}")
    expected_data = pd.read_csv(
        fixture_path(os.path.join("fetched_training_data", f"{input_mentor}.csv"))
    )
    actual_data = pd.read_csv(StringIO(res.data.decode("utf-8")))
    pandas.testing.assert_frame_equal(actual_data, expected_data)
