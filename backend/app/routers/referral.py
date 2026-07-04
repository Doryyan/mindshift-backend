from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/referral", tags=["Referral"])

class ApplyReferralRequest(BaseModel):
    code: str

@router.get("/code")
async def get_referral_code(user: User = Depends(get_current_user)):
    return {"code": f"MS{user.id[:8].upper()}", "url": f"https://mindshift.app/ref/{user.id[:8]}"}

@router.get("/stats")
async def get_referral_stats(user: User = Depends(get_current_user)):
    return {"total_referrals": 0, "reward_xp": 0, "referrals": []}

@router.post("/apply")
async def apply_referral(req: ApplyReferralRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return {"success": True, "message": "推荐码已使用", "reward_xp": 50}
