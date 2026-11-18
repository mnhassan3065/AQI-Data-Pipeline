# AQI Data Pipeline

Small Python pipeline that pulls sensor metadata from the Breathe London API
into a local MySQL database, plus a Flask endpoint for reading it back.

## ⚠️ Before you push: rotate the exposed API key

An API key (`AIzaSy...`) was previously hardcoded in `curltest.sh`. It has been
removed from the code, but it must be considered compromised:

1. Go to **Google Cloud Console → APIs & Services → Credentials**.
2. **Delete / rotate** that key and create a new one (restrict it by API and,
   if possible, by IP).
3. Put the new key in your local `.env` (see below) and in GitHub Secrets if
   you add CI later.

Do not reuse the old key anywhere. If this repository was ever published or
shared with that file present, treat the key as leaked.

## Secrets and configuration

**No credentials are stored in this repository.** Every secret is read from
environment variables. Locally those live in `.env`, which is gitignored.

```sh
cp .env.example .env
$EDITOR .env          # fill in BREATHE_API_KEY and MYSQL_PASSWORD
```

`.env.example` (committed) documents the variables:

| Variable | Purpose |
| --- | --- |
| `BREATHE_API_KEY` | Breathe API key (**secret**) |
| `BREATHE_URL_ROOT` | API base URL, trailing `/` (not secret) |
| `MYSQL_HOST`, `MYSQL_PORT` | MySQL connection details |
| `MYSQL_DATABASE` | Database name (default `airquality`) |
| `MYSQL_USER` | Database user |
| `MYSQL_PASSWORD` | Database password (**secret**) |
| `FLASK_HOST`, `FLASK_DEBUG` | Web server binding / debug toggle |

Rules:

- `.env`, `.env.*` (except `.env.example`), `project.ini`, `*.log`,
  `listsensors.raw.json*` and `venv/` are all gitignored.
- `projectinitdb.sql` is a **template**; the shell script substitutes values
  from `.env` and escapes them before running the SQL.
- Neither app logs the DB connection string, and SQLAlchemy `echo` is off.
- If you add GitHub Actions / deployment later, store these values in
  **Settings → Secrets and variables → Actions** (or in an Environment's
  secrets) and never write them into a workflow file. Enable **secret
  scanning** and **push protection** in the repo settings as well.

## Local setup

Requires Python 3, `pip`, and a running MySQL server.

```sh
python3 -m venv venv
. venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Initialise the database (needs MySQL root, reads credentials from `.env`):

```sh
sudo -E ./projectinitdb.sh
```

Run the pipeline and the read-only web API:

```sh
./breathe.py          # or: ./breathe.sh
./project-bottle.py   # serves http://127.0.0.1:8080/listsensors
```

The shell wrappers (`breathe.sh`, `project-bottle.sh`) still support `-i` to
create the venv and install dependencies, and `-h` for usage.

`curltest.sh` is a quick API smoke test; it writes to `listsensors.raw.json`
(gitignored).

## Pushing to a new **private** GitHub repository

From this directory, once you are happy with the files:

```sh
git init -b main
git add .
git commit -m "Initial commit: AQI data pipeline"
git remote add origin git@github.com:<your-username>/<repo-name>.git
git push -u origin main
```

Create the repo on GitHub first via **New repository → Private**, and leave
"Add a README / .gitignore / license" unchecked since those files already
exist here. Then add `BREATHE_API_KEY` and `MYSQL_PASSWORD` under
**Settings → Secrets and variables** if any workflow or deployment needs them.
