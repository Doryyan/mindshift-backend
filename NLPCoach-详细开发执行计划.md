# 念转（MindShift）详细开发执行计划 v2.2

> 项目代号：MindShift | 编制日期：2026-06-30 | 总工期：约42周（10.5个月）
> 技术栈：React Native 0.74.5 + FastAPI + 智谱AI GLM-4-Flash + PostgreSQL
> 产品名：念转（MindShift）| Bundle ID：com.mindshift.app | 图标：钻石之钥

---

## 执行总览

| 阶段 | 周数 | 周期 | 核心目标 | 里程碑 |
|------|------|------|----------|--------|
| 阶段0：项目准备 | W1-W3 | 6.30 - 7.20 | 版权合规 + 环境搭建 + 设计定稿 | 🏁 设计稿评审通过 |
| 阶段1：MVP核心 | W4-W10 | 7.21 - 9.7 | iOS TestFlight可用版本 | 🏁 TestFlight首次分发 |
| 阶段2：内容扩展 | W11-W17 | 9.8 - 10.26 | 完整内容+AI深度应用 | 🏁 全部50场景可用 |
| 阶段3：商业化 | W18-W21 | 10.27 - 11.23 | 付费闭环 | 🏁 内购沙盒测试通过 |
| 阶段4：打磨上线 | W22-W25 | 11.24 - 12.21 | App Store审核上线 | 🏁 App Store上架 |
| 阶段5：增长飞轮 | W26-W32 | 12.22 - 2.7 | 社交增长体系 | 🏁 分享卡片+邀请系统 |
| 阶段6：多平台 | W33-W42 | 2.8 - 4.18 | macOS+Android | 🏁 双平台上架 |

---

## 阶段0：项目准备（W1-W3，6.30 - 7.20）

### W1（6.30 - 7.6）版权合规 + 项目初始化

| 任务ID | 任务 | 负责人 | 交付物 | 验收标准 |
|--------|------|--------|--------|----------|
| P0-01 | 起草用户协议 | 产品+法务 | 用户协议.md | 含知识产权声明、免责条款 |
| P0-02 | 起草隐私政策 | 产品+法务 | 隐私政策.md | 含数据加密说明、用户数据权利 |
| P0-03 | 起草免责声明 | 产品+法务 | 免责声明文案 | "非医疗建议"标注到位 |
| P0-04 | 版权合规方案终稿 | 产品 | 版权方案终稿 | 参考书目清单+内容SOP |
| P0-05 | NLP教练招聘启动 | 产品 | 招聘JD发布 | 兼职/顾问，Practitioner级 |
| P0-06 | React Native项目脚手架初始化 | 前端 | RN项目骨架 | `npx react-native init`成功 |
| P0-07 | FastAPI项目骨架初始化 | 后端 | FastAPI骨架 | `/health`返回200 |
| P0-08 | 开发环境验证 | 前端+后端 | 环境验证报告 | iOS模拟器启动OK，后端启动OK |

### W2（7.7 - 7.13）内容大纲 + UI设计

| 任务ID | 任务 | 负责人 | 交付物 | 验收标准 |
|--------|------|--------|--------|----------|
| D-01 | App图标设计（钻石之钥·暗色+霓虹） | 设计 | 1024x1024图标 + 各尺寸导出 | 见图标设计规范5.4节，暗色背景+钻石+钥匙杆+神经网格 |
| D-02 | 导航结构设计（底部5Tab + Stack） | 设计 | 导航信息架构图 | Tab切换交互定义清晰 |
| D-03 | 引导页5张UI设计稿 | 设计 | 5张引导页UI稿 | 品牌页（Logo动效）+4张功能介绍页，霓虹动效说明 |
| D-04 | 学习模块课程列表页设计 | 设计 | 课程列表UI稿 | 三级筛选+进度条+霓虹卡片 |
| D-05 | 暗色主题设计系统文档 | 设计 | 设计系统文档 | 色板/字体/间距/组件规范 |
| B-01 | 数据库模型设计终稿 | 后端 | ER图 + DDL脚本 | 覆盖全部表：users/courses/lessons/training/roleplay/cases/community/membership/skill_profiles |
| B-02 | API接口文档初稿 | 后端 | OpenAPI 3.0文档 | 全部endpoint定义完成 |

