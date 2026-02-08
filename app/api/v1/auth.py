from fastapi import APIRouter, HTTPException, Request
from app.schemas.auth import LoginRequest
from app.core.security import create_access_token
from app.core.rate_limit import limiter
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/login")
@limiter.limit("10/minute")
async def admin_login(request: Request, payload: LoginRequest):
    if (
        payload.email != settings.ADMIN_EMAIL
        or payload.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    token = create_access_token(
        {
            "sub": payload.email,
            "role": "admin",
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }