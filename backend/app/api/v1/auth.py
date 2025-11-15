"""
Authentication API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()


@router.post("/register")
async def register(db: AsyncSession = Depends(get_db)):
    """회원가입"""
    return {"message": "Registration endpoint - To be implemented"}


@router.post("/login")
async def login(db: AsyncSession = Depends(get_db)):
    """로그인"""
    return {"message": "Login endpoint - To be implemented"}


@router.post("/refresh")
async def refresh_token(db: AsyncSession = Depends(get_db)):
    """토큰 갱신"""
    return {"message": "Refresh token endpoint - To be implemented"}


@router.get("/me")
async def get_current_user(db: AsyncSession = Depends(get_db)):
    """현재 사용자 정보"""
    return {"message": "Current user endpoint - To be implemented"}