### W3（7.14 - 7.20）内容一期 + 设计定稿

| 任务ID | 任务 | 负责人 | 交付物 | 验收标准 |
|--------|------|--------|--------|----------|
| C-01 | 4门入门课程大纲终稿 | 内容 | 课程大纲文档 | 每课含课时列表+来源标注 |
| C-02 | NLP-B-01内容撰写（前3课时） | 内容 | 3课时完整内容 | 每课时1500-3000字+概念卡片+来源标注 |
| C-03 | 12个MVP场景描述撰写 | 内容 | 12场景描述文档 | 含角色设定+开场白+NLP技巧提示 |
| D-06 | 全部页面设计稿终稿 | 设计 | 完整UI设计稿 | 含登录/注册/引导页/学习/训练/角色扮演/社区/个人 |
| B-03 | 智谱AI API Key申请 | 后端 | .env配置 | API Key验证可用 |
| B-04 | 数据库迁移脚本（Alembic） | 后端 | Alembic初始化 | `alembic upgrade head`成功 |

---

## 阶段1：MVP核心（W4-W10，7.21 - 9.7）

### W4-W5（7.21 - 8.3）认证+引导页+导航骨架

| 任务ID | 任务 | 负责人 | 依赖 | 交付物 |
|--------|------|--------|------|--------|
| F-01 | 引导页OnboardingScreen实现 | 前端 | D-03 | 5页滑动：品牌启动页（Logo+3秒过渡）+4页功能介绍+最后一页登录按钮 |
| F-02 | 登录/注册页面实现 | 前端 | D-06 | LoginScreen + RegisterScreen |
| F-03 | 底部Tab导航实现 | 前端 | D-02 | 5Tab：学习/训练/角色扮演/社区/个人 |
| F-04 | AuthStack + MainTab导航编排 | 前端 | F-02, F-03 | 根据登录状态切换导航 |
| F-05 | 霓虹主题系统实现 | 前端 | D-05 | colors.ts + typography.ts + NeonButton等 |
| B-05 | 用户注册/登录API | 后端 | B-01 | POST /auth/register, /auth/login, /auth/me |
| B-06 | JWT认证中间件 | 后端 | B-05 | JWT生成+验证+自动刷新 |

### W6-W7（8.4 - 8.17）学习+训练+角色扮演核心

| 任务ID | 任务 | 负责人 | 依赖 | 交付物 |
|--------|------|--------|------|--------|
| F-06 | 课程列表+详情页 | 前端 | F-03 | CourseListScreen + CourseDetailScreen |
| F-07 | 课时学习页（WebView富文本） | 前端 | F-06 | LessonScreen：图文+概念卡片+来源标签 |
| F-08 | 训练主页+感官训练页 | 前端 | F-03 | TrainingHomeScreen + SensoryScreen |
| F-09 | 信念日记页 | 前端 | F-03 | BeliefScreen：输入+AI分析+反馈 |
| F-10 | 场景列表+详情页 | 前端 | F-03 | ScenarioListScreen(8分类) + ScenarioDetailScreen |
| F-11 | 角色扮演对话页 | 前端 | F-10 | DialogueScreen：聊天气泡+NLP技巧徽章 |
| B-07 | 课程内容API | 后端 | B-01 | GET /courses, /courses/{id}/lessons, /lessons/{id} |
| B-08 | 训练评估API | 后端 | B-01, B-03 | POST /training/evaluate, /training/sensory, /training/belief |
| B-09 | 角色扮演API | 后端 | B-01, B-03 | POST /roleplay/dialogue/start, /chat, /evaluate |
| B-10 | 智谱AI NLP评估器 | 后端 | B-03 | NLP技巧多维度评估Prompt+JSON解析 |
| B-11 | 角色扮演对话管理器 | 后端 | B-03 | 场景角色Prompt+对话状态管理+历史记录 |
| C-04 | NLP-B-01全部10课时内容 | 内容 | C-01 | 完整课程内容入库 |
| C-05 | NLP-B-02全部12课时内容 | 内容 | C-01 | 完整课程内容入库 |

### W8（8.18 - 8.24）能力评估+游戏化+数据加密

| 任务ID | 任务 | 负责人 | 依赖 | 交付物 |
|--------|------|--------|------|--------|
| F-12 | 初始能力评估页（8题） | 前端 | F-03 | AssessmentScreen：8题+雷达图生成 |
| F-13 | 能力雷达图组件 | 前端 | F-05 | RadarChart组件：8维度霓虹色 |
| F-14 | 个人中心页 | 前端 | F-03 | ProfileScreen：雷达图+数据+设置入口 |
| F-15 | XP系统+段位徽章组件 | 前端 | F-05 | XP动画+段位霓虹徽章 |
| F-16 | AI每日心语组件 | 前端 | F-03 | 首页顶部每日心语卡片 |
| F-17 | 数据加密模块 | 前端 | - | AES-256-GCM加密工具类 |
| B-12 | 进度统计API | 后端 | B-01 | GET /progress/, /progress/stats, /progress/radar |
| B-13 | 用户能力画像API | 后端 | B-01 | NLP 8维度能力分CRUD |
| B-14 | AI每日心语API | 后端 | B-03 | 基于用户数据生成个性化心语 |
| P0-09 | 免责声明嵌入App | 前端 | P0-03 | 启动页+设置页+训练入口 |

### W9-W10（8.25 - 9.7）社区+联调+TestFlight

| 任务ID | 任务 | 负责人 | 依赖 | 交付物 |
|--------|------|--------|------|--------|
| F-18 | 社区主页+帖子列表 | 前端 | F-03 | CommunityScreen |
| F-19 | 发帖+帖子详情页 | 前端 | F-18 | CreatePostScreen + PostDetailScreen |
| F-20 | 每日打卡页 | 前端 | F-03 | CheckInScreen：日历视图+连续天数 |
| B-15 | 社区API | 后端 | B-01 | GET/POST /community/posts, /checkin |
| B-16 | 打卡API | 后端 | B-01 | GET/POST /community/checkin |
| T-01 | 前后端联调 | 全栈 | 全部B-*, F-* | 全部接口联调通过 |
| T-02 | iOS构建打包 | 前端 | T-01 | 生成.ipa并通过TestFlight分发 |
| T-03 | TestFlight内部测试（3-5人） | 测试 | T-02 | 测试报告+bug清单 |
| T-04 | Bug修复 | 前端+后端 | T-03 | 阻断性bug清零 |
| C-06 | NLP-B-03/NLP-B-04课程内容 | 内容 | C-01 | 2门课程内容入库 |
| C-07 | 5个精选案例内容 | 内容 | - | 原创案例+深度解析 |

---

## 阶段2：内容扩展 + AI深度应用（W11-W17，9.8 - 10.26）

### W11-W13（9.8 - 9.28）内容批量生产

| 任务ID | 任务 | 负责人 | 交付物 |
|--------|------|--------|--------|
| C-08 | 进阶6门课程内容撰写 | NLP教练+内容编辑 | 6门×~10课时=60课时 |
| C-09 | 高级4门课程内容撰写 | NLP教练+内容编辑 | 4门×~12课时=50课时 |
| C-10 | 50场景详细角色设定 | NLP教练+内容编辑 | 50场景完整描述+角色Prompt+开场白 |
| C-11 | 60+案例库撰写 | NLP教练+内容编辑 | 60个原创案例+深度解析 |
| F-21 | 案例列表+详情页 | 前端 | CaseListScreen + CaseDetailScreen |
| F-22 | 高级训练页面（心锚/次感元/语言模式） | 前端 | AnchorScreen + SubmodalityScreen + LanguageScreen |
| B-17 | 案例API | 后端 | GET /cases, /cases/{id} |
| B-18 | 高级训练API | 后端 | POST /training/anchor, /training/language |

### W14-W15（9.29 - 10.12）AI深度应用

| 任务ID | 任务 | 负责人 | 交付物 |
|--------|------|--------|--------|
| B-19 | AI信念挖掘器 | 后端 | 信念识别+结构分析+转化引导Prompt |
| F-23 | AI信念挖掘器页面 | 前端 | BeliefMiningScreen：输入困扰→AI分析→信念转化 |
| B-20 | AI引导式冥想脚本生成 | 后端 | 动态冥想引导词生成+TTS集成 |
| F-24 | 冥想引导页面 | 前端 | MeditationScreen：AI生成引导词+语音+动效 |
| B-21 | AI梦境日记 | 后端 | 梦境NLP次感元分析Prompt |
| F-25 | 梦境日记页面 | 前端 | DreamJournalScreen：记录+AI分析 |
| F-26 | AI语音韵律分析 | 前端 | 角色扮演后可选语音分析入口 |
| B-22 | 语音文本分析API | 后端 | 分析用户用词偏好的VAKOG倾向 |

