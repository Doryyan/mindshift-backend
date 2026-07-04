# 念转（MindShift）- 项目长期记忆

## 项目基本信息
- **产品名称**：念转（MindShift）
- **项目代号**：MindShift
- **Bundle ID**：com.nianzhuan.mindshift（原 com.mindshift.app 已被占用）
- **App Store全称**：念转 - NLP心智训练与AI角色扮演
- **App Store副标题**：一念之转，重塑心智
- **图标**：钻石之钥（Diamond Key）—— 钻石主体+内部神经网格+钥匙杆齿
- **目标平台**：iOS App Store（首发）→ macOS → Windows → Android
- **技术栈**：React Native 0.74.5 + FastAPI + 智谱AI GLM-4-Flash + PostgreSQL
- **设计风格**：暗色背景(#0A0E27) + 霓虹高亮(#00D4FF电光蓝/#A855F7霓虹紫)

## 核心设计决策
- 内容来源：原创内容+学理引用模式（版权合规方案已定稿）
- 课程体系：14门课程/约150课时，分入门(4门)/进阶(6门)/高级(4门)三级
- 角色扮演：8大分类，50个场景，每个场景初级/中级/高级三难度
- 会员定价：基础198元/年，高级368元/年，7天免费试用，7天冻结卡
- 社区策略：MVP即上线每日打卡+心得分享
- 账号设计：单用户独立账号，后期支持多设备云端同步
- 代码复用：预计75%复用NVC项目代码
- 数据安全：用户心理数据AES-256-GCM客户端加密，密钥不上传
- AI深度应用：信念挖掘器+每日心语+引导冥想+梦境日记+韵律分析

## 开发项目位置
- 前端：/Users/nannan/NLP 语言教练/mindshift-app/ (67源文件 ~12,863行TS)
- 后端：/Users/nannan/NLP 语言教练/mindshift-backend/ (69源文件 ~6,397行Python)
- 测试：后端8文件465行 + 前端3文件
- 法律文件：mindshift-app/docs/ (3份用户协议/隐私政策/免责声明)
- App Store素材：mindshift-app/docs/AppStore/ (12份，覆盖iOS/macOS/Android/Windows)
- 合规页面：mindshift-app/public/ (3个HTML静态页面)
- 构建脚本：mindshift-app/scripts/ (3个跨平台构建/测试脚本)
- 方案文档 v2.3：/Users/nannan/.workbuddy/plans/toasty-aurora-curie.md
- 评估报告：/Users/nannan/NLP 语言教练/念转-开发成本与规模评估报告.docx

## 阶段总览
- 阶段0：项目准备 W1-W3（✅已完成）
- 阶段1：MVP核心 W4-W10（✅已完成）
- 阶段2：内容扩展 W11-W17（✅已完成）
- 阶段3：商业化 W18-W21（✅已完成）
- 阶段4：打磨上线 W22-W25（✅已完成）
- 阶段5：增长飞轮 W26-W32（✅已完成）
- 阶段6：多平台 W33-W42（✅已完成：macOS配置+Android适配+Windows评估+云端同步+跨平台脚本）

## 待办（优先级）
1. ⬜ iOS构建验证（Pod install + Xcode build）
2. ⬜ App Store Connect配置（App ID + 内购产品 + 推送证书）
3. ⬜ 部署隐私政策/用户协议HTTPS页面到生产域名
4. ⬜ App Store审核递交

## 待办（优先级）
1. ⬜ 配置真实智谱AI API Key（当前为占位符）
2. ⬜ 部署隐私政策/用户协议HTTPS页面
3. ⬜ iOS构建验证（Pod install + Xcode build）
4. ⬜ App Store Connect配置（App ID + 内购产品）

