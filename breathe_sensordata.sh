#!/usr/bin/bash

PYTHONSCRIPT=${0%.sh}.py

setupVenv() {
  set -uxo pipefail
  python3 -m venv venv
  source venv/bin/activate
}

usage() {
  echo "Usage: $0 [-h|-i]"
  echo "h: Show this message"
  echo "Description:"
  echo "Wrapper script for launching ${PYTHONSCRIPT} in python virtual environment"
  exit 0
}

while getopts h flag
do
  case "${flag}" in
     h)
       usage
       ;;
     *)
       usage
       ;;
  esac
done

setupVenv

# Launch the App

echo "INFO: Launching ${PYTHONSCRIPT}..."

python3 ${PYTHONSCRIPT}


