"""Tests for activity management endpoints using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Should return all activities with their details."""
        # Arrange
        expected_activity_count = 3

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_activity_count
        assert "Chess Club" in response.json()
        assert "Programming Class" in response.json()
        assert "Gym Class" in response.json()

    def test_get_activities_contains_activity_details(self, client):
        """Should return activities with all required fields."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        for activity in activities.values():
            assert all(field in activity for field in required_fields)

    def test_get_activities_shows_current_participants(self, client):
        """Should show the current list of participants for each activity."""
        # Arrange
        # Act
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]

        # Assert
        assert response.status_code == 200
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Should successfully add a new student to an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

        # Verify the participant was added
        verify = client.get("/activities")
        assert email in verify.json()[activity_name]["participants"]

    def test_signup_duplicate_email(self, client):
        """Should return 400 when student is already signed up."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_not_found(self, client):
        """Should return 404 when activity does not exist."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_preserves_other_participants(self, client):
        """Should not affect other participants when adding a new one."""
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        original_participants = client.get("/activities").json()[activity_name]["participants"].copy()

        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        updated = client.get("/activities").json()[activity_name]["participants"]
        assert all(p in updated for p in original_participants)
        assert email in updated


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """Should successfully remove a student from an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

        # Verify the participant was removed
        verify = client.get("/activities")
        assert email not in verify.json()[activity_name]["participants"]

    def test_unregister_student_not_registered(self, client):
        """Should return 400 when student is not registered for activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_activity_not_found(self, client):
        """Should return 404 when activity does not exist."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_preserves_other_participants(self, client):
        """Should not affect other participants when removing one."""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        original_participants = client.get("/activities").json()[activity_name]["participants"].copy()

        # Act
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email_to_remove})

        # Assert
        updated = client.get("/activities").json()[activity_name]["participants"]
        assert email_to_keep in updated
        assert email_to_remove not in updated

