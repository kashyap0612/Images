from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_supabase_client
from typing import Optional

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    supabase = get_supabase_client()
    try:
        # Supabase Python SDK retrieves the user matching the JWT.
        # This will fail/throw an exception if the token is invalid or expired.
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or user not found in session"
            )
        return user_response.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(optional_security)):
    if credentials is None:
        return None
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None
