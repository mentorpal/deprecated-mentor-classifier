#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os

from celery import Celery
from kombu import Exchange, Queue

from . import (
    QUEUE_TRAINING,
)

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
celery = Celery("mentor_classifier_tasks", broker=broker_url)
celery.conf.update(
    {
        "accept_content": ["json"],
        "broker_url": broker_url,
        "event_serializer": os.environ.get("CELERY_EVENT_SERIALIZER", "json"),
        "result_backend": os.environ.get(
            "CELERY_RESULT_BACKEND", "redis://redis:6379/0"
        ),
        "result_serializer": os.environ.get("CELERY_RESULT_SERIALIZER", "json"),
        "task_default_queue": QUEUE_TRAINING,
        "task_default_exchange": QUEUE_TRAINING,
        "task_default_routing_key": QUEUE_TRAINING,
        "task_queues": [
            Queue(
                QUEUE_TRAINING,
                exchange=Exchange(QUEUE_TRAINING, "direct", durable=True),
                routing_key=QUEUE_TRAINING,
            )
        ],
        "task_routes": {"mentor_classifier_tasks.tasks.*": {"queue": QUEUE_TRAINING}},
        "task_serializer": os.environ.get("CELERY_TASK_SERIALIZER", "json"),
    }
)


@celery.task()
def train_task(mentor):
    pass
