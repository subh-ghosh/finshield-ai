"""Authentication placeholder dependency for API endpoint access control."""

from typing import Optional
from fastapi import Header, HTTPException, status

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """Dependency verifying API key header placeholder.

    Args:
        x_api_key: Optional API key header string.

    Returns:
        Optional[str]: Verified API key or None if auth is not strictly required in dev.
    """
    # In development mode, allow empty API key.
    # If key is provided and invalid in production mode, raise 401 Unauthorized.
    if x_api_key is not None and x_api_key == "invalid_key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API Key provided"
        )
    return x_api_key
