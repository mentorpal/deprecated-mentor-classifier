# #
# # This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# # Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
# #
# # The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
# #
# import json
# import os

# import pytest

# from mentor_classifier import QuestionPIPELINEResult, SpeechActPIPELINEResult  # type: ignore
# from . import fixture_path


# @pytest.fixture(scope="module")
# def shared_root(word2vec) -> str:
#     return os.path.dirname(word2vec)


# @pytest.fixture(autouse=True)
# def python_path_env(monkeypatch, shared_root):
#     monkeypatch.setenv("MODEL_ROOT", fixture_path("models"))
#     monkeypatch.setenv("SHARED_ROOT", shared_root)


# def test_returns_400_response_when_mentor_not_set(client):
#     res = client.post(
#         "/classifier/evaluate/",
#         data=json.dumps({"input": "peer pressure", "question": "0"}),
#         content_type="application/json",
#     )
#     assert res.status_code == 400
#     assert res.json == {"mentor": ["required field"]}


# def test_returns_400_response_when_input_not_set(client):
#     res = client.post(
#         "/classifier/evaluate/",
#         data=json.dumps({"mentor": "q1", "question": "0"}),
#         content_type="application/json",
#     )
#     assert res.status_code == 400
#     assert res.json == {"input": ["required field"]}


# def test_returns_404_response_with_no_question_available_with_no_config_data(client):
#     res = client.post(
#         "/classifier/evaluate/",
#         data=json.dumps({"mentor": "doesNotExist", "input": "peer pressure"}),
#         content_type="application/json",
#     )
#     assert res.status_code == 404
#     assert res.json == {
#         "message": "No models found for mentor doesNotExist. Config data is required"
#     }


# @pytest.mark.parametrize(
#     "input_mentor, input_answer, input_question, config_data, expected_results",
#     [
#         # (
#         #     "doesNotExist",
#         #     "peer pressure can change your behavior",
#         #     0,
#         #     {
#         #         "question": "What are the challenges to demonstrating integrity in a group?",
#         #         "questions": [
#         #             {
#         #                 "ideal": "Peer pressure can cause you to allow inappropriate behavior"
#         #             }
#         #         ],
#         #     },
#         #     [QuestionPIPELINEResult(question=0, score=0.0, evaluation="Bad")],
#         # ),
#         (
#             "doesNotExist",
#             "they need sunlight",
#             -1,
#             {
#                 "question": "how can i grow better plants?",
#                 "questions": [
#                     {"ideal": "give them the right amount of water"},
#                     {"ideal": "they need sunlight"},
#                 ],
#             },
#             [
#                 QuestionPIPELINEResult(question=0, evaluation="Bad", score=0.02),
#                 QuestionPIPELINEResult(question=1, evaluation="Good", score=1.0),
#             ],
#         )
#     ],
# )
# def test_evaluate_with_no_question_available_with_config_data(
#     client, input_mentor, input_answer, input_question, config_data, expected_results
# ):
#     res = client.post(
#         "/classifier/evaluate/",
#         data=json.dumps(
#             {
#                 "mentor": input_mentor,
#                 "input": input_answer,
#                 "question": input_question,
#                 "config": config_data,
#             }
#         ),
#         content_type="application/json",
#     )
#     assert res.status_code == 200
#     assert res.json["version"]["modelId"] == "default"
#     results = res.json["output"]["questionResults"]
#     assert len(results) == len(expected_results)
#     for res, res_expected in zip(results, expected_results):
#         assert res["question"] == res_expected.question
#         assert round(float(res["score"]), 2) == res_expected.score
#         assert res["evaluation"] == res_expected.evaluation


# @pytest.mark.parametrize(
#     "input_mentor,input_answer,input_question,config_data,expected_results,expected_sa_results",
#     [
#         (
#             "q1",
#             "peer pressure can change your behavior",
#             0,
#             {},
#             [QuestionPIPELINEResult(question=0, score=0.99, evaluation="Good")],
#             {
#                 "metacognitive": SpeechActPIPELINEResult(evaluation="Bad", score=0),
#                 "profanity": SpeechActPIPELINEResult(evaluation="Bad", score=0),
#             },
#         ),
#         (
#             "q1",
#             "peer pressure can change your behavior",
#             -1,
#             {},
#             [
#                 QuestionPIPELINEResult(question=0, score=0.99, evaluation="Good"),
#                 QuestionPIPELINEResult(question=1, score=0.50, evaluation="Bad"),
#                 QuestionPIPELINEResult(question=2, score=0.57, evaluation="Bad"),
#             ],
#             {
#                 "metacognitive": SpeechActPIPELINEResult(evaluation="Bad", score=0),
#                 "profanity": SpeechActPIPELINEResult(evaluation="Bad", score=0),
#             },
#         ),
#         (
#             "q1",
#             "I dont know what you are talking about",
#             0,
#             {},
#             [QuestionPIPELINEResult(question=0, score=0.86, evaluation="Bad")],
#             {
#                 "metacognitive": SpeechActPIPELINEResult(evaluation="Good", score=1),
#                 "profanity": SpeechActPIPELINEResult(evaluation="Bad", score=0),
#             },
#         ),
#     ],
# )
# def test_evaluate_classifies_user_questions(
#     client,
#     input_mentor,
#     input_answer,
#     input_question,
#     config_data,
#     expected_results,
#     expected_sa_results,
# ):
#     res = client.post(
#         "/classifier/evaluate/",
#         data=json.dumps(
#             {
#                 "mentor": input_mentor,
#                 "input": input_answer,
#                 "question": input_question,
#                 "config": config_data,
#             }
#         ),
#         content_type="application/json",
#     )
#     assert res.json["version"]["modelId"] == input_mentor
#     speech_acts = res.json["output"]["speechActs"]
#     assert (
#         speech_acts["metacognitive"]["evaluation"]
#         == expected_sa_results["metacognitive"].evaluation
#     )
#     assert (
#         speech_acts["metacognitive"]["score"]
#         == expected_sa_results["metacognitive"].score
#     )
#     assert (
#         speech_acts["profanity"]["evaluation"]
#         == expected_sa_results["profanity"].evaluation
#     )
#     assert speech_acts["profanity"]["score"] == expected_sa_results["profanity"].score
#     results = res.json["output"]["questionResults"]
#     assert len(results) == len(expected_results)
#     for res, res_expected in zip(results, expected_results):
#         assert res["question"] == res_expected.question
#         assert round(float(res["score"]), 2) == res_expected.score
#         assert res["evaluation"] == res_expected.evaluation
