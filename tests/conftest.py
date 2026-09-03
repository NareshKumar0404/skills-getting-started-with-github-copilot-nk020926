import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Return a TestClient instance for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture to save and restore the original activities state.
    This ensures no test pollutes the in-memory data for the next test.
    """
    import copy
    original_activities = copy.deepcopy(activities)
    yield
    # Restore the original state after the test
    activities.clear()
    activities.update(original_activities)