### W16-W17（10.13 - 10.26）联调+性能+测试

| 任务ID | 任务 | 负责人 | 交付物 |
|--------|------|--------|--------|
| T-05 | 全部功能联调 | 全栈 | 第二阶段全量功能测试 |
| T-06 | 性能优化 | 前端+后端 | 页面加载<2s，AI响应P95<8s |
| T-07 | 内容质量审核 | NLP教练 | 全部内容专业审核通过 |
| T-08 | TestFlight v2分发测试 | 测试 | 用户反馈收集 |

---

## 阶段3：商业化闭环（W18-W21，10.27 - 11.23）

### W18-W19（10.27 - 11.9）会员系统+Apple内购

| 任务ID | 任务 | 负责人 | 交付物 |
|--------|------|--------|--------|
| B-23 | 会员方案API | 后端 | GET /membership/plans, /status, /upgrade |
| B-24 | 支付记录API | 后端 | POST /membership/upgrade记录支付 |
| B-25 | Apple IAP服务端验证 | 后端 | App Store Receipt验证 |
| F-27 | 会员中心页面 | 前端 | MembershipScreen：方案对比+购买按钮 |
| F-28 | Apple IAP集成 | 前端 | react-native-iap集成+沙盒测试 |
| F-29 | 会员权益判断逻辑 | 前端 | 功能入口的会员校验（课程锁/场景锁） |
| F-30 | 7天免费试用逻辑 | 前端+后端 | 新用户自动试用+到期提醒+降级 |
| 🆕 F-30a | Apple IAP强制披露文案 | 前端 | 会员购买页：自动续费说明+试用转付费+取消路径+价格确认 |
| 🆕 F-30b | 隐私政策/用户协议URL部署 | 全栈 | 可访问的HTTPS页面，会员购买页底部链接 |
| 🆕 P0-12 | Apple IAP合规自检 | 产品 | 对照审核指南3.1.1/3.1.2(a)/5.1.1逐项检查 |

### W20-W21（11.10 - 11.23）个性化+挑战赛+A/B测试

| 任务ID | 任务 | 负责人 | 交付物 |
|--------|------|--------|--------|
| B-26 | 自适应推荐引擎 | 后端 | 基于能力弱项的场景/训练推荐 |
| F-31 | 兴趣标签选择页 | 前端 | 注册后可选标签（职场/情感/成长/亲子/社交） |
| F-32 | 首页个性化内容排序 | 前端 | 根据标签+能力数据排序课程/场景 |
| F-33 | 每周挑战赛页面 | 前端 | WeeklyChallengeScreen+倒计时+奖励展示 |
| B-27 | 挑战赛API | 后端 | 挑战生成+完成验证+奖励发放 |
| B-28 | A/B测试框架 | 后端 | 分流+事件追踪基础架构 |

---

## 阶段4：打磨上线（W22-W25，11.24 - 12.21）

### W22-W23（11.24 - 12.7）技术优化

| 任务ID | 任务 | 负责人 | 交付物 |
|--------|------|--------|--------|
| F-34 | 离线模式 | 前端 | 课程缓存+训练本地暂存+联网同步 |
| F-35 | 加载骨架屏 | 前端 | AI等待场景的霓虹风格骨架屏 |
| F-36 | Bugly崩溃监控接入 | 前端 | iOS crash上报配置 |
| P0-10 | 隐私政策URL部署 | 全栈 | 可访问的HTTPS隐私政策页面 |
| P0-11 | 用户协议URL部署 | 全栈 | 可访问的HTTPS用户协议页面 |

### W24-W25（12.8 - 12.21）上架准备+审核递交

