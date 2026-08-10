from fastapi import status
from urllib.parse import quote


def get_activity_participants(client, activity_name):
    response = client.get("/activities")
    assert response.status_code == status.HTTP_200_OK
    activities = response.json()
    return activities[activity_name]["participants"]


def encode_path_segment(value: str) -> str:
    return quote(value, safe="")


def test_get_activities_returns_activity_list(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    activities = response.json()
    assert isinstance(activities, dict)
    assert expected_activity in activities
    assert "participants" in activities[expected_activity]
    assert isinstance(activities[expected_activity]["participants"], list)


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent+signup@mergington.edu"
    participants = get_activity_participants(client, activity_name)
    if email in participants:
        client.delete(
            f"/activities/{encode_path_segment(activity_name)}/participants?email={quote(email, safe='')}"
        )

    # Act
    response = client.post(
        f"/activities/{encode_path_segment(activity_name)}/signup?email={quote(email, safe='')}"
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["message"] == f"Signed up {email} for {activity_name}"

    participants = get_activity_participants(client, activity_name)
    assert email in participants

    # Cleanup
    delete_response = client.delete(
        f"/activities/{encode_path_segment(activity_name)}/participants?email={quote(email, safe='')}"
    )
    assert delete_response.status_code == status.HTTP_200_OK


def test_delete_participant_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent+delete@mergington.edu"
    if email not in get_activity_participants(client, activity_name):
        signup_response = client.post(
            f"/activities/{encode_path_segment(activity_name)}/signup?email={quote(email, safe='')}"
        )
        assert signup_response.status_code == status.HTTP_200_OK

    # Act
    response = client.delete(
        f"/activities/{encode_path_segment(activity_name)}/participants?email={quote(email, safe='')}"
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["message"] == f"Removed {email} from {activity_name}"
    participants = get_activity_participants(client, activity_name)
    assert email not in participants
