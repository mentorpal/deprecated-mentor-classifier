#!/usr/bin/env bash
celery --app mentor_classifier_tasks.tasks.celery worker --loglevel=INFO
