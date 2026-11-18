#!/usr/bin/env python3
"""Fetch Breathe sensor metadata and load it into the local MySQL staging table."""

import argparse
import logging
import logging.handlers
import sys
from datetime import datetime, timezone

import requests
import sqlalchemy as db
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import get_config

logger = logging.getLogger(__name__)

# Column definitions mirror the existing breathe_staging table.
COLUMNS = [
    ("SiteCode", db.String(255)),
    ("SiteName", db.String(255)),
    ("DeviceCode", db.String(255)),
    ("InstallationCode", db.String(255)),
    ("Facility", db.String(255)),
    ("Latitude", db.Float),
    ("Longitude", db.Float),
    ("Borough", db.String(255)),
    ("SiteClassification", db.String(255)),
    ("SensorHeightAboveGround", db.Float),
    ("DistanceToKerb", db.Float),
    ("SponsorName", db.String(255)),
    ("SiteLocationType", db.String(255)),
    ("StartDate", db.DateTime),
    ("EndDate", db.DateTime),
    ("PowerTag", db.String(255)),
    ("SiteDescription", db.Text),
    ("SitePhotoURL", db.String(255)),
    ("SensorContract", db.String(255)),
]


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.handlers.RotatingFileHandler(
                "breathe.log", maxBytes=5_000_000, backupCount=3
            ),
        ],
    )


def fetch_sensors(cfg) -> list:
    """Fetch ListSensors with retries and a bounded timeout."""
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    with requests.Session() as session:
        session.headers.update({"X-API-KEY": cfg.breathe_api_key})
        session.mount("https://", HTTPAdapter(max_retries=retries))
        response = session.get(
            cfg.breathe_url_root + "ListSensors", timeout=(5, 30)
        )
        response.raise_for_status()
        data = response.json()

    if not isinstance(data, list):
        raise ValueError("Expected a JSON list from ListSensors")
    return data


def parse_timestamp(value, site_code: str, field: str):
    """Parse ISO-8601 timestamps into naive UTC, tolerating bad/missing values."""
    if not value:
        return None
    try:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except (ValueError, TypeError):
        logger.warning("Unparseable %s for %s: %r", field, site_code, value)
        return None


def transform(sensors: list) -> list:
    """Map API records onto staging-table rows, skipping invalid records."""
    rows = []
    for sensor in sensors:
        if not isinstance(sensor, dict):
            logger.warning("Skipping non-object record: %r", sensor)
            continue
        site_code = sensor.get("SiteCode")
        if not site_code:
            logger.warning("Skipping record with no SiteCode")
            continue

        row = {}
        for name, _ in COLUMNS:
            if name in ("StartDate", "EndDate"):
                row[name] = parse_timestamp(sensor.get(name), site_code, name)
            else:
                row[name] = sensor.get(name)
        rows.append(row)
    return rows


def load(engine, rows: list) -> None:
    """Replace the staging snapshot atomically, so reruns never duplicate rows."""
    metadata = db.MetaData()
    table = db.Table(
        "breathe_staging",
        metadata,
        *(db.Column(name, col_type) for name, col_type in COLUMNS),
    )
    metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(db.delete(table))
        conn.execute(db.insert(table), rows)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="fetch and validate data without writing to the database",
    )
    args = parser.parse_args(argv)

    setup_logging()
    try:
        cfg = get_config()
        logger.info("DB target: %s", cfg.safe_summary())

        sensors = fetch_sensors(cfg)
        rows = transform(sensors)
        if not rows:
            raise RuntimeError(
                "No valid sensor records returned; refusing to replace staging data"
            )
        logger.info("Fetched %d valid sensor records", len(rows))

        if args.dry_run:
            for row in rows[:5]:
                logger.info("Dry run - would load %s / %s", row["SiteCode"], row["DeviceCode"])
            logger.info("Dry run complete; no database changes made")
            return 0

        engine = db.create_engine(cfg.database_url())
        load(engine, rows)
        logger.info("Loaded %d records into breathe_staging", len(rows))
        return 0
    except Exception:
        logger.exception("Pipeline failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
