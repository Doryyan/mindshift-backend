"""Dashboard API — aggregate stats for admin panel."""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

async def get_one(db, sql, params=None):
    r = await db.execute(text(sql), params or {})
    return r.scalar() or 0

@router.get("/summary")
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    month_ago = (now - timedelta(days=30)).isoformat()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()

    total_users = await get_one(db, "SELECT COUNT(*) FROM users")
    new_today = await get_one(db, "SELECT COUNT(*) FROM users WHERE created_at >= :d", {"d": today})
    new_week = await get_one(db, "SELECT COUNT(*) FROM users WHERE created_at >= :d", {"d": week_ago})
    new_month = await get_one(db, "SELECT COUNT(*) FROM users WHERE created_at >= :d", {"d": month_ago})
    active_30d = await get_one(db, "SELECT COUNT(*) FROM users WHERE last_login_at >= :d", {"d": month_ago})
    free_c = await get_one(db, "SELECT COUNT(*) FROM users WHERE membership_plan='free'")
    monthly_c = await get_one(db, "SELECT COUNT(*) FROM users WHERE membership_plan='monthly'")
    yearly_c = await get_one(db, "SELECT COUNT(*) FROM users WHERE membership_plan='yearly'")
    premium_total = monthly_c + yearly_c
    conv_rate = round(premium_total / total_users * 100, 1) if total_users else 0
    mrr = monthly_c * 98 + round(yearly_c * 498 / 12, 1)
    courses = await get_one(db, "SELECT COUNT(*) FROM courses")
    lessons = await get_one(db, "SELECT COUNT(*) FROM lessons")
    cases = await get_one(db, "SELECT COUNT(*) FROM cases")
    scenarios = await get_one(db, "SELECT COUNT(*) FROM scenarios")
    posts = await get_one(db, "SELECT COUNT(*) FROM community_posts")
    training = await get_one(db, "SELECT COUNT(*) FROM training_sessions")
    kc = await get_one(db, "SELECT COUNT(*) FROM knowledge_cards")

    rows = await db.execute(text(
        "SELECT id, nickname, email, membership_plan, is_premium, created_at, last_login_at "
        "FROM users ORDER BY created_at DESC LIMIT 10"
    ))
    recent = []
    for r in rows:
        recent.append({"id":str(r[0]),"nickname":str(r[1]),"email":str(r[2]),
            "plan":str(r[3]),"is_premium":bool(r[4]),
            "created_at":str(r[5]) if r[5] else None,
            "last_login":str(r[6]) if r[6] else None})

    labels, vals = [], []
    for i in range(29, -1, -1):
        d = now - timedelta(days=i)
        ds = d.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        de = d.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
        c = await get_one(db, "SELECT COUNT(*) FROM users WHERE created_at BETWEEN :a AND :b", {"a": ds, "b": de})
        labels.append(d.strftime("%m/%d")); vals.append(c)

    return {
        "users":{"total":total_users,"new_today":new_today,"new_week":new_week,"new_month":new_month,"active_30d":active_30d},
        "membership":{"free":free_c,"monthly":monthly_c,"yearly":yearly_c,"premium_total":premium_total,"conversion_rate":conv_rate},
        "revenue":{"estimated_mrr":mrr,"monthly_rev":monthly_c*98,"yearly_rev":yearly_c*498},
        "content":{"courses":courses,"lessons":lessons,"cases":cases,"scenarios":scenarios,"posts":posts,"training_sessions":training,"knowledge_cards":kc},
        "recent_users":recent,"growth":{"labels":labels,"values":vals},
    }

@router.get("/users")
async def list_users(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                    search: str = "", db: AsyncSession = Depends(get_db)):
    limit = page_size; offset = (page - 1) * page_size
    where = ""
    params = {"l": limit, "o": offset}
    if search:
        where = " WHERE nickname LIKE :s OR email LIKE :s"
        params["s"] = f"%{search}%"
    rows = await db.execute(text(
        f"SELECT id, nickname, email, membership_plan, is_premium, created_at, last_login_at, gender, level, xp FROM users{where} ORDER BY created_at DESC LIMIT :l OFFSET :o"
    ), params)
    total = await get_one(db, f"SELECT COUNT(*) FROM users{where}", params if search else None)
    users = []
    for r in rows:
        users.append({"id":str(r[0]),"nickname":str(r[1]),"email":str(r[2]),
            "plan":str(r[3]),"is_premium":bool(r[4]),
            "created_at":str(r[5]) if r[5] else None,"last_login":str(r[6]) if r[6] else None,
            "gender":str(r[7]) if r[7] else "","level":r[8] or 0,"xp":r[9] or 0})
    return {"users":users,"total":total,"page":page,"page_size":page_size}

