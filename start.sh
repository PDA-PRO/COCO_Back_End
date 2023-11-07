#! /usr/bin/env bash

# fastapi 시작 스크립트
python -m app.ready
uvicorn app.main:app --port 8000 --host 0.0.0.0