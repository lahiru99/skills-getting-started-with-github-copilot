"""
Tests for the Mergington High School API
"""

import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "name": "Chess Club",
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "name": "Basketball Team",
            "description": "Join the team and compete in local tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Art Club": {
            "name": "Art Club",
            "description": "Explore various art techniques and create your own masterpieces",
            "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Drama Club": {
            "name": "Drama Club",
            "description": "Participate in theater productions and improve acting skills",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": []
        },
        "Debate Team": {
            "name": "Debate Team",
            "description": "Engage in debates and enhance public speaking skills",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Math Club": {
            "name": "Math Club",
            "description": "Solve challenging math problems and participate in competitions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 8
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_contains_activity_details(self, reset_activities):
        """Test that activities contain required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_participants_count(self, reset_activities):
        """Test that participants are correctly listed"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "john.doe@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "john.doe@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, reset_activities):
        """Test that signup adds participant to activity"""
        email = "john.doe@mergington.edu"
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Team"]["participants"]
    
    def test_signup_nonexistent_activity(self, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "john.doe@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, reset_activities):
        """Test signup for activity when already registered"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_times(self, reset_activities):
        """Test multiple signup attempts with different emails"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            "/activities/Basketball Team/signup",
            params={"email": email1}
        )
        response2 = client.post(
            "/activities/Basketball Team/signup",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both are registered
        response = client.get("/activities")
        data = response.json()
        assert email1 in data["Basketball Team"]["participants"]
        assert email2 in data["Basketball Team"]["participants"]


class TestUnregister:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, reset_activities):
        """Test successful unregistration"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, reset_activities):
        """Test that unregister removes participant from activity"""
        email = "michael@mergington.edu"
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "john@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self, reset_activities):
        """Test unregister when participant is not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "unknown@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_signup_then_unregister(self, reset_activities):
        """Test signup followed by unregister"""
        email = "test@mergington.edu"
        activity = "Basketball Team"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify unregistered
        response3 = client.get("/activities")
        data = response3.json()
        assert email not in data[activity]["participants"]


class TestRootRedirect:
    """Test the root endpoint redirect"""
    
    def test_root_redirect(self, reset_activities):
        """Test that root redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
