#!/usr/bin/env bash
# Quick API smoke test. Reads credentials from .env / the environment.
set -euo pipefail

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

: "${LONAQN_URL_ROOT:?Set LONAQN_URL_ROOT in .env or the environment}"

url_root="${LONAQN_URL_ROOT%/}"

#out_file="/tmp/listsensors.lonaqn.raw.json"
#curl --insecure -X GET "${url_root}/Information/MonitoringSites/GroupName=London/Json" -H "Content-Type: application/json" > ${out_file}

#out_file="sensorsdata.lonaqn.raw.json"

#curl --insecure -X GET "${url_root}/Daily/MonitoringIndex/Latest/GroupName=London/Json" -H "Content-Type: application/json" > ${out_file}

#curl --insecure -X GET "${url_root}/Data/Site/SiteCode=BQ7/StartDate=01-10-2026/EndDate=29-10-2026/Json" -H "Content-Type: application/json" > ${out_file}

#out_file="/tmp/sensorsdata.lonaqn.raw.json"
#curl --insecure -X GET "${url_root}/Data/Wide/Site/SiteCode=BQ7/StartDate=01-10-2026/EndDate=29-10-2026/Json" -H "Content-Type: application/json" > sensorsdata.lonaqn.raw.json

out_file="/tmp/sensorsdata.lonaqn.raw.xml"
curl --insecure -X GET "${url_root}/Data/Wide/Site/SiteCode=BQ7/StartDate=01-10-2026/EndDate=29-10-2026" -H "Content-Type: application/json" > ${out_file}

