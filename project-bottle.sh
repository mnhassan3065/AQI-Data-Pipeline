#!/usr/bin/bash

setupVenv() {
  set -uxo pipefail
  python3 -m venv venv
  source venv/bin/activate
}

initVenv() {
  echo "INFO: Initializing Python Virtual Environment..."
  setupVenv

  python3 -m pip install --upgrade pip
  python3 -m pip install -r requirements.txt

  exit 0
}

usage() {
  echo "Usage: $0 [-h|-i]"
  echo "h: Show this message"
  echo "i: Initialize python virtualEnvironment"
  exit 0
}

while getopts hi flag
do
  case "${flag}" in
     i) 
       initVenv
       ;;
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

python3 ./project-bottle.py 


