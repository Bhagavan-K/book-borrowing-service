from fastapi import Header, HTTPException
from typing import Optional
import httpx
from ..core.config import settings

async def validate_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/user/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")