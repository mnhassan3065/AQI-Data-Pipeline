# AQI Data Pipeline

Small Python pipeline that pulls sensor metadata from the Breathe London API
into a local MySQL database, plus a Flask endpoint for reading it back.

This is currently a **local-only** project: everything it needs is configured
through a `.env` file in this directory. No cloud account is required.

## Configuration

**No credentials are stored in this repository.** Every setting is read from
the environment, and for local development those values live in `.env`, which
is gitignored.

```sh
cp .env.example .env
$EDITOR .env
```

`.env.example` (committed) documents the variables:

| Variable | Purpose |
| --- | --- |
| `BREATHE_API_KEY` | Breathe API key (**required** — needed to fetch data) |
| `BREATHE_URL_ROOT` | API base URL, trailing `/` (not secret) |
| `MYSQL_HOST`, `MYSQL_PORT` | MySQL connection details |
| `MYSQL_DATABASE` | Database name (default `airquality`) |
| `MYSQL_USER` | Database user |
| `MYSQL_PASSWORD` | Database password (**secret**) |
| `MYSQL_ROOT_PASSWORD` | Docker Compose only: MySQL root password |
| `FLASK_HOST`, `FLASK_DEBUG` | Web server binding / debug toggle |

You need a valid Breathe API key from your API provider to test the core
functionality. Put it in `.env` as `BREATHE_API_KEY` — the app will refuse to
start without it.

Notes:

- `.env`, `.env.*` (except `.env.example`), `project.ini`, `*.log`,
  `listsensors.raw.json*` and `venv/` are all gitignored.
- `projectinitdb.sql` is a **template**; the shell script substitutes values
  from `.env` and escapes them before running the SQL.
- Neither app logs the DB connection string, and SQLAlchemy `echo` is off.

## Local setup

Requires Python 3, `pip`, and a running MySQL server.

Quickest path — creates the venv, installs pinned dependencies and creates
`.env` from the template if it doesn't exist:

```sh
./setup.sh
$EDITOR .env
```

Or do it manually:

```sh
python3 -m venv venv
. venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-dev.txt
```

Initialise the database (needs MySQL root, reads credentials from `.env`):

```sh
sudo -E ./projectinitdb.sh
```

Run the pipeline and the read-only web API:

```sh
./breathe.py --dry-run   # fetch/validate only, no database writes
./breathe.py             # or: ./breathe.sh
./project-bottle.py      # serves http://127.0.0.1:8080/listsensors
```

Endpoints: `/listsensors` returns a JSON array of staging rows, `/health`
reports database connectivity, and static pages are at
`http://127.0.0.1:8080/static/index.html` and `.../static/testtable.html`.

Each successful run **replaces** the contents of `breathe_staging`, so reruns
do not create duplicate rows. If the API returns no valid records, the table is
left untouched.

The shell wrappers (`breathe.sh`, `project-bottle.sh`) still support `-i` to
create the venv and install dependencies, and `-h` for usage.

`curltest.sh` is a quick API smoke test; it writes to `listsensors.raw.json`
(gitignored).

## Tests

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```

The tests use SQLite and mocks — no live API key or MySQL server needed.

## CI

`.github/workflows/ci.yml` runs on pushes and pull requests to `main`: syntax
check, `ruff`, `pytest`, `pip-audit`, and a check that no key or `.env` file is
tracked. It needs no secrets.

## Docker Compose (optional)

Runs MySQL 8 and the API in containers; no local MySQL install or `sudo`
needed. Copy and edit `.env` first.

```sh
docker compose up --build          # API on http://127.0.0.1:8080
docker compose --profile pipeline run --rm pipeline   # load sensor data
docker compose down                # stop; add -v to delete the DB volume
```

The MySQL container creates the user/database itself using `MYSQL_USER`,
`MYSQL_PASSWORD` and `MYSQL_DATABASE` from `.env`. The app containers get
`MYSQL_HOST=mysql` injected; secrets are never baked into the image.

## How it fits together

1. `breathe.py` calls `ListSensors`, validates/parses the response, and
   **replaces** the `breathe_staging` table in one transaction.
2. `project-bottle.py` exposes that table read-only at `/listsensors` and
   serves the static pages.
3. `config.py` is the single source of settings; `render_sql.py` produces the
   escaped SQL used by `projectinitdb.sh`.

`sensordata-mapping.ods` is the reference spreadsheet describing the sensor
fields and how they map to the staging columns in `breathe.py` (`COLUMNS`).

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError: dotenv` | Activate the venv: `. venv/bin/activate` |
| `Missing required setting BREATHE_API_KEY` | Fill in `.env` |
| `Access denied for user 'project'` | Re-run `sudo -E ./projectinitdb.sh`; it now syncs the password |
| HTTP 403 from the API | Check the Breathe key and its restrictions |
| Connection refused | Start MySQL: `sudo systemctl start mysql` |
