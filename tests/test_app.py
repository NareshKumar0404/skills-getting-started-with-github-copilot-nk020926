import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client(reset_activities):
    """Return a TestClient instance with reset activities state."""
    return TestClient(app)


def test_root_redirect(client):
    """Test that GET / redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers.get("location", "")


def test_get_activities_returns_dict(client):
    """Test that GET /activities returns a dictionary with activities"""
    response = client.get("/activities")
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
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]


def test_signup_duplicate_email(client):
    """Test that signing up the same email twice returns 400"""
    email = "duplicate@mergington.edu"
    activity = "Basketball Team"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/{activity}/signup?email={email}",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        f"/activities/{activity}/signup?email={email}",
        params={"email": email}
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client):
    """Test that signing up for a nonexistent activity returns 404"""
    email = "test@mergington.edu"
    activity = "NonexistentActivity"
    
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        params={"email": email}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_delete_participant(client):
    """Test that deleting an existing participant removes them"""
    email = "student@mergington.edu"
    activity = "Tennis Club"
    
    # First, sign up the participant
    response1 = client.post(
        f"/activities/{activity}/signup?email={email}",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Then, delete the participant
    response2 = client.delete(
        f"/activities/{activity}/participants/{email}"
    )
    
    assert response2.status_code == 200
    data = response2.json()
    assert email in data["message"]
    assert activity in data["message"]


def test_delete_nonexistent_participant(client):
    """Test that deleting a non-member returns 404"""
    email = "nonmember@mergington.edu"
    activity = "Drama Club"
    
    response = client.delete(
        f"/activities/{activity}/participants/{email}"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not signed up" in data["detail"]


def test_delete_nonexistent_activity(client):
    """Test that deleting from a nonexistent activity returns 404"""
    email = "test@mergington.edu"
    activity = "NonexistentActivity"
    
    response = client.delete(
        f"/activities/{activity}/participants/{email}"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]
