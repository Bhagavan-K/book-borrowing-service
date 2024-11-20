import pytest

def test_create_reservation_for_borrowed_book(client, test_data):
    response = client.post(
        "/api/reservations/create",
        headers={"Authorization": f"Bearer {test_data['users']['user2']['token']}"},
        json={
            "user_id": test_data['users']['user2']['id'],
            "book_id": test_data['books']['book1']['_id']
        }
    )
    assert response.status_code == 200
    assert response.json()["book_id"] == test_data['books']['book1']['_id']
    assert response.json()["status"] == "WAITING"

def test_create_reservation_for_available_book(client, test_data):
    response = client.post(
        "/api/reservations/create",
        headers={"Authorization": f"Bearer {test_data['users']['user2']['token']}"},
        json={
            "user_id": test_data['users']['user2']['id'],
            "book_id": test_data['books']['book2']['_id']
        }
    )
    assert response.status_code == 400
    assert "can only reserve borrowed books" in response.json()["detail"].lower()

def test_get_reservation_queue(client, test_data):
    response = client.get(
        f"/api/reservations/queue/{test_data['books']['book1']['_id']}",
        headers={"Authorization": f"Bearer {test_data['users']['user1']['token']}"}
    )
    assert response.status_code == 200
    assert "queue" in response.json()