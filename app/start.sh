#! /usr/bin/env bash

# fastapi 시작 스크립트
python ./ready.py
uvicorn main:app --port 8000 --host 0.0.0.0 --reload