#!/usr/bin/env bash
# Quick API smoke test. Reads credentials from .env / the environment.
set -euo pipefail

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

: "${BREATHE_API_KEY:?Set BREATHE_API_KEY in .env or the environment}"
: "${BREATHE_URL_ROOT:?Set BREATHE_URL_ROOT in .env or the environment}"

url_root="${BREATHE_URL_ROOT%/}"

curl --fail --silent --show-error \
  -X GET "${url_root}/ListSensors" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: ${BREATHE_API_KEY}" \
  > listsensors.raw.json

echo "INFO: Response written to listsensors.raw.json"
