from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, AuthResponse, PreferencesUpdate, MessageResponse
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已注册")
    
    user = User(
        nickname=req.nickname,
        email=req.email,
        hashed_password=hash_password(req.password),
        gender=req.gender,
    )
    db.add(user)
    await db.flush()
    
    token = create_access_token(user.id, user.email)
    return AuthResponse(
        token=token,
        user={
            "id": user.id, "nickname": user.nickname, "email": user.email,
            "gender": user.gender, "avatar": user.avatar, "level": user.level,
            "xp": user.xp, "is_premium": user.is_premium,
            "membership_plan": user.membership_plan,
        }
    )

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")
    
    token = create_access_token(user.id, user.email)
    return AuthResponse(
        token=token,
        user={
            "id": user.id, "nickname": user.nickname, "email": user.email,
            "gender": user.gender, "avatar": user.avatar, "level": user.level,
            "xp": user.xp, "is_premium": user.is_premium,
            "membership_plan": user.membership_plan,
        }
    )

@router.put("/preferences", response_model=MessageResponse)
async def update_preferences(
    req: PreferencesUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import json
    user.preferences = json.dumps(req.preferences, ensure_ascii=False)
    await db.flush()
    return MessageResponse(message="偏好设置已保存")

@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    import json
    return {
        "id": user.id, "nickname": user.nickname, "email": user.email,
        "gender": user.gender, "avatar": user.avatar, "level": user.level,
        "xp": user.xp, "is_premium": user.is_premium,
        "membership_plan": user.membership_plan,
        "preferences": json.loads(user.preferences) if user.preferences else {},
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
