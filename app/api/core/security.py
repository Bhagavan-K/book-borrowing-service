from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from typing import Dict
from ...core.config import settings

security = HTTPBearer()

class AuthHandler:
    # Test users - Manipulated
    def __init__(self):
        self.test_tokens = {
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsImlhdCI6MTczMTgxOTQ0OCwiZXhwIjoxNzMxODIzMDQ4fQ.-phsHzDJnDKdllMdQqEw9uiUbnzmleGHNR8kFmrkGF8": {
                "id": 1,
                "username": "test_user1",
                "email": "test1@example.com",
                "role": "user"
            }
        }
    
    async def validate_token(self, credentials: HTTPAuthorizationCredentials) -> Dict:
        if not credentials:
            raise HTTPException(status_code=401, detail="Invalid authorization credentials")
        
        token = credentials.credentials

        # MANIPULATED FOR TESTING WITHOUT ACTUAL USER AUTH SERVICE
        if token in self.test_tokens:
            return self.test_tokens[token]
            
        elif token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIsImlhdCI6MTczMTgxOTQ0OCwiZXhwIjoxNzMxODIzMDQ4fQ.dS8k0VLc-QyoMvGDQH6OxYBF7qmZvwXte9EjvuxRxtU":
            return {
                "id": 2,
                "username": "test_user2",
                "email": "test2@example.com",
                "role": "user"
            }
        elif token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMsImlhdCI6MTczMTgxOTQ0OCwiZXhwIjoxNzMxODIzMDQ4fQ.YOJ4BxzHVJNX5iIwCwxYdY1c7cj5kKhBnYB0rX5g6KQ":
            return {
                "id": 3,
                "username": "admin",
                "email": "admin@example.com",
                "role": "admin"
            }
        
        raise HTTPException(status_code=401, detail="Invalid token")

        # COMMENTED FOR MANIPULATED TESTING
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/user/validate",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 401:
                    raise HTTPException(status_code=401, detail="Invalid token or expired token")
                elif response.status_code != 200:
                    raise HTTPException(status_code=500, detail="Authentication service error")
                
                return response.json()
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Authentication service unavailable")
        """

auth_handler = AuthHandler()