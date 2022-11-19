#!/bin/bash
set -eox pipefail

python3 manage.py wait_db

exec $*
