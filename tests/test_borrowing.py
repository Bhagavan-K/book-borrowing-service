import pytest
from fastapi.testclient import TestClient

def test_borrow_available_book(client, test_data):
    response = client.post(
        "/api/borrowings/borrow",
        headers={"Authorization": f"Bearer {test_data['users']['user1']['token']}"},
        json={
            "user_id": test_data['users']['user1']['id'],
            "book_id": test_data['books']['book2']['_id']
        }
    )
    assert response.status_code == 200
    assert response.json()["book_id"] == test_data['books']['book2']['_id']
    assert response.json()["status"] == "ACTIVE"

def test_borrow_already_borrowed_book(client, test_data):
    response = client.post(
        "/api/borrowings/borrow",
        headers={"Authorization": f"Bearer {test_data['users']['user1']['token']}"},
        json={
            "user_id": test_data['users']['user1']['id'],
            "book_id": test_data['books']['book1']['_id']
        }
    )
    assert response.status_code == 400
    assert "not available" in response.json()["detail"].lower()

def test_get_user_borrowings(client, test_data):
    response = client.get(
        f"/api/borrowings/user/{test_data['users']['user1']['id']}/borrowings",
        headers={"Authorization": f"Bearer {test_data['users']['user1']['token']}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_book_history(client, test_data):
    response = client.get(
        f"/api/borrowings/book/{test_data['books']['book1']['_id']}/history",
        headers={"Authorization": f"Bearer {test_data['users']['admin']['token']}"}
    )
    assert response.status_code == 200