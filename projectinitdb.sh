#!/usr/bin/env bash
# Initialise the local MySQL database using credentials from .env / environment.
set -euo pipefail

if [ "$EUID" -ne 0 ] ; then
    echo "ERROR: This script must be run as root."
    exit 1
fi

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

: "${MYSQL_USER:?Set MYSQL_USER in .env or the environment}"
: "${MYSQL_PASSWORD:?Set MYSQL_PASSWORD in .env or the environment}"
: "${MYSQL_DATABASE:?Set MYSQL_DATABASE in .env or the environment}"

INITDBSCRIPT="projectinitdb.sql"

echo "INFO: Setting up project database"
echo "INFO: Using script: ${INITDBSCRIPT}"

# Render the template with properly escaped SQL literals / identifiers so the
# password never appears in the shell command line or in the repository.
python3 render_sql.py "$INITDBSCRIPT" | mysql -u root -p

echo "INFO: Done."
