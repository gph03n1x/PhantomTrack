#!/usr/bin/env bash

alembic upgrade head
python -m core.app