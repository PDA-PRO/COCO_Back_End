#! /bin/bash

REQ_FILE_PATH="$( cd "$( dirname "$0" )" && pwd -P )"
pip install -r $REQ_FILE_PATH/$1/requirements.txt