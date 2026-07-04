#!/usr/bin/env python3
"""Generate operation manual PDF for MindShift app — redesigned layout.

Features:
- Clean A4 portrait layout with professional typography
- Phone-frame screenshot placeholders drawn directly in PDF
- Text left / screenshot right layout for feature pages
- Clear labels for every placeholder — you place the real images
"""

from fpdf import FPDF
import os

OUTPUT = "/Users/nannan/NLP 语言教练_Codex/docs/操作说明书_V1.0.pdf"
SCREENSHOT_DIR = "/Users/nannan/NLP 语言教练_Codex/docs/截图"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_MEDIUM = "/System/Library/Fonts/STHeiti Medium.ttc"

# ── Color palette ──────────────────────────────────────────
C_ACCENT     = (0, 188, 212)       # cyan accent
C_TITLE      = (26, 26, 46)        # near-black for titles
C_BODY       = (60, 60, 75)        # body text
C_MUTED      = (120, 120, 140)     # secondary / muted text
C_PH_BG      = (238, 242, 248)     # placeholder background
C_PH_BORDER  = (180, 190, 210)     # placeholder outline
C_PH_TEXT    = (140, 150, 175)     # placeholder label
C_LINE       = (220, 225, 235)     # separator line

# ── Section data ──────────────────────────────────────────
CH_NUM = ["一","二","三","四","五","六","七","八","九","十","十一","十二","十三","十四"]