| 任务ID | 任务 | 负责人 | 交付物 |
|--------|------|--------|--------|
| S-01 | App Store Connect配置 | 产品 | App ID: com.mindshift.app + 内购产品创建 |
| S-02 | App截图制作（3种尺寸×5张） | 设计 | 6.7"+6.5"+5.5"截图 |
| S-03 | App元数据填写 | 产品 | 名称：念转 - NLP心智训练与AI角色扮演<br>副标题：一念之转，重塑心智<br>关键词：NLP训练,心智重塑,情绪管理,自我提升 |
| S-04 | 隐私营养标签填写 | 产品 | App Store隐私标签 |
| S-05 | APNs推送证书配置 | 后端 | 推送证书上传+验证 |
| S-06 | 最终TestFlight测试 | 测试 | 10+人外部测试 |
| S-07 | 审核递交 | 产品 | 提交App Store审核 |
| S-08 | 审核问题响应准备 | 产品 | 常见审核拒绝原因应对方案 |

---

## 阶段5：增长飞轮（W26-W32，12.22 - 2.7）

| 任务ID | 任务 | 负责人 | 周次 | 交付物 |
|--------|------|--------|------|--------|
| F-37 | 分享成就卡片生成 | 前端 | W26-W27 | 霓虹风格卡片+二维码+保存相册 |
| F-38 | 邀请奖励系统 | 前端+后端 | W27-W28 | 邀请码+双方奖励+追踪 |
| F-39 | 打卡挑战系统 | 前端+后端 | W28-W29 | 21/30天挑战+进度+徽章 |
| F-40 | 专家答疑模块 | 前端+后端 | W29-W30 | AI初答+人工补充回复 |
| F-41 | NLP免费公开课（AI主持） | 后端 | W30-W31 | 定时直播内容生成 |
| F-42 | 成长故事精选 | 前端 | W31-W32 | 用户故事展示页+投稿入口 |
| B-29 | 社区审核后台 | 后端 | W26-W28 | 审核面板+敏感词过滤 |
| B-30 | 数据分析仪表盘 | 后端 | W28-W30 | 用户增长/留存/付费漏斗 |

---

## 阶段6：多平台（W33-W42，2.8 - 4.18）

| 任务ID | 任务 | 负责人 | 周次 | 交付物 |
|--------|------|--------|------|--------|
| MP-01 | macOS UI适配 | 前端 | W33-W35 | 大屏布局+鼠标键盘交互 |
| MP-02 | macOS Catalyst构建 | 前端 | W35-W36 | macOS App包生成 |
| MP-03 | Mac App Store上架 | 产品 | W36-W37 | macOS商店审核递交 |
| MP-04 | Android UI适配 | 前端 | W37-W39 | 多种屏幕尺寸适配 |
| MP-05 | Android构建+测试 | 前端 | W39-W40 | APK/AAB生成+真机测试 |
| MP-06 | Google Play上架 | 产品 | W40-W41 | Google Play审核递交 |
| MP-07 | 多设备数据同步 | 后端 | W38-W40 | 云端同步服务（加密传输） |
| MP-08 | Windows版评估 | 产品 | W41-W42 | 市场分析+技术可行性报告 |

---

## 质量保障体系

### 各阶段质量门禁

| 阶段 | 质量门禁 | 通过标准 |
|------|----------|----------|
| 阶段0 | 设计评审 | 全部UI稿评审通过 |
| 阶段0 | 合规审查 | 用户协议+隐私政策+免责声明法务审核通过 |
| 阶段1 | TestFlight分发 | 3-5人内部测试，阻断性bug=0 |
| 阶段2 | 内容审核 | NLP教练审核全部课程+场景+案例 |
| 阶段2 | 性能基准 | 页面加载<2s，AI响应P95<8s |
| 阶段3 | IAP沙盒测试 | 内购全流程通过 |
| 阶段4 | App Store合规 | 通过审核指南自检清单 |
| 阶段4 | 崩溃率 | iOS crash rate <0.5% |

### 测试策略

| 测试类型 | 频率 | 工具 | 覆盖范围 |
|----------|------|------|----------|
| 单元测试 | 每次提交 | Jest + pytest | 核心业务逻辑 |
| 接口测试 | 每日构建 | httpx + pytest | 全部API endpoints |
| UI回归测试 | 每周 | 人工 | 核心用户旅程 |
| 性能测试 | 每阶段末 | 人工 + Instruments | 启动时间/内存/AI延迟 |
| 安全测试 | 阶段1/阶段4 | 人工 | 加密验证/数据泄露检测 |
| Beta测试 | 阶段1+4 | TestFlight | 10+外部用户 |

---

## 风险登记表

