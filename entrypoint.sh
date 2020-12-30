#! /usr/bin/env bash

pipenv run python load_test_fixtures.py
pipenv run uvicorn main:app --host 0.0.0.0 --port 8000