SECTIONS = [
    {
        "id": 1, "title": "软件简介", "screenshots": [],
        "body": (
            "念转 MindShift 是一款基于神经语言程序学（NLP）的自主心智训练应用。"
            "应用提供 NLP 课程学习、AI 辅助训练、角色扮演对话、案例学习等核心功能，"
            "帮助用户提升沟通能力、情绪管理能力和自我认知能力。\n\n"
            "运行环境要求：\n"
            "  - iOS 系统版本：26.5 及以上\n"
            "  - 支持机型：iPhone 15 系列及以上\n"
            "  - 网络要求：需网络连接以使用 AI 教练功能\n"
            "  - 存储空间：约 150MB\n\n"
            "技术架构：React Native 0.74 + Zustand 状态管理 + 智谱 AI GLM-4-Flash 引擎"
        ),
    },
    {
        "id": 2, "title": "启动与引导页",
        "screenshots": ["01_splash"],
        "body": (
            "首次打开应用：\n"
            "1. 启动后显示品牌 Logo 与产品名称的启动画面\n"
            "2. 自动进入引导页（Onboarding），展示 NLP 核心理念和三大核心功能\n"
            "3. 引导页包含三个轮播页面：NLP 简介 -> 核心功能 -> 开始学习\n"
            "4. 滑动浏览后点击「开始使用」进入登录页面\n\n"
            "非首次启动：将直接跳过引导页进入登录界面。\n"
            "已登录用户：跳过所有中间步骤直接进入主页。"
        ),
    },
    {
        "id": 3, "title": "登录与注册",
        "screenshots": ["02_login", "03_register"],
        "body": (
            "登录流程：\n"
            "1. 输入注册时使用的电子邮箱地址\n"
            "2. 输入密码（隐私文本输入）\n"
            "3. 点击「登录」按钮完成认证\n"
            "4. 登录成功后自动跳转到主页\n\n"
            "注册流程：\n"
            "1. 在登录页点击「立即注册」\n"
            "2. 填写：电子邮箱、昵称、密码\n"
            "3. 可选填写：性别\n"
            "4. 点击「注册」创建账户\n"
            "5. 注册成功后自动登录并进入主页\n\n"
            "安全说明：密码通过 bcrypt 哈希存储，传输全程 TLS 加密。"
        ),
    },
    {
        "id": 4, "title": "首页与底部导航",
        "screenshots": ["04_home_learn"],
        "body": (
            "底部导航栏包含五个主要模块，始终显示在屏幕底部：\n\n"
            "1.【学习】课程列表与筛选 — 全部 NLP 课程，支持按「入门」「进阶」「高级」筛选；"
            "每个课程卡片展示标题、等级标签、课程数、进度条。\n\n"
            "2.【训练】日常 NLP 训练入口 — 感官觉察训练和信念转变训练；"
            "底部展示历史训练记录列表。\n\n"
            "3.【角色扮演】NLP 场景对话 — 分类标签选择（职场/家庭/情绪等）；"
            "点击场景开始与 AI 教练对话。\n\n"
            "4.【知识库】综合内容 — 免费公开课、我的故事、专家问答、案例中心。\n\n"
            "5.【个人】个人中心与设置入口。"
        ),
    },
    {
        "id": 5, "title": "课程学习功能",
        "screenshots": ["05_course_detail", "06_lesson"],
        "body": (
            "课程列表页：\n"
            "  - 顶部分类筛选：全部 / 入门 / 进阶 / 高级\n"
            "  - 课程卡片：标题 + 难度标签（绿/蓝/紫）+ 课程数 + 进度条\n"
            "  - PREMIUM 标签表示会员专属课程\n\n"
            "课程详情页：\n"
            "  - 课程标题和描述\n"
            "  - 章节列表（每节课标题 + 完成状态图标）\n"
            "  - 课程总体进度条\n"
            "  - 点击任一章节进入学习内容\n\n"
            "课程内容页：\n"
            "  - Markdown 排版的教学正文\n"
            "  - 包含：核心概念、技术详解、实践应用、日常练习\n"
            "  - 可在学习后点击「标记完成」记录进度\n\n"
            "每日 NLP 知识卡：可分享的知识卡片，含 NLP 金句、今日练习、出处。"
        ),
    },
    {
        "id": 6, "title": "日常训练功能",
        "screenshots": ["07_training", "08_training_analysis"],
        "body": (
            "训练首页提供两种训练类型入口：\n"
            "  1. 感官觉察 — 提升五感觉察能力\n"
            "  2. 信念转变 — 识别和转化限制性信念\n"
            "底部「训练记录」列表展示所有历史训练。\n\n"
            "训练执行流程：\n"
            "1. 选择训练类型\n"
            "2. 在输入框中输入当前感受或信念\n"
            "3. 点击「NLP教练 深度分析」按钮\n"
            "4. 显示 AI 加载动画（旋转菱形 + NLP 名言轮播）\n"
            "5. AI 教练返回专业 NLP 分析报告\n"
            "6. 分析包含：共情回应、NLP 技术分析、具体建议、行动练习\n\n"
            "每次训练自动评分，可用于追踪进步趋势。"
        ),
    },
    {
        "id": 7, "title": "角色扮演功能",
        "screenshots": ["09_roleplay", "10_dialogue"],
        "body": (
            "场景选择：\n"
            "  - 分类标签：职场 / 家庭 / 情绪 / 社交 / 成长 / 关系 / 健康 / 学习\n"
            "  - 每个场景显示：标题、难度标签（易/中/难）、PRO 标记\n"
            "  - PRO 标记为会员专属场景\n"
            "  - 点击场景卡进入对话界面\n\n"
            "AI 对话界面：\n"
            "  - 微信风格聊天气泡设计\n"
            "  - AI 教练自动发送开场引导信息\n"
            "  - 用户在底部输入框输入回应\n"
            "  - AI 教练结合 NLP 理论给予专业反馈\n"
            "  - 对话采用流式等待响应，显示 AI 正在输入状态\n\n"
            "每个场景可反复练习，尝试不同的回应策略。"
        ),
    },
    {
        "id": 8, "title": "知识库功能",
        "screenshots": ["11_community", "19_cases"],
        "body": (
            "知识库包含四个核心模块：\n\n"
            "1.【免费公开课】20 节 NLP 精品公开课，覆盖 8 个分类。"
            "每节课包含：理论讲解、案例说明、通俗理解、练习。\n\n"
            "2.【我的故事】用户分享的 NLP 学习成长经历，可点赞互动、提交自己的故事。\n\n"
            "3.【专家问答】提出 NLP 相关问题，获得专业解答。"
            "按分类浏览：NLP 技巧 / 情绪管理 / 人际关系。\n\n"
            "4.【案例中心】50 个 NLP 实战案例，覆盖 8 大分类。"
            "每个案例包含：NLP 技术分析、话术示范、转变对比。"
        ),
    },
    {
        "id": 9, "title": "个人中心与会员方案",
        "screenshots": ["12_profile", "13_membership"],
        "body": (
            "个人中心页面：\n"
            "  - 顶部统计面板：完成课程数、训练次数、打卡天数、徽章数\n"
            "  - 功能入口：学习记录（训练统计 + 雷达图 + 历史）| 本周挑战 | "
            "成就徽章 | 会员方案 | 偏好设置 | 设置 | 邀请好友\n"
            "  - 底部「退出登录」按钮\n\n"
            "会员方案页面：\n"
            "  - 免费版：展示基础功能\n"
            "  - 月付会员（98元/月）：全部课程、训练、案例\n"
            "  - 年付会员（498元/年）：月付全部权益 + 专属社群 + 1对1 服务\n"
            "  - 通过 Apple IAP 完成订阅支付\n"
            "  - 7 天免费试用\n\n"
            "左上角「< 返回」退回个人页面，支持左滑返回手势。"
        ),
    },
    {
        "id": 10, "title": "设置与隐私数据",
        "screenshots": ["14_settings", "15_privacy"],
        "body": (
            "设置页面功能：\n\n"
            "【显示设置】\n"
            "  - 深色模式切换\n"
            "  - 推送通知开关\n"
            "  - 每日提醒开关\n\n"
            "【数据管理】\n"
            "  - 导出学习报告（Markdown）\n"
            "  - 清除缓存\n"
            "  - 清除个人所有数据（保留账户信息）\n\n"
            "【安全设置】\n"
            "  - 自动锁定时间设置（1/3/5/10 分钟或永不）\n"
            "  - 超过设定时间自动锁定，解锁需输入登录密码\n\n"
            "【法律信息】\n"
            "  - 隐私政策（完整版全文）\n"
            "  - 服务条款（含 Apple 自动续费披露条款）\n\n"
            "【账户操作】\n"
            "  - 注销账户（永久删除账户及关联数据）\n"
            "  - 退出登录"
        ),
    },
    {
        "id": 11, "title": "账户注销流程",
        "screenshots": ["17_delete_account"],
        "body": (
            "操作步骤：\n\n"
            "1. 进入「个人中心」->「设置」\n"
            "2. 点击「注销账户」\n"
            "3. 系统弹出确认对话框：\n"
            "   「确定要注销账户吗？此操作不可恢复，\n"
            "    您所有的数据将被永久删除」\n"
            "4. 点击「确认注销」执行删除\n"
            "5. 系统清除以下数据：\n"
            "   - 账户信息（邮箱、昵称、密码哈希）\n"
            "   - 学习进度和训练记录\n"
            "   - 成就徽章和打卡记录\n"
            "   - 会员状态\n"
            "6. 注销成功后返回登录页面\n\n"
            "[注意] 注销后无法恢复任何数据，如需重新使用需重新注册。\n\n"
            "清除本地数据（保留账户）：\n"
            "  设置 -> 清除个人所有数据 -> 确认后清除本地缓存、\n"
            "  学习进度、训练记录，保留登录状态和云端信息。"
        ),
    },
    {
        "id": 12, "title": "成就系统与打卡",
        "screenshots": ["18_achievement", "20_checkin"],
        "body": (
            "成就徽章系统（共 10 枚）：\n"
            "  1. 初识 NLP — 完成第一节课程\n"
            "  2. 学习达人 — 完成 5 节课程\n"
            "  3. 专注之星 — 连续 7 天练习\n"
            "  4. 感官大师 — 完成感官觉察训练\n"
            "  5. NLP 探索者 — 完成所有入门课程\n"
            "  6. 沟通高手 — 完成 10 次角色扮演\n"
            "  7. 信念转化者 — 完成信念转变训练\n"
            "  8. 连续打卡王 — 连续 30 天打卡\n"
            "  9. NLP 实践者 — 完成 50 次训练\n"
            "  10. NLP 大师 — 完成全部课程\n\n"
            "每日打卡功能：\n"
            "  - 在个人中心点击「今日打卡」签到\n"
            "  - 每日首次进入会提示打卡\n"
            "  - 连续打卡记录显示在统计面板\n"
            "  - 打卡数据存储在本地 AsyncStorage"
        ),
    },
    {
        "id": 13, "title": "法律文档（合规说明）",
        "screenshots": ["16_terms"],
        "body": (
            "隐私政策：\n"
            "  完整隐私政策共 11 节，涵盖信息收集（主动+自动，含 Apple 隐私标签分类表）、"
            "AES-256-GCM 加密、信息使用与共享（含第三方服务列表）、数据存储与安全、"
            "用户数据权利（查阅/更正/删除/导出/撤回/注销）、未成年人保护、Cookie 政策、"
            "国际数据传输、政策更新、联系方式。\n\n"
            "服务条款：\n"
            "  完整协议共 11 节，其中第 6.4 节为 Apple 强制披露的自动续期订阅条款：\n"
            "  - 扣款通过 Apple ID 账户\n"
            "  - 自动续订机制说明\n"
            "  - 24 小时关闭自动续订提示\n"
            "  - Apple 订阅管理路径\n"
            "  - 免费试用失效说明\n"
            "  - 退款需通过 Apple 官方渠道"
        ),
    },
    {
        "id": 14, "title": "技术架构说明",
        "screenshots": [],
        "body": (
            "应用架构概述\n\n"
            "  前端框架：React Native 0.74（跨平台 iOS / Android）\n"
            "  状态管理：Zustand（7 个独立 Store）\n"
            "  导航方案：React Navigation 6（Stack + BottomTab）\n"
            "  AI 引擎：智谱 AI GLM-4-Flash（NLP 教练对话 + 训练评估）\n"
            "  数据存储：AsyncStorage（本地）+ 云端 API（认证/会员）\n"
            "  加密方案：AES-256-GCM（客户端敏感数据加密）\n"
            "  安全认证：JWT Token + bcrypt 密码哈希\n\n"
            "核心模块划分\n\n"
            "  services/     - API 通信、离线队列、AI 服务、崩溃监控\n"
            "  store/        - 领域状态管理（认证/课程/训练/角色扮演/会员等）\n"
            "  components/   - 13 个通用 UI 组件（按钮/卡片/雷达图/加载动画等）\n"
            "  screens/      - 36 个页面（学习/训练/角色扮演/知识库/个人）\n"
            "  navigation/   - 3 个导航栈（认证/主页面/帮助）\n"
            "  utils/        - 平台适配和常量定义\n\n"
            "数据流说明\n\n"
            "  用户操作 -> Screen 组件 -> Store（Zustand）-> Service（API）-> 云/本地存储\n"
            "  AI 功能：Training/Roleplay Screen -> Store -> zhipuaiService -> 智谱 API"
        ),
    },
]