| 风险ID | 风险描述 | 概率 | 影响 | 缓解措施 | 负责人 |
|--------|----------|------|------|----------|--------|
| R-01 | NLP教练招聘延迟 | 中 | 高 | 提前启动招聘，预备2-3位候选人 | 产品 |
| R-02 | App Store审核被拒 | 中 | 高 | 提前研究审核指南4.2+5.1.1，准备申诉材料 | 产品 |
| R-03 | 智谱AI额度超限 | 低 | 中 | 监控使用量，预备阿里云百炼Qwen备用 | 后端 |
| R-04 | iOS版本兼容问题 | 中 | 中 | 参考NVC项目兼容矩阵，严格锁定依赖版本 | 前端 |
| R-05 | 内容生产速度不足 | 中 | 高 | 阶段0即启动内容撰写，NLP教练+编辑并行 | 内容 |
| R-06 | 版权纠纷 | 低 | 极高 | 严格执行原创内容+学理引用模式，法务预审 | 产品 |
| R-07 | 用户心理数据泄露 | 低 | 极高 | AES-256客户端加密，密钥不上传，定期安全审计 | 全栈 |

---

## 关键技术规格速查

### 前端核心依赖版本（锁定）

| 包名 | 版本 | 说明 |
|------|------|------|
| react-native | 0.74.5 | 框架主版本 |
| typescript | ^5.0 | 类型系统 |
| @react-navigation/native | ^7.0 | 导航核心 |
| @react-navigation/bottom-tabs | ^7.0 | 底部Tab |
| @react-navigation/stack | ^7.0 | Stack导航 |
| zustand | ^5.0 | 状态管理 |
| axios | ^1.18 | HTTP客户端 |
| react-native-reanimated | ^3.16 | 动画引擎 |
| react-native-linear-gradient | ^2.0 | 霓虹渐变 |
| react-native-vector-icons | ^10.0 | 图标库 |
| react-native-webview | ^13.0 | 课程内容渲染 |
| react-native-iap | ^12.0 | Apple内购 |
| @react-native-async-storage/async-storage | ^3.0 | 本地持久化 |
| react-native-push-notification | ^8.0 | 推送通知 |
| victory-native | ^41.0 | 雷达图/趋势图 |

### 后端核心依赖版本（锁定）

| 包名 | 版本 | 说明 |
|------|------|------|
| fastapi | ^0.111 | Web框架 |
| uvicorn | ^0.30 | ASGI服务器 |
| sqlalchemy[asyncio] | ^2.0 | ORM |
| aiosqlite | ^0.20 | 开发DB |
| asyncpg | ^0.29 | 生产DB驱动 |
| alembic | ^1.13 | 数据库迁移 |
| httpx | ^0.27 | AI API调用 |
| python-jose | ^3.3 | JWT |
| passlib[bcrypt] | ^1.7 | 密码哈希 |
| pydantic-settings | ^2.0 | 配置管理 |
| loguru | ^0.7 | 日志 |
| redis | ^5.0 | 缓存 |

### 数据库核心表清单

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| users | 用户认证 | email, hashed_password, nickname, stage |
| nlp_courses | NLP课程 | id, level, source, is_premium |
| nlp_lessons | 课时内容 | course_id, type, content, concepts, source_refs |
| nlp_training_records | 训练记录 | user_id, training_type, input_data, ai_result, overall_score |
| rp_scenarios | 角色扮演场景 | category, difficulty, nlp_techniques, role_prompt |
| rp_dialogue_sessions | 对话会话 | user_id, scenario_id, messages, nlp_score |
| nlp_cases | 案例库 | category, techniques_applied, source |
| nlp_skill_profiles | 用户能力画像 | 8维度能力分(0-100), streak_days |
| community_posts | 社区帖子 | user_id, content, topic_tags, likes |
| post_comments | 帖子评论 | post_id, user_id, content |
| checkins | 打卡记录 | user_id, date, streak_count |
| subscription_plans | 会员方案 | level, price_monthly, price_annually |
| memberships | 用户会员 | user_id, plan_id, status, expires_at |
| payment_records | 支付记录 | user_id, plan_id, amount, receipt_data |

---

> **文档版本**：v2.0
> **编制日期**：2026年6月30日
> **基于方案文档**：NLPCoach方案 v2.0（含七大优化章节）
