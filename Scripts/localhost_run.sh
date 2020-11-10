#!/bin/bash
#localhost_run.sh

source venv/bin/activate
export FLASK_APP=App.py
export FLASK_ENV=development
export FLASK_DEBUG=0

flask run
