#!/usr/bin/env bash
celery --app mentor_pipeline_tasks.tasks.celery worker --loglevel=INFO
