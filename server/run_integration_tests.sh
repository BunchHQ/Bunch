#!/usr/bin/env bash

uv run --env-file=.env manage.py test tests.integration.test_clerk_auth -v 2
