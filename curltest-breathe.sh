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

#out_file="tmp/listsensors.raw.json"
#curl --insecure -X GET "${url_root}/ListSensors" -H "Content-Type: application/json" -H "X-API-KEY: ${BREATHE_API_KEY}" > ${out_file}

out_file="tmp/sensordata.raw.json"
curl --insecure -X GET "${url_root}/SensorData" -H "Content-Type: application/json" -H "X-API-KEY: ${BREATHE_API_KEY}" > ${out_file}

echo "INFO: Response written to ${out_file}"