# Screenshot key -> display label
SCREENSHOT_LABELS = {
    "01_splash": "[启动页/入门引导]",
    "02_login": "[登录页面]",
    "03_register": "[注册页面]",
    "04_home_learn": "[首页-课程列表]",
    "05_course_detail": "[课程详情页]",
    "06_lesson": "[课程内容页]",
    "07_training": "[训练选择页]",
    "08_training_analysis": "[AI 分析反馈页]",
    "09_roleplay": "[角色扮演场景列表]",
    "10_dialogue": "[AI 对话界面]",
    "11_community": "[知识库首页]",
    "12_profile": "[个人中心]",
    "13_membership": "[会员方案页]",
    "14_settings": "[设置页面]",
    "15_privacy": "[隐私政策页]",
    "16_terms": "[服务条款页]",
    "17_delete_account": "[注销确认对话框]",
    "18_achievement": "[成就徽章页]",
    "19_cases": "[案例中心页]",
    "20_checkin": "[每日打卡页]",
}

def ch_section_id(idx):
    """Return Chinese section number for 1..14."""
    if 1 <= idx <= len(CH_NUM):
        return CH_NUM[idx-1]
    return str(idx)

# ════════════════════════════════════════════════════════════
#  PDF class
# ════════════════════════════════════════════════════════════

