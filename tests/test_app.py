import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client(reset_activities):
    """Return a TestClient instance with reset activities state."""
    return TestClient(app)


def test_root_redirect(client):
    """Test that GET / redirects to /static/index.html"""
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert expected_location in response.headers.get("location", "")


def test_get_activities_returns_dict(client):
    """Test that GET /activities returns a dictionary with activities"""
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Verify structure of an activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity


def test_signup_new_participant(client):
    """Test that signing up a new participant adds them to the activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )

    # Read the updated activity state before asserting the result.
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]
    assert activities_response.status_code == 200
    activities = activities_response.json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate_email(client):
    """Test that signing up the same email twice returns 400"""
    # Arrange
    email = "duplicate@mergington.edu"
    activity = "Basketball Team"

    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client):
    """Test that signing up for a nonexistent activity returns 404"""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonexistentActivity"

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_delete_participant(client):
    """Test that deleting an existing participant removes them"""
    # Arrange
    email = "student@mergington.edu"
    activity = "Tennis Club"

    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )

    # Act
    response = client.delete(
        f"/activities/{activity}/participants/{email}"
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert email in data["message"]
    assert activity in data["message"]


def test_delete_nonexistent_participant(client):
    """Test that deleting a non-member returns 404"""
    # Arrange
    email = "nonmember@mergington.edu"
    activity = "Drama Club"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "not signed up" in data["detail"]


def test_delete_nonexistent_activity(client):
    """Test that deleting from a nonexistent activity returns 404"""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonexistentActivity"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]
