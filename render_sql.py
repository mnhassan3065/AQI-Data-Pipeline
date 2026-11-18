"""Render projectinitdb.sql from environment variables with safe escaping."""

import os
import sys
from pathlib import Path


def sql_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def sql_identifier(value: str) -> str:
    return "`" + value.replace("`", "``") + "`"


def render(template_path: str, user: str, password: str, database: str) -> str:
    template = Path(template_path).read_text()
    return template % {
        "user": sql_string(user),
        "password": sql_string(password),
        "database": sql_identifier(database),
    }


if __name__ == "__main__":
    print(
        render(
            sys.argv[1],
            os.environ["MYSQL_USER"],
            os.environ["MYSQL_PASSWORD"],
            os.environ["MYSQL_DATABASE"],
        )
    )
