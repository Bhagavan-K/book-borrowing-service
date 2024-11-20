import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import asyncio
from app.main import app
from app.core.config import settings

# Test tokens
USER1_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsImlhdCI6MTczMTgxOTQ0OCwiZXhwIjoxNzMxODIzMDQ4fQ.-phsHzDJnDKdllMdQqEw9uiUbnzmleGHNR8kFmrkGF8"
USER2_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIsImlhdCI6MTczMTgxOTQ0OCwiZXhwIjoxNzMxODIzMDQ4fQ.dS8k0VLc-QyoMvGDQH6OxYBF7qmZvwXte9EjvuxRxtU"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMsImlhdCI6MTczMTgxOTQ0OCwiZXhwIjoxNzMxODIzMDQ4fQ.YOJ4BxzHVJNX5iIwCwxYdY1c7cj5kKhBnYB0rX5g6KQ"

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_data():
    return {
        "books": {
            "book1": {
                "_id": 101,
                "title": "The Hobbit",
                "author": "J.R.R. Tolkien",
                "isbn": "9780261103344"
            },
            "book2": {
                "_id": 102,
                "title": "1984",
                "author": "George Orwell",
                "isbn": "9780451524935"
            }
        },
        "users": {
            "user1": {
                "id": 1,
                "token": USER1_TOKEN
            },
            "user2": {
                "id": 2,
                "token": USER2_TOKEN
            },
            "admin": {
                "id": 3,
                "token": ADMIN_TOKEN
            }
        }
    }

@pytest.fixture
async def db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    return client[settings.DATABASE_NAME]