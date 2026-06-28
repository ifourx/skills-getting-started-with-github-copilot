"""Tests for the Mergington High School API endpoints.

All tests follow the AAA (Arrange-Act-Assert) pattern with explicit comments.
"""


class TestRootRedirect:
    def test_root_redirects_to_index(self, client):
        # Arrange — no special setup needed
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in (302, 307, )
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    def test_returns_all_activities(self, client):
        # Arrange — rely on default activities from conftest reset
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_has_required_fields(self, client):
        # Arrange — rely on default activities from conftest reset
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        for name, details in data.items():
            assert "description" in details, f"{name} missing 'description'"
            assert "schedule" in details, f"{name} missing 'schedule'"
            assert "max_participants" in details, f"{name} missing 'max_participants'"
            assert "participants" in details, f"{name} missing 'participants'"


class TestSignup:
    def test_signup_success(self, client):
        # Arrange
        activity_name = "Soccer Club"
        email = "teststudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        # Verify side effect — student appears in participants
        verify = client.get("/activities")
        participants = verify.json()[activity_name]["participants"]
        assert email in participants

    def test_signup_activity_not_found(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_signup_already_registered(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already a participant

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Student already signed up for this activity"
        }


class TestUnregister:
    def test_unregister_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # existing participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Removed {email} from {activity_name}"
        }
        # Verify side effect — student no longer in participants
        verify = client.get("/activities")
        participants = verify.json()[activity_name]["participants"]
        assert email not in participants

    def test_unregister_activity_not_found(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_unregister_not_registered(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Student not registered for this activity"
        }