@router.get("/users/{user_id}")
async def user_detail(user_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(text(
        "SELECT id, nickname, email, membership_plan, is_premium, membership_expires_at, created_at, last_login_at, gender, level, xp, bio "
        "FROM users WHERE id=:id"), {"id": user_id})
    u = r.fetchone()
    if not u: return {"error": "not found"}
    # Get progress summary
    prog = await get_one(db, "SELECT COUNT(*) FROM user_progress WHERE user_id=:id", {"id": user_id})
    checkin = await get_one(db, "SELECT COUNT(*) FROM daily_checkins WHERE user_id=:id", {"id": user_id})
    return {
        "id":str(u[0]),"nickname":str(u[1]),"email":str(u[2]),"plan":str(u[3]),"is_premium":bool(u[4]),
        "expires_at":str(u[5]) if u[5] else None,"created_at":str(u[6]) if u[6] else None,
        "last_login":str(u[7]) if u[7] else None,"gender":str(u[8]) if u[8] else "",
        "level":u[9] or 0,"xp":u[10] or 0,"bio":str(u[11]) if u[11] else "",
        "progress_lessons":prog,"checkin_days":checkin,
    }

@router.get("/revenue")
async def revenue_analysis(db: AsyncSession = Depends(get_db)):
    monthly_c = await get_one(db, "SELECT COUNT(*) FROM users WHERE membership_plan='monthly'")
    yearly_c = await get_one(db, "SELECT COUNT(*) FROM users WHERE membership_plan='yearly'")
    free_c = await get_one(db, "SELECT COUNT(*) FROM users WHERE membership_plan='free'")
    total = monthly_c + yearly_c + free_c
    return {
        "summary": {
            "monthly_users": monthly_c, "yearly_users": yearly_c, "free_users": free_c,
            "total_users": total,
            "conversion_rate": round((monthly_c+yearly_c)/total*100,1) if total else 0,
            "mrr": monthly_c*98 + round(yearly_c*498/12, 1),
            "monthly_revenue": monthly_c*98, "yearly_revenue": yearly_c*498,
            "arpu": round((monthly_c*98+yearly_c*498/12)/total,1) if total else 0,
        },
        "plans": [
            {"name":"免费版","price":0,"users":free_c,"revenue":0},
            {"name":"月付会员","price":98,"users":monthly_c,"revenue":monthly_c*98*12},
            {"name":"年付会员","price":498,"users":yearly_c,"revenue":yearly_c*498},
        ]
    }

@router.get("/content")
async def content_overview(db: AsyncSession = Depends(get_db)):
    courses = await get_one(db, "SELECT COUNT(*) FROM courses")
    lessons = await get_one(db, "SELECT COUNT(*) FROM lessons")
    cases = await get_one(db, "SELECT COUNT(*) FROM cases")
    scenarios = await get_one(db, "SELECT COUNT(*) FROM scenarios")
    posts = await get_one(db, "SELECT COUNT(*) FROM community_posts")
    training = await get_one(db, "SELECT COUNT(*) FROM training_sessions")
    kc = await get_one(db, "SELECT COUNT(*) FROM knowledge_cards")
    achievements = await get_one(db, "SELECT COUNT(*) FROM achievements")

    # Course list with lesson counts
    rows = await db.execute(text(
        "SELECT c.id, c.title, c.level, c.is_premium, "
        "(SELECT COUNT(*) FROM lessons WHERE course_id=c.id) as lesson_count FROM courses c ORDER BY c.created_at DESC LIMIT 20"
    ))
    course_list = []
    for r in rows:
        course_list.append({"id":str(r[0]),"title":str(r[1]),"level":str(r[2]),"is_premium":bool(r[3]),"lessons":r[4] or 0})

    return {
        "counts":{"courses":courses,"lessons":lessons,"cases":cases,"scenarios":scenarios,
                  "posts":posts,"training_sessions":training,"knowledge_cards":kc,"achievements":achievements},
        "courses": course_list,
    }

@router.get("/growth")
async def growth_trends(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    # 90 day user growth
    labels90, vals90 = [], []
    for i in range(89, -1, -1):
        d = now - timedelta(days=i)
        ds = d.replace(hour=0,minute=0,second=0,microsecond=0).isoformat()
        de = d.replace(hour=23,minute=59,second=59,microsecond=999999).isoformat()
        c = await get_one(db, "SELECT COUNT(*) FROM users WHERE created_at BETWEEN :a AND :b", {"a": ds, "b": de})
        if i % 5 == 0 or i == 0 or i == 89:
            labels90.append(d.strftime("%m/%d"))
        else:
            labels90.append("")
        vals90.append(c)

    # Cumulative
    cum = 0
    cum_vals = []
    for v in vals90:
        cum += v; cum_vals.append(cum)

    # Plan trend (per month for last 6 months)
    labels6m, free6m, monthly6m, yearly6m = [], [], [], []
    for i in range(5, -1, -1):
        d = (now.replace(day=1) - timedelta(days=30*i)).replace(hour=0,minute=0,second=0)
        labels6m.append(d.strftime("%Y/%m"))
        ds = d.isoformat()
        de = (d + timedelta(days=32)).replace(day=1).isoformat()
        free6m.append(await get_one(db, "SELECT COUNT(*) FROM users WHERE membership_plan='free' AND created_at < :de", {"de": de}))
        monthly6m.append(await get_one(db, "SELECT COUNT(*) FROM users WHERE membership_plan='monthly' AND created_at < :de", {"de": de}))
        yearly6m.append(await get_one(db, "SELECT COUNT(*) FROM users WHERE membership_plan='yearly' AND created_at < :de", {"de": de}))

    return {
        "daily_registration": {"labels": labels90, "values": vals90},
        "cumulative_users": {"labels": labels90, "values": cum_vals},
        "plan_evolution": {"labels": labels6m, "free": free6m, "monthly": monthly6m, "yearly": yearly6m},
    }

@router.get("/system")
async def system_info():
    import platform, sys
    return {
        "app_name": "MindShift API",
        "version": "1.0.0",
        "python": sys.version,
        "platform": platform.platform(),
        "server_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "database": "SQLite (本地) / PostgreSQL (生产)",
        "endpoints": {
            "admin_dashboard": "/admin",
            "api_docs": "/docs",
            "api_health": "/api/v1/health",
        }
    }