class ManualPDF(FPDF):
    PHONE_W = 52        # phone mockup width (mm)
    PHONE_H = 112       # phone mockup height (~393:852 ratio)
    GAP = 4             # gap between stacked mockups
    COL_RIGHT = 138     # right column start (left text width ~120mm)
    LM = 14             # left margin
    RM = 14             # right margin

    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(True, 18)
        self.add_font('L', '', FONT_LIGHT)
        self.add_font('M', '', FONT_MEDIUM)

    # ── Header ─────────────────────────────────────────────
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('L', '', 8.5)
        self.set_text_color(*C_MUTED)
        self.cell(0, 5, "MindShift  V1.0  操作说明书", align='L')
        self.cell(0, 5, f"- {self.page_no()} -", align='R', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(*C_LINE)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    # ── Footer ─────────────────────────────────────────────
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_font('L', '', 7)
        self.set_text_color(*C_MUTED)
        self.cell(0, 6, "北京汇成家科技有限公司  |  仅供 Apple App Store 审核及软著申请使用",
                  align='C')

    # ── Phone mockup ───────────────────────────────────────
    def draw_phone_mockup(self, x, y, screenshot_key):
        w, h = self.PHONE_W, self.PHONE_H
        label = SCREENSHOT_LABELS.get(screenshot_key, screenshot_key)
        img_file = os.path.join(SCREENSHOT_DIR, f"{screenshot_key}.png")

        if os.path.exists(img_file):
            # ── Real screenshot — place it ──
            inset = 2
            self.image(img_file, x=x+inset, y=y+inset, w=w-2*inset, h=h-2*inset)
            self.set_line_width(1)
            self.set_draw_color(*C_PH_BORDER)
            self.rect(x, y, w, h, style='D')
            self.set_font('L', '', 7)
            self.set_text_color(*C_MUTED)
            self.set_xy(x, y + h + 0.5)
            self.cell(w, 4, label, align='C')
            return

        # ── Placeholder ──
        # Outer phone body
        self.set_fill_color(*C_PH_BG)
        self.set_draw_color(*C_PH_BORDER)
        self.set_line_width(0.8)
        self.rect(x, y, w, h, style='DF')

        # Inner screen area
        ins = 3
        sx, sy, sw, sh = x+ins, y+ins+8, w-2*ins, h-ins-14
        self.set_fill_color(245, 247, 252)
        self.rect(sx, sy, sw, sh, style='F')

        # Status bar
        self.set_fill_color(*C_PH_BORDER)
        self.rect(sx, sy, sw, 8, style='F')

        # Label text
        self.set_font('M', '', 8)
        self.set_text_color(*C_PH_TEXT)
        self.set_xy(sx, sy + 14)
        self.cell(sw, 5, "请在此处放置截图", align='C')
        self.set_xy(sx, sy + 22)
        self.set_font('L', '', 7)
        self.cell(sw, 5, label, align='C')
        self.set_xy(sx, sy + 30)
        self.set_font('L', '', 6.5)
        self.set_text_color(*C_MUTED)
        self.cell(sw, 4, f"文件名: {screenshot_key}.png", align='C')
        self.set_xy(sx, sy + 36)
        self.cell(sw, 4, "推荐尺寸: 393 x 852 px", align='C')

        # Arrow
        self.set_text_color(*C_ACCENT)
        self.set_font('L', '', 24)
        self.set_xy(sx, sy + 44)
        self.cell(sw, 10, "v", align='C')

        # Notch
        self.set_fill_color(*C_PH_BORDER)
        notch_cx = x + w / 2
        self.rect(notch_cx - 10, y + ins + 1, 20, 4, style='F')
        self.circle(notch_cx, y + ins + 3, 2)

        # Label below
        self.set_font('L', '', 7)
        self.set_text_color(*C_MUTED)
        self.set_xy(x, y + h + 0.5)
        self.cell(w, 4, label, align='C')

    # ── Cover page ────────────────────────────────────────
    def cover_page(self):
        self.add_page()
        # Top accent bar
        self.set_fill_color(*C_ACCENT)
        self.rect(0, 0, self.w, 4, style='F')

        self.ln(50)

        # App name
        self.set_font('M', '', 28)
        self.set_text_color(*C_TITLE)
        self.cell(0, 14, "MindShift", new_x='LMARGIN', new_y='NEXT', align='C')
        self.set_font('L', '', 14)
        self.set_text_color(*C_MUTED)
        self.cell(0, 8, "念转", new_x='LMARGIN', new_y='NEXT', align='C')

        self.ln(8)
        self.set_font('M', '', 20)
        self.set_text_color(*C_ACCENT)
        self.cell(0, 10, "操 作 说 明 书", new_x='LMARGIN', new_y='NEXT', align='C')

        # Decorative line
        self.ln(4)
        self.set_draw_color(*C_ACCENT)
        self.set_line_width(0.6)
        cx = self.w / 2
        self.line(cx - 28, self.get_y(), cx + 28, self.get_y())
        self.ln(25)

        # Info block
        self.set_font('L', '', 11)
        self.set_text_color(*C_BODY)
        for line in [
            "软件名称：MindShift (念转)",
            "版本号：V1.0",
            "开发公司：北京汇成家科技有限公司",
            "运行平台：iOS 26.5+ / iPhone",
            "",
            "文档类型",
            "Apple App Store 审核  /  软著申请配套说明",
        ]:
            self.cell(0, 8, line, new_x='LMARGIN', new_y='NEXT', align='C')

        # Bottom accent bar
        self.ln(30)
        self.set_fill_color(*C_ACCENT)
        self.rect(0, self.h - 4, self.w, 4, style='F')

    # ── Section page ───────────────────────────────────────
    def section_page(self, sec):
        self.add_page()

        title = f"{ch_section_id(sec['id'])}、{sec['title']}"

        # Section title
        self.set_font('M', '', 16)
        self.set_text_color(*C_ACCENT)
        self.cell(0, 9, title, new_x='LMARGIN', new_y='NEXT')
        self.ln(1)

        # Accent underline
        self.set_draw_color(*C_ACCENT)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.l_margin + 35, self.get_y())
        self.ln(6)

        screenshots = sec.get("screenshots", [])
        if not screenshots:
            self._render_body_text_full(sec["body"])
            return

        # Layout: text on left, mockups on right
        mx = self.COL_RIGHT
        my_start = self.get_y()
        text_w = mx - self.l_margin - 4

        # Draw mockups first
        for i, skey in enumerate(screenshots):
            my = my_start + i * (self.PHONE_H + self.GAP + 4)
            self.draw_phone_mockup(mx, my, skey)

        # Draw text on left
        self.set_xy(self.l_margin, my_start)
        self.set_font('L', '', 10)
        self.set_text_color(*C_BODY)
        for para in sec["body"].split('\n\n'):
            para = para.strip()
            if not para:
                continue
            self.set_x(self.l_margin)
            self.multi_cell(text_w, 5.8, para)
            self.ln(1.5)

    def _render_body_text_full(self, text):
        self.set_font('L', '', 10)
        self.set_text_color(*C_BODY)
        for para in text.split('\n\n'):
            para = para.strip()
            if not para:
                continue
            self.multi_cell(0, 5.8, para)
            self.ln(1.5)


# ════════════════════════════════════════════════════════════
#  Generate
# ════════════════════════════════════════════════════════════

def generate():
    pdf = ManualPDF()

    pdf.cover_page()

    for sec in SECTIONS:
        pdf.section_page(sec)

    pdf.output(OUTPUT)
    print(f"\nDone! 操作说明书已生成: {OUTPUT}")
    print(f"   总页数: {pdf.page_no()}")

    # ── Image insertion guide ──
    print("\n" + "=" * 60)
    print("截图放置指南")
    print("=" * 60)
    for skey, label in SCREENSHOT_LABELS.items():
        img_path = os.path.join(SCREENSHOT_DIR, f"{skey}.png")
        status = "[已有]" if os.path.exists(img_path) else "[待放]"
        print(f"  {status}  {skey}.png  {label}")
    print("\n  截图规格: 393 x 852 像素 (iPhone 17 Pro 原生分辨率)")
    print(f"  放置目录: {SCREENSHOT_DIR}/")
    print("=" * 60)

if __name__ == "__main__":
    generate()
