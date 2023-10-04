#! /usr/bin/env bash

# worker 시작 스크립트
python ./celery_ready.py
celery -A app.core.celery_app worker --loglevel=info -c $CELERY_CONCURRENCY