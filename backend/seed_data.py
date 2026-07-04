"""Seed development data for MindShift backend."""
import asyncio
import uuid
import json
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.config import settings
from app.database import Base
from app.models.course import Course, Lesson, KnowledgeCard
from app.models.case import Case
from app.models.roleplay import Scenario
from app.models.training import Achievement
from app.utils.security import hash_password
from app.models.user import User

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with session_factory() as db:
        # Check if already seeded
        r = await db.execute(select(Course).limit(1))
        if r.scalar_one_or_none():
            print("Already seeded. Skipping.")
            return
        
        # --- Achievements ---
        achievements = [
            {"key":"first_login","name":"初识NLP","description":"首次登录应用","icon":"🌟","category":"入门","xp_reward":10,"condition_type":"login_count","condition_value":1},
            {"key":"first_course","name":"学习启航","description":"完成第一门课程","icon":"📚","category":"学习","xp_reward":30,"condition_type":"course_count","condition_value":1},
            {"key":"five_courses","name":"学以致用","description":"完成5门课程","icon":"🎓","category":"学习","xp_reward":100,"condition_type":"course_count","condition_value":5},
            {"key":"first_training","name":"训练新手","description":"完成第一次训练","icon":"🧠","category":"训练","xp_reward":20,"condition_type":"training_count","condition_value":1},
            {"key":"ten_trainings","name":"坚持训练","description":"完成10次训练","icon":"💪","category":"训练","xp_reward":80,"condition_type":"training_count","condition_value":10},
            {"key":"first_roleplay","name":"角色初演","description":"完成第一次角色扮演","icon":"🎭","category":"实践","xp_reward":25,"condition_type":"roleplay_count","condition_value":1},
            {"key":"seven_day_streak","name":"七天坚持","description":"连续签到7天","icon":"🔥","category":"习惯","xp_reward":70,"condition_type":"streak_days","condition_value":7},
            {"key":"thirty_day_streak","name":"月度达人","description":"连续签到30天","icon":"👑","category":"习惯","xp_reward":300,"condition_type":"streak_days","condition_value":30},
            {"key":"level_five","name":"NLP探索者","description":"达到等级5","icon":"⭐","category":"成长","xp_reward":150,"condition_type":"level","condition_value":5},
            {"key":"level_ten","name":"NLP大师","description":"达到等级10","icon":"🏆","category":"成长","xp_reward":500,"condition_type":"level","condition_value":10},
        ]
        for a in achievements:
            db.add(Achievement(id=str(uuid.uuid4()), **a))
        
        # --- Courses (membership) ---
        membership_courses = [
            {"title":"NLP基础入门","description":"了解NLP的起源、核心概念和基本框架","level":"beginner","category":"foundation","lesson_count":5,"total_lessons":5,"sort_order":1,"cover_emoji":"🌱"},
            {"title":"感官觉察训练","description":"提升五感敏锐度，觉察信息的细微变化","level":"beginner","category":"sensory","lesson_count":5,"total_lessons":5,"sort_order":2,"cover_emoji":"👁️"},
            {"title":"信念系统探索","description":"识别限制性信念，建立积极思维模式","level":"beginner","category":"belief","lesson_count":5,"total_lessons":5,"sort_order":3,"cover_emoji":"💭"},
            {"title":"情绪管理艺术","description":"运用NLP技术调节情绪，提升情商","level":"beginner","category":"emotion","lesson_count":5,"total_lessons":5,"sort_order":4,"cover_emoji":"💙"},
            {"title":"沟通模式进阶","description":"掌握米尔顿模式和元模型沟通技巧","level":"intermediate","category":"communication","lesson_count":5,"total_lessons":5,"sort_order":5,"cover_emoji":"🗣️","is_premium":True},
            {"title":"换框技术实战","description":"运用上下文换框和意义换框解决问题","level":"intermediate","category":"reframing","lesson_count":5,"total_lessons":5,"sort_order":6,"cover_emoji":"🔄","is_premium":True},
            {"title":"锚定技术精讲","description":"建立和管理资源心锚，掌控状态","level":"intermediate","category":"anchoring","lesson_count":5,"total_lessons":5,"sort_order":7,"cover_emoji":"⚓","is_premium":True},
            {"title":"次感元深度应用","description":"运用次感元调节技术改变内在体验","level":"advanced","category":"submodalities","lesson_count":5,"total_lessons":5,"sort_order":8,"cover_emoji":"🔬","is_premium":True},
            {"title":"策略建模大师","description":"学习NLP建模技术，复制卓越","level":"advanced","category":"modeling","lesson_count":5,"total_lessons":5,"sort_order":9,"cover_emoji":"🏗️","is_premium":True},
            {"title":"NLP综合实战","description":"综合运用NLP技术解决复杂问题","level":"advanced","category":"comprehensive","lesson_count":5,"total_lessons":5,"sort_order":10,"cover_emoji":"🎯","is_premium":True},
        ]
        for c in membership_courses:
            course = Course(id=str(uuid.uuid4()), is_public=False, **c)
            db.add(course)
            # Add lessons for each course
            lesson_titles = [
                [f"{c['title']} - 第1课：理论基础",f"{c['title']} - 第2课：核心概念",f"{c['title']} - 第3课：实践练习",f"{c['title']} - 第4课：案例应用",f"{c['title']} - 第5课：总结提升"],
            ][0]
            for j, lt in enumerate(lesson_titles):
                db.add(Lesson(id=str(uuid.uuid4()), course_id=course.id, title=lt, content=f"{lt}\n\n本节将带你深入了解NLP的核心内容。通过理论学习、案例分析和实践练习，你将逐步掌握相关技能。\n\n核心概念：\n1. 理解NLP的基本原则和框架\n2. 掌握关键技术和工具\n3. 在实际场景中灵活应用\n\n实践练习：\n• 每日反思：记录一个NLP技术应用场景\n• 观察练习：注意日常沟通中的语言模式\n• 模拟训练：与伙伴进行角色扮演练习", sort_order=j+1))
        
        # --- Scenarios ---
        scenarios_data = [
            ("职场沟通","职场","easy",False,"你是职场沟通教练，帮助学员练习工作中的NLP沟通技巧。"),("会议发言","职场","easy",False,"你是会议场合的NLP教练，帮助学员克服发言紧张。"),
            ("向上汇报","职场","medium",False,"帮助学员向上级汇报工作时的沟通技巧。"),("跨部门协作","职场","medium",False,"帮助学员处理跨部门协调沟通。"),
            ("面试谈判","职场","hard",True,"帮助学员在薪资谈判中运用NLP技巧。"),("客户说服","职场","hard",True,"帮助学员运用NLP提升客户说服力。"),
            ("时间管理","职场","easy",False,"用结果导向思维提高工作效率。"),("亲子对话","家庭","easy",False,"帮助改善亲子沟通方式。"),
            ("夫妻沟通","家庭","medium",False,"化解夫妻沟通障碍。"),("家庭矛盾调解","家庭","medium",False,"调解家庭成员之间的矛盾。"),
            ("青春期沟通","家庭","hard",True,"帮助与青春期孩子有效沟通。"),("婆媳关系","家庭","hard",True,"处理复杂的婆媳关系。"),
            ("家庭决策","家庭","easy",False,"用良好结果条件做家庭决策。"),("焦虑管理","情绪","easy",False,"处理日常焦虑和压力。"),
            ("愤怒控制","情绪","medium",False,"用中断模式控制愤怒情绪。"),("悲伤转化","情绪","medium",False,"用重新框架技术转化悲伤。"),
            ("恐惧克服","情绪","hard",True,"克服特定情境的恐惧感。"),("自信心建立","情绪","easy",False,"用次感元技术增强自信。"),
            ("情绪觉察","情绪","easy",False,"提升情绪觉察能力。"),("压力释放","情绪","medium",False,"用状态管理释放压力。"),
            ("陌生人破冰","社交","easy",False,"与陌生人自然展开对话。"),("社交焦虑克服","社交","medium",False,"克服社交场合紧张感。"),
            ("即兴演讲","社交","hard",True,"即兴发言时的状态管理。"),("聚会社交","社交","easy",False,"聚会中轻松社交技巧。"),
            ("拒绝与边界","社交","medium",False,"学会优雅地说不。"),("赞美与反馈","社交","easy",False,"有效赞美和反馈他人。"),
            ("目标设定","成长","easy",False,"用良好结果条件设定目标。"),("拖延克服","成长","medium",False,"用中断模式克服拖延。"),
            ("信念转化","成长","medium",False,"识别并转化限制性信念。"),("习惯养成","成长","easy",False,"用锚定技术培养新习惯。"),
            ("决策困境","成长","medium",False,"用生态平衡检查做决策。"),("自我激励","成长","medium",False,"用资源心锚激发内在动力。"),
            ("建立亲和力","关系","easy",False,"用匹配技术建立深层亲和力。"),("倾听技巧","关系","easy",False,"提升倾听能力。"),
            ("冲突化解","关系","hard",True,"用换框技术化解人际冲突。"),("表达需求","关系","medium",False,"有效表达需求感受。"),
            ("道歉与修复","关系","medium",False,"修复破裂关系。"),("影响他人","关系","hard",True,"正面影响他人。"),
            ("运动习惯建立","健康","easy",False,"锚定技术建立运动习惯。"),("饮食管理","健康","medium",False,"次感元调节改善饮食。"),
            ("冥想入门","健康","easy",False,"NLP冥想放松身心。"),("睡眠改善","健康","medium",False,"状态管理改善睡眠。"),
            ("戒除坏习惯","健康","hard",True,"六步换框法戒除不良习惯。"),("快速学习","学习","easy",False,"表象系统优化学习。"),
            ("记忆力提升","学习","medium",False,"次感元增强记忆。"),("专注力训练","学习","easy",False,"心锚提升专注。"),
            ("考试焦虑","学习","medium",False,"克服考试紧张。"),("新技能掌握","学习","hard",True,"建模快速掌握新技能。"),
            ("创造力激发","学习","medium",False,"迪士尼策略激发创造。"),("领导力提升","职场","hard",True,"NLP提升领导力影响力。"),
        ]
        for title,cat,diff,premium,prompt in scenarios_data:
            db.add(Scenario(id=str(uuid.uuid4()),title=title,category=cat,difficulty=diff,
                is_premium=premium,system_prompt=prompt,
                opening_message=f"你好，欢迎进入「{title}」角色扮演场景。我是你的NLP教练，让我们开始练习如何在实际场景中运用NLP技巧。请先描述你遇到的具体情况，我会引导你找到更好的沟通方式。",
                sort_order=len(scenarios_data)))
        
        # --- Cases ---
        case_categories = ["communication","emotion_mgmt","personal_growth","parenting","relationship","sales_negotiation","health_habit","conflict_resolution"]
        case_names = {
            "communication": ["化解团队冲突","高效会议主持","绩效面谈技巧","一对一辅导","跨文化沟通","远程团队协作"],
            "emotion_mgmt": ["愤怒管理案例","焦虑缓解方案","压力转化实践","自信心重塑","负面情绪觉察","情绪表达训练"],
            "personal_growth": ["突破自我设限","目标达成之路","告别拖延症","建立晨间习惯","学习力突破","人生方向探索"],
            "parenting": ["作业大战化解","青春期沟通","电子产品管理","培养独立性","二孩关系调节","学习动力激发"],
            "relationship": ["夫妻冷战修复","婆媳关系改善","建立信任边界","深度倾听练习","表达爱的方式","修复感情裂痕"],
            "sales_negotiation": ["大客户谈判","价格博弈策略","建立客户信任","异议处理技巧","成交促成方法","长期关系维护"],
            "health_habit": ["戒烟成功之路","运动习惯养成","饮食结构调整","早睡早起计划","压力性饮食控制","冥想练习坚持"],
            "conflict_resolution": ["邻里纠纷调解","职场权力斗争","亲友借钱困境","价值观冲突化解","资源分配争议","误会消除指南"],
        }
        for cat in case_categories:
            for j, name in enumerate(case_names[cat]):
                is_prem = cat not in ("communication","emotion_mgmt")
                db.add(Case(id=str(uuid.uuid4()),title=name,category=cat,is_premium=is_prem,
                    scenario_description=f"这是一个关于{name}的真实案例，展示了NLP技术在{cat}领域的实际应用。",
                    techniques_applied='{"主要技术":"换框技术","辅助技术":"感官觉察","补充技术":"锚定技术"}',
                    key_learning=f"通过{name}案例，学会运用NLP技术解决问题，提升沟通能力。",
                    sort_order=j))
        
        # --- Knowledge Cards ---
        today = date.today()
        for i in range(30):
            d = today.replace(day=max(1, today.day - i))
            db.add(KnowledgeCard(id=str(uuid.uuid4()),
                title=f"NLP每日一课 - {d.strftime('%m月%d日')}",
                content=f"<h2>今日NLP智慧</h2><p>每一天都是新的学习机会。NLP教会我们，改变从觉察开始。关注你的思维模式，你会发现更多可能性。</p>",
                emoji="📖", date=d.isoformat()))
        
        # --- Demo user ---
        demo_user = User(
            id="demo-user-001",
            nickname="NLP学习者",
            email="demo@mindshift.app",
            hashed_password=hash_password("demo123"),
            gender="unspecified",
            level=3,
            xp=250,
            is_premium=False,
            membership_plan="free",
        )
        db.add(demo_user)
        
        await db.commit()
        print("✅ Seed data created successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
