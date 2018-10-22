#!/usr/bin/bash

alembic upgrade head
python -m core.app