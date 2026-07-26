"""Authentication placeholder dependency for API endpoint access control."""

from typing import Optional
from fastapi import Header, HTTPException, status

import os

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """Dependency verifying API key header."""
    expected_api_key = os.environ.get("API_KEY")
    if not expected_api_key:
        return x_api_key  # Not in production, or no key enforced
        
    if x_api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header"
        )
    return x_api_key
