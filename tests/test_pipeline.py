from datetime import datetime
from unittest.mock import MagicMock

import pytest
import sqlalchemy as db

import breathe
import config
import render_sql


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in (
        "BREATHE_API_KEY", "MYSQL_PASSWORD", "BREATHE_URL_ROOT",
        "MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_DATABASE",
        "FLASK_HOST", "FLASK_DEBUG",
    ):
        monkeypatch.delenv(key, raising=False)
    config.get_config.cache_clear()
    yield
    config.get_config.cache_clear()


def test_config_requires_api_key(monkeypatch):
    monkeypatch.setenv("MYSQL_PASSWORD", "pw")
    with pytest.raises(RuntimeError, match="BREATHE_API_KEY"):
        config.get_config()


def test_config_requires_db_password(monkeypatch):
    monkeypatch.setenv("BREATHE_API_KEY", "key")
    with pytest.raises(RuntimeError, match="MYSQL_PASSWORD"):
        config.get_config()


def test_config_normalises_url_and_hides_password(monkeypatch):
    monkeypatch.setenv("BREATHE_API_KEY", "key")
    monkeypatch.setenv("MYSQL_PASSWORD", "hunter2")
    monkeypatch.setenv("BREATHE_URL_ROOT", "https://example.test/api")
    cfg = config.get_config()

    assert cfg.breathe_url_root == "https://example.test/api/"
    assert "hunter2" not in cfg.safe_summary()
    rendered = cfg.database_url().render_as_string(hide_password=True)
    assert "hunter2" not in rendered
    assert "***" in rendered


def test_fetch_sensors_validates_response(monkeypatch):
    response = MagicMock()
    response.json.return_value = {"not": "a list"}
    session = MagicMock()
    session.__enter__.return_value = session
    session.get.return_value = response
    monkeypatch.setattr(breathe.requests, "Session", lambda: session)
    cfg = MagicMock(breathe_api_key="key", breathe_url_root="https://x/")

    with pytest.raises(ValueError, match="JSON list"):
        breathe.fetch_sensors(cfg)
    session.get.assert_called_once_with("https://x/ListSensors", timeout=(5, 30))


def test_transform_parses_dates_and_skips_invalid():
    rows = breathe.transform([
        {
            "SiteCode": "A",
            "StartDate": "2024-01-02T03:04:05Z",
            "EndDate": "not-a-date",
        },
        {"SiteCode": ""},
        "not a dict",
    ])

    assert len(rows) == 1
    assert rows[0]["StartDate"] == datetime(2024, 1, 2, 3, 4, 5)
    assert rows[0]["EndDate"] is None


def test_load_replaces_snapshot():
    engine = db.create_engine("sqlite:///:memory:")

    breathe.load(engine, breathe.transform([{"SiteCode": "A"}]))
    breathe.load(engine, breathe.transform([{"SiteCode": "B"}]))

    with engine.connect() as conn:
        codes = [row[0] for row in conn.execute(db.text("SELECT SiteCode FROM breathe_staging"))]
    assert codes == ["B"]


def test_render_sql_escapes_quotes_and_identifiers(tmp_path):
    template = tmp_path / "t.sql"
    template.write_text("U=%(user)s P=%(password)s D=%(database)s")

    out = render_sql.render(str(template), "o'brien", "p'x", "air`quality")

    assert "o''brien" in out
    assert "'p''x'" in out
    assert "`air``quality`" in out
