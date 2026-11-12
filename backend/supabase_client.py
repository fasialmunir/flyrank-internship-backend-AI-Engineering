import os
from pathlib import Path
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase_auth.errors import AuthApiError
from fastapi import HTTPException
# Locate the backend directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from backend/.env
load_dotenv(BASE_DIR / ".env")

# Read Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate configuration
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL or SUPABASE_KEY is missing from .env"
    )

# Initialize Supabase client
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Check whether token is provided
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail={"error": "Access token required"}
        )

    token = credentials.credentials.strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail={"error": "Access token required"}
        )

    try:
        # Verify token with Supabase
        response = supabase.auth.get_user(token)

        if not response.user:
            raise HTTPException(
                status_code=401,
                detail={"error": "Invalid or expired token"}
            )

        # Return verified user
        return response.user

    except AuthApiError:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid or expired token"}
        )