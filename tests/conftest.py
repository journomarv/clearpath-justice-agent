"""Shared pytest fixtures."""
import os

import pytest
from fastapi.testclient import TestClient

# Ensure a predictable (but fake) config for tests, set before app import.
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key-not-real")
os.environ.setdefault("ENVIRONMENT", "development")


@pytest.fixture
def client():
    from app.main import app

    return TestClient(app)
