#! /usr/bin/env bash

# worker 시작 스크립트
service redis-server start
celery -A app.core.celery_app worker --loglevel=info