#!/usr/bin/env bash
# One-command local setup: venv, pinned dependencies, and .env template.
set -euo pipefail

if [ ! -f .env ]; then
  cp .env.example .env
  echo "INFO: Created .env from .env.example - set BREATHE_API_KEY and MYSQL_PASSWORD."
else
  echo "INFO: .env already exists - leaving it untouched."
fi

python3 -m venv venv
. venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-dev.txt

echo "INFO: Setup complete."
echo "Next: sudo -E ./projectinitdb.sh"
echo "Then: ./breathe.py --dry-run"
