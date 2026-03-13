"""
conftest.py — Shared pytest fixtures for the AI Resume Analyzer test suite.
Provides a Flask test client and an in-memory SQLite database that is
created fresh for every test session and torn down automatically.
"""
import pytest
from flask import Flask
from models import db as _db, AnalysisResult, RankingBatch, RankingResult


@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing with in-memory SQLite."""
    test_app = Flask(__name__, template_folder="../templates")
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-secret",
        "WTF_CSRF_ENABLED": False,
    })

    _db.init_app(test_app)
    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope="function")
def db_session(app):
    """Wrap each test in a transaction and roll it back after the test."""
    with app.app_context():
        yield _db
        _db.session.rollback()
