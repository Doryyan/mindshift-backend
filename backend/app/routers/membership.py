from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.utils.security import get_current_user
import json

router = APIRouter(prefix="/api/v1/membership", tags=["Membership"])

PLANS = [
    {"id": 1, "name": "免费版", "price": 0, "period": "permanent", "features": [
        "入门课程（4门·20节课）", "100+节NLP免费公开课", "感官觉察+信念转变训练",
        "职场+家庭角色扮演", "职场沟通+情绪管理案例", "每日NLP知识卡", "帮助中心",
        "成长故事·专家问答浏览"
    ]},
    {"id": 2, "name": "月付会员", "price": 98, "period": "monthly", "features": [
        "全部10门课程（50+节）", "全部训练类型+AI分析", "50个角色扮演场景",
        "50个NLP实战案例", "学习记录·成就徽章", "学习报告导出", "社区互动",
        "深色模式·自动锁定"
    ]},
    {"id": 3, "name": "年付会员", "price": 498, "period": "yearly", "features": [
        "月付会员全部权益", "专属NLP学习社群", "新功能优先体验",
        "每月1次1v1教练咨询", "年费会员专属标识", "2倍徽章进度加速"
    ]},
]

@router.get("/plans")
async def get_plans():
    return PLANS

@router.get("/status")
async def get_status(user: User = Depends(get_current_user)):
    return {
        "has_membership": user.is_premium,
        "plan_name": user.membership_plan,
        "status": "active" if user.is_premium else "free",
        "expires_at": user.membership_expires_at.isoformat() if user.membership_expires_at else None,
    }

@router.post("/upgrade")
async def upgrade_plan(
    req: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan_id = req.get("plan_id", 2)
    user.is_premium = True
    user.membership_plan = "monthly" if plan_id == 2 else "yearly"
    from datetime import datetime, timezone, timedelta
    user.membership_expires_at = datetime.now(timezone.utc) + timedelta(days=30 if plan_id == 2 else 365)
    await db.flush()
    return {"success": True, "message": "升级成功"}

@router.post("/cancel")
async def cancel_subscription(user: User = Depends(get_current_user)):
    return {"success": True, "message": "订阅已取消"}

@router.post("/restore")
async def restore_purchases(user: User = Depends(get_current_user)):
    return {"success": True, "message": "购买已恢复"}
