#!/usr/bin/python3
"""Read-only web API for the local AQI staging table."""

import logging
import logging.handlers
import sys

import sqlalchemy as db
from flask import Flask, jsonify
from sqlalchemy.exc import SQLAlchemyError

from config import get_config

app = Flask(__name__)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler(
            "project-bottle.log", maxBytes=5_000_000, backupCount=3
        ),
    ],
)

cfg = get_config()
engine = db.create_engine(cfg.database_url())
logger.info("DB target: %s", cfg.safe_summary())


def staging_table(conn):
    """Reflect the table on demand so import does not require a live DB."""
    metadata = db.MetaData()
    metadata.reflect(bind=conn, only=["breathe_staging"])
    return metadata.tables["breathe_staging"]


@app.route("/hello")
def hello():
    return "Hello World!"


@app.route("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(db.text("SELECT 1"))
        return jsonify(status="ok")
    except SQLAlchemyError:
        logger.exception("Database health check failed")
        return jsonify(status="unavailable"), 503


@app.route("/listsensors")
def listsensors():
    try:
        # A fresh connection per request - SQLAlchemy connections are not
        # safe to share across Flask's worker threads.
        with engine.connect() as conn:
            rows = conn.execute(staging_table(conn).select()).mappings().all()
        return jsonify([dict(row) for row in rows])
    except SQLAlchemyError:
        logger.exception("Failed to read sensor data")
        return jsonify(error="Could not read sensor data"), 500


if __name__ == "__main__":
    logger.info("Starting web server on %s:8080", cfg.flask_host)
    app.run(host=cfg.flask_host, port=8080, debug=cfg.flask_debug)
