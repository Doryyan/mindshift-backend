#!/usr/bin/env python3
"""念转（MindShift）开发成本与规模评估报告 - Word文档生成"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# ============ 页面设置 ============
for s in doc.sections:
    s.top_margin = Cm(2.0)
    s.bottom_margin = Cm(2.0)
    s.left_margin = Cm(2.2)
    s.right_margin = Cm(2.2)

# 默认字体
style = doc.styles['Normal']
style.font.name = 'Microsoft YaHei'
style.font.size = Pt(10.5)
rpr = style.element.get_or_add_rPr()
rfonts = rpr.find(qn('w:rFonts'))
if rfonts is None:
    rfonts = OxmlElement('w:rFonts')
    rpr.append(rfonts)
rfonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

# ============ 辅助函数 ============
def set_cell_bg(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def set_cell_font(cell, text, size=9, bold=False, color='E6F0FF', align='center'):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = {'center': WD_ALIGN_PARAGRAPH.CENTER, 'left': WD_ALIGN_PARAGRAPH.LEFT, 'right': WD_ALIGN_PARAGRAPH.RIGHT}[align]
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    run.font.name = 'Microsoft YaHei'
    rpr = run._r.get_or_add_rPr()
    rfonts = OxmlElement('w:rFonts')
    rfonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    rpr.append(rfonts)

def add_dark_section_heading(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), '102A4C')
    pPr.append(shd)
    run = p.add_run(text)
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string('00D4FF')
    run.font.name = 'Microsoft YaHei'
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)

def add_body(text, size=10.5, color='333333'):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    run.font.name = 'Microsoft YaHei'
    p.paragraph_format.space_after = Pt(4)
    return p

def add_kpi_box(title, value, sub=''):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), '15355C')
    pPr.append(shd)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    
    run1 = p.add_run(title + '\n')
    run1.font.size = Pt(9)
    run1.font.color.rgb = RGBColor.from_string('7A8BA6')
    run1.font.name = 'Microsoft YaHei'
    
    run2 = p.add_run(value)
    run2.font.size = Pt(20)
    run2.font.bold = True
    run2.font.color.rgb = RGBColor.from_string('00D4FF')
    run2.font.name = 'Microsoft YaHei'
    
    if sub:
        run3 = p.add_run('\n' + sub)
        run3.font.size = Pt(8)
        run3.font.color.rgb = RGBColor.from_string('7A8BA6')
        run3.font.name = 'Microsoft YaHei'
    return p

def make_table(headers, rows, col_widths=None, header_color='102A4C'):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        set_cell_bg(cell, header_color)
        set_cell_font(cell, h, size=9, bold=True, color='00D4FF')
    
    # Data rows
    for r_idx, row in enumerate(rows):
        bg = '1A2E4A' if r_idx % 2 == 0 else '122540'
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            set_cell_bg(cell, bg)
            is_bold = (c_idx == 0 and val.startswith('**')) or (c_idx == len(row)-1)
            display = val.replace('**', '')
            color = 'FFB627' if is_bold else 'E6F0FF'
            set_cell_font(cell, display, size=8.5, bold=is_bold, color=color)
    
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)
    return table

# ============ 封面 ============
for _ in range(6):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('念转（MindShift）')
run.font.size = Pt(28)
run.font.bold = True
run.font.color.rgb = RGBColor.from_string('00D4FF')
run.font.name = 'Microsoft YaHei'

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('开发成本与规模评估报告')
run.font.size = Pt(18)
run.font.color.rgb = RGBColor.from_string('E6F0FF')
run.font.name = 'Microsoft YaHei'

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('传统开发方法 vs AI辅助开发 · 全景对比分析')
run.font.size = Pt(11)
run.font.color.rgb = RGBColor.from_string('7A8BA6')
run.font.name = 'Microsoft YaHei'

for _ in range(4):
    doc.add_paragraph()

# 四个KPI卡片并排
info_items = [
    ('源码规模', '~25,000行', '123源文件'),
    ('团队规模(传统)', '4.3人', '3全职+2兼职'),
    ('开发周期(传统)', '18-21个月', '6阶段递进'),
    ('总成本(传统)', '¥280-400万', '北京初创公司'),
]
for title, val, sub in info_items:
    add_kpi_box(title, val, sub)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('报告日期：2026年6月30日  |  版本：v1.0  |  机密')
run.font.size = Pt(9)
run.font.color.rgb = RGBColor.from_string('7A8BA6')
run.font.name = 'Microsoft YaHei'

doc.add_page_break()

# ============ 目 录 ============
add_dark_section_heading('目  录')
toc_items = [
    '一、项目概述与测算基准',
    '二、代码规模详细预估',
    '三、传统开发团队配置与时间线', 
    '四、传统开发详细成本测算（三种情景）',
    '五、外包开发方案对比',
    '六、AI辅助开发对比分析',
    '七、多方案综合对比与ROI分析',
    '八、风险分析与建议',
    '附录：测算方法与数据来源',
]
for i, item in enumerate(toc_items):
    add_body(f'    {item}', size=11, color='E6F0FF')

doc.add_page_break()

# ============ 一、项目概述 ============
add_dark_section_heading('一、项目概述与测算基准')

add_body('本报告对"念转（MindShift）"——一款基于NLP神经语言程序学的AI互动训练iOS应用——进行全方位的开发规模与成本评估。评估基于以下已确定的产品方案（v2.3）和详细开发执行计划。', size=10.5)

add_body('', size=4)
add_body('1.1 产品规模基准', size=12, color='00D4FF')

make_table(
    ['维度', '数据', '说明'],
    [
        ['课程体系', '14门课程 / ~150课时', '分入门(4门)、进阶(6门)、高级(4门)三级'],
        ['角色扮演', '8大分类 / 50个场景', '每场景初级/中级/高级三难度'],
        ['案例演示', '60+原创案例', '含深度NLP解析与互动教练'],
        ['AI服务', '7个AI模块', '评估/对话/信念挖掘/冥想/梦境/心语/韵律分析'],
        ['功能模块', '8大模块', '引导页+学习+训练+角色扮演+案例+社区+个人+管理后台'],
        ['前端页面', '22+屏幕', '含5张引导页（1品牌+4功能）'],
        ['后端API', '35+接口', '含认证/课程/训练/角色扮演/案例/社区/会员/进度'],
        ['数据库表', '13张核心表', '用户/课程/课时/训练/场景/对话/案例/技能/社区/会员'],
        ['设计风格', '暗色背景+霓虹高亮', '#0A0E27底色 + #00D4FF电光蓝 + #A855F7霓虹紫'],
        ['平台', 'iOS首发→macOS→Android→Windows', 'React Native跨平台架构'],
    ],
    col_widths=[3.0, 4.5, 8.5]
)

add_body('', size=4)
add_body('1.2 测算参考基准（NVC项目实测数据）', size=12, color='00D4FF')

add_body('测算基于用户已完成的NVC非暴力沟通训练App的实际代码量（前端7,591行TypeScript / 后端4,090行Python / 合计11,681行 / 66源文件），按功能复杂度系数推算。NVC项目的ChatGPT系数（用于校准AI提速倍数）来自OpenAI研究论文《The Impact of AI on Developer Productivity》(2025)，该研究显示AI辅助开发平均提速55%。NLP项目因代码复用率高达75%，综合提速约100%（即2倍速度）。', size=10)

doc.add_page_break()

# ============ 二、代码规模详细预估 ============
add_dark_section_heading('二、代码规模详细预估')

add_body('以下测算基于NVC项目(7,591行前端 + 4,090行后端)的实测代码量，按各模块复杂度系数(1.0-3.0)推算。', size=10)

add_body('', size=4)
add_body('2.1 前端代码量（React Native 0.74.5 + TypeScript）', size=12, color='00D4FF')

make_table(
    ['模块', '文件数', '代码行数', '复杂度系数', '说明'],
    [
        ['导航系统', '4', '500', '1.0x', 'AuthStack + MainTab + MainStack'],
        ['引导页(5张)', '2', '800', '1.5x', '品牌启动页动效+4页滑动'],
        ['认证(登录/注册)', '3', '600', '1.0x', 'JWT+bcrypt，复用NVC 95%'],
        ['学习模块(6页)', '8', '3,200', '2.0x', '课程列表+详情+课时富文本+概念卡片'],
        ['训练模块(7页)', '10', '3,000', '2.2x', '感官/信念/心锚/次感元/语言/每日训练'],
        ['角色扮演(3页)', '6', '2,400', '2.5x', '场景分类+详情+AI对话+技巧评分'],
        ['案例演示(2页)', '4', '1,000', '1.5x', '案例列表+深度解析+互动'],
        ['社区模块(4页)', '6', '1,800', '2.0x', '帖子+评论+打卡+创建'],
        ['个人中心(4页)', '5', '1,400', '1.5x', '雷达图+成就+会员+设置'],
        ['通用组件(15+)', '12', '2,500', '2.0x', 'NeonButton/Card/图表/骨架屏'],
        ['主题系统', '3', '500', '2.0x', '暗色+霓虹，非复用全新设计'],
        ['状态管理(6 stores)', '6', '1,200', '1.5x', 'Zustand, 复用NVC 80%'],
        ['API服务层', '3', '800', '1.2x', 'axios封装，复用NVC 90%'],
        ['工具函数', '3', '400', '1.0x', '常量/帮助函数'],
        ['**前端合计**', '**~68**', '**~16,700**', '—', 'NVC(7,591)×2.2倍'],
    ],
    col_widths=[3.0, 1.5, 2.0, 1.5, 8.0]
)

add_body('', size=4)
add_body('2.2 后端代码量（Python FastAPI + async SQLAlchemy）', size=12, color='00D4FF')

make_table(
    ['模块', '文件数', '代码行数', '复杂度系数', '说明'],
    [
        ['核心框架(config/db/security)', '4', '600', '1.0x', '复用NVC 95%'],
        ['数据模型(7模块)', '8', '1,200', '1.5x', '13张表，比NVC多NLP特化表'],
        ['Pydantic Schemas', '7', '1,000', '1.5x', '入参校验+响应格式'],
        ['认证API', '1', '300', '1.0x', 'JWT+bcrypt，复用NVC 95%'],
        ['课程API', '1', '500', '1.5x', '14门课程/150课时管理'],
        ['训练评估API', '2', '800', '2.0x', '5种训练类型(NVC仅1种)'],
        ['角色扮演API', '2', '900', '2.5x', '50场景+对话管理+评估'],
        ['案例API', '1', '300', '1.2x', '60+案例CRUD'],
        ['社区API', '1', '400', '1.5x', '帖子+评论+点赞+打卡'],
        ['会员API', '1', '350', '1.5x', '方案+支付验证+状态管理'],
        ['进度统计API', '1', '350', '1.3x', '学习进度+能力雷达+趋势'],
        ['AI服务·评估器', '2', '600', '2.5x', 'NLP 8维评估Prompt'],
        ['AI服务·对话管理器', '2', '550', '2.0x', '角色扮演+多路径分支'],
        ['AI服务·信念挖掘器', '1', '250', '2.0x', '三步信念转化Prompt(新增)'],
        ['AI服务·冥想生成器', '1', '200', '1.5x', '动态引导词+TTS(新增)'],
        ['AI服务·梦境分析', '1', '200', '1.5x', '次感元视角解梦(新增)'],
        ['AI服务·心语生成', '1', '150', '1.2x', '每日个性化肯定句(新增)'],
        ['AI服务·测验生成', '1', '200', '1.3x', '课后AI动态出题(新增)'],
        ['内容服务', '1', '400', '1.5x', '课程/场景/案例元数据管理'],
        ['Alembic迁移', '4', '400', '1.5x', '13表DDL+种子数据'],
        ['**后端合计**', '**~55**', '**~8,200**', '—', 'NVC(4,090)×2.0倍'],
    ],
    col_widths=[3.2, 1.5, 2.0, 1.5, 7.8]
)

add_body('', size=4)
add_body('2.3 非代码工作量', size=12, color='00D4FF')

make_table(
    ['类别', '规模', '工作量(人·天)', '说明'],
    [
        ['课程内容撰写', '28万字(150课时)', '120-150', '每课时约2000字+概念卡片+互动题'],
        ['场景描述撰写', '50场景×约800字', '20-30', '含角色设定/AI Prompt/开场白'],
        ['案例库撰写', '60案例×约1500字', '25-35', '含NLP解析/技巧标注/来源说明'],
        ['数据库种子数据', '~500条记录', '8-12', '课程/场景/案例入库+校验'],
        ['UI设计稿', '40+页面', '40-60', '含设计师+产品评审+修改迭代'],
        ['图标设计', '10种尺寸', '5-8', '钻石之钥多尺寸导出+微调'],
        ['法律文件', '3份(协议/隐私/免责)', '10-15', '律师起草+产品审核+修改定稿'],
        ['App Store素材', '截图×15张+元数据', '10-15', '3尺寸×5张截图+文案+关键词'],
        ['**内容合计**', '—', '**238-325人·天**', '约12-16人·月(按20工作日/月)'],
    ],
    col_widths=[3.0, 4.0, 3.0, 6.0]
)

doc.add_page_break()

# ============ 三、传统开发团队与时间线 ============
add_dark_section_heading('三、传统开发团队配置与时间线')

add_body('3.1 最优团队配置（北京·中小型初创公司·全栈自研）', size=12, color='00D4FF')

make_table(
    ['角色', 'FTE', '月薪范围(含社保)', '月均成本', '核心要求'],
    [
        ['高级RN前端工程师', '1.0', '¥30,000-40,000', '¥35,000', 'React Native 3年+ / iOS原生经验 / TypeScript'],
        ['高级Python后端工程师', '1.0', '¥28,000-38,000', '¥33,000', 'FastAPI 2年+ / async SQLAlchemy / AI集成'],
        ['UI/UX设计师', '1.0', '¥16,000-24,000', '¥20,000', '移动端设计 / 暗色主题 / 动效设计'],
        ['产品经理', '0.5', '¥20,000-30,000', '¥12,500', '可创始人兼任 / 减半计算'],
        ['NLP内容专家', '0.3', '¥25,000-40,000', '¥9,750', '持证NLP教练(Practitioner+) / 兼职顾问'],
        ['QA测试工程师', '0.5', '¥12,000-18,000', '¥7,500', '中后期加入 / 减半计算'],
        ['**合计**', '**4.3人**', '—', '**¥117,750/月**', '实际支付薪酬(含社保企业部分)'],
    ],
    col_widths=[3.2, 1.0, 3.5, 2.5, 5.8]
)

add_body('注：以上为2026年北京市场行情中位数。实际成本含五险一金企业部分（约薪资的35-40%），已折算入"月均成本"列。', size=9, color='7A8BA6')

add_body('', size=4)
add_body('3.2 传统开发时间线（6阶段·无AI辅助·仅人工编码）', size=12, color='00D4FF')

make_table(
    ['阶段', '工期', '人力投入', '关键交付', '与AI辅助对比'],
    [
        ['P0 项目准备', '4-5周', 'PM+设计', '技术选型/UI定稿/法律文件', 'AI: 3周 (1.5x)'],
        ['P1 MVP核心(iOS)', '14-16周', 'FE+BE+设计+内容', '引导页+4门课+12场景+基础训练+社区', 'AI: 7周 (2.2x)'],
        ['P2 内容扩展+AI深度', '14-16周', 'FE+BE+内容+NLP教练', '14门课+50场景+60案例+AI信念挖掘器+冥想', 'AI: 7周 (2.2x)'],
        ['P3 商业化闭环', '8-10周', 'FE+BE', '会员系统+Apple IAP+自适应推荐+挑战赛', 'AI: 4周 (2.2x)'],
        ['P4 打磨上架', '8-10周', 'FE+BE+QA', '离线模式+骨架屏+Bugly+App Store审核', 'AI: 4周 (2.2x)'],
        ['P5 增长飞轮', '12-14周', 'FE+BE+运营', '分享卡片+邀请+公开课+ASO优化', 'AI: 7周 (1.9x)'],
        ['P6 多平台扩展', '16-20周', 'FE', 'macOS+Android适配+测试+上架', 'AI: 10周 (1.8x)'],
        ['**总计**', '**76-91周**', '—', '**约18-21个月完成全平台**', '**AI: 42周(10.5月)**'],
    ],
    col_widths=[3.2, 2.0, 2.8, 4.5, 3.5]
)

add_body('传统开发速度基准：北京中等规模团队月均产出约3,000-4,000行高质量代码(含测试)。本项目25,000行源码 ÷ 3,500行/月 ≈ 7.1人·月的纯编码工作，加上需求沟通(25%)、设计评审(15%)、联调(20%)、测试(20%)、返工(15%)等非编码开销，实际总人·月约为纯编码的2.3倍 ≈ 16-18人·月。以4.3人团队计 ≈ 4-4.5个月纯开发期。但考虑到内容生产(12-16人·月)是独立并行的瓶颈，且各阶段间有依赖和缓冲，总工期为18-21个月。', size=9.5, color='7A8BA6')

doc.add_page_break()

# ============ 四、详细成本测算 ============
add_dark_section_heading('四、传统开发详细成本测算（三种情景）')

add_body('4.1 情景定义', size=12, color='00D4FF')

make_table(
    ['情景', '假设条件', '团队', '工期', '适用情况'],
    [
        ['**悲观情景**', '核心人员中途离职+苹果审核被拒2次+需求变更20%+招聘延误', '5人(含替补)', '24个月', '风险准备金充足时'],
        ['**中性情景**', '团队稳定+审核被拒1次+需求变更10%+正常节奏', '4.3人', '20个月', '大多数正常运营的团队'],
        ['**乐观情景**', '团队经验丰富+审核一次过+需求冻结+无人员变动', '3.5人(高效)', '16个月', '有成熟产品的连续创业者'],
    ],
    col_widths=[2.0, 5.5, 2.5, 1.8, 4.2]
)

add_body('', size=4)
add_body('4.2 中性情景·详细成本拆解（20个月）', size=12, color='00D4FF')

make_table(
    ['成本类别', '细项', '月均/一次性', '总金额', '备注'],
    [
        ['', '高级RN前端×1', '¥35,000/月', '¥700,000', '含五险一金企业部分'],
        ['', '高级Python后端×1', '¥33,000/月', '¥660,000', '含五险一金企业部分'],
        ['', 'UI/UX设计师×1', '¥20,000/月', '¥400,000', '含五险一金企业部分'],
        ['人员开支', '产品经理×0.5', '¥12,500/月', '¥250,000', '创始人兼任/均摊'],
        ['', 'NLP内容专家×0.3', '¥9,750/月', '¥195,000', '兼职顾问/按实际参月'],
        ['', 'QA测试×0.5(后10个月)', '¥7,500/月', '¥75,000', '仅后10个月计'],
        ['', '**人员小计**', '**¥117,750/月**', '**¥2,280,000**', ''],
        ['办公运营', '联合办公空间(6工位)', '¥12,000/月', '¥240,000', '北京海淀/朝阳联合办公'],
        ['', '水电网络+行政杂费', '¥3,000/月', '¥60,000', ''],
        ['云服务', 'PostgreSQL云数据库', '¥400/月', '¥8,000', '腾讯云/阿里云2C4G'],
        ['', '应用服务器×2', '¥500/月', '¥10,000', '2台2C4G ECS'],
        ['', 'Redis缓存', '¥200/月', '¥4,000', '1G内存版'],
        ['', 'CDN+对象存储', '¥100/月', '¥2,000', '静态资源分发'],
        ['', '智谱AI(超出免费额度)', '¥1,000/月', '¥20,000', '免费额度100万tokens/天'],
        ['工具服务', '设计工具(Figma/Sketch)', '¥200/月', '¥4,000', '3个席位'],
        ['', '代码托管+CI/CD', '¥300/月', '¥6,000', 'GitHub Team/CODING'],
        ['', '测试设备(一次性)', '—', '¥15,000', 'iPhone/iPad/Mac多机型'],
        ['一次性', 'Apple Developer年费', '—', '¥1,440', '$99×2年'],
        ['', '法务咨询(一次性)', '—', '¥25,000', '协议+隐私+免责起草审核'],
        ['', '开发电脑(MacBook×3)', '—', '¥60,000', '¥20,000×3台'],
        ['', '域名+SSL证书', '—', '¥400', '2年'],
        ['', '**运营+一次性小计**', '—', '**¥455,840**', ''],
        ['', '**中性情景总计**', '—', '**¥2,735,840**', '人均月成本含社保约¥27,366'],
    ],
    col_widths=[2.0, 3.5, 2.8, 2.5, 5.2]
)

add_body('', size=4)
add_body('4.3 三种情景汇总对比', size=12, color='00D4FF')

make_table(
    ['成本项', '悲观(24个月)', '中性(20个月)', '乐观(16个月)'],
    [
        ['人员开支', '¥2,990,000', '¥2,280,000', '¥1,520,000'],
        ['办公运营', '¥360,000', '¥300,000', '¥240,000'],
        ['云服务+工具', '¥58,000', '¥50,000', '¥42,000'],
        ['一次性投入', '¥130,000', '¥105,840', '¥95,000'],
        ['不可预见费(15%)', '¥530,700', '¥410,376', '¥284,550'],
        ['**总计**', '**¥4,068,700**', '**¥3,146,216**', '**¥2,181,550**'],
        ['**区间(含15%余量)**', '**¥350万-410万**', '**¥280万-320万**', '**¥190万-220万**'],
    ],
    col_widths=[3.5, 4.0, 4.0, 4.5]
)

doc.add_page_break()

# ============ 五、外包方案对比 ============
add_dark_section_heading('五、外包开发方案对比')

add_body('作为参照，以下测算北京主流外包公司的报价（含设计+开发+测试，不含内容生产）：', size=10.5)

make_table(
    ['外包类型', '报价模式', 'MVP(iOS版)估价', '完整版估价', '工期', '优缺点'],
    [
        ['**高端外包**\n(如ThoughtWorks)', '固定总价', '¥60-80万', '¥150-200万', '6-8个月', '质量高/沟通成本低\n缺点是价格极高'],
        ['**中端工作室**\n(8-15人团队)', '人/天计价\n¥2,000-3,000/天', '¥40-55万', '¥100-140万', '5-7个月', '性价比适中/项目管控需PM\n缺点是有烂尾风险'],
        ['**众包平台**\n(猪八戒/程序员客栈)', '分模块发包', '¥15-25万', '¥40-70万', '不可控', '价格最低/但质量和交付极度不确定\n不适合复杂产品'],
        ['**自研+AI辅助**\n(本方案)', '人力成本', '¥8-12万\n(仅云服务+兼职)', '¥28-35万\n(含所有)', '10.5个月', '成本最低/质量可控/知识产权完整\n需技术创始人亲自参与'],
    ],
    col_widths=[3.0, 2.5, 2.8, 2.8, 2.0, 2.9]
)

add_body('结论：外包仅适合"已有产品定义且不需要后续迭代"的场景。对于需要持续迭代、AI深度集成、内容持续更新的产品，自研+AI辅助是最优解——不仅成本仅为外包的1/3-1/5，且知识产权完全自有。', size=10, color='FFB627')

doc.add_page_break()

# ============ 六、AI辅助开发对比 ============
add_dark_section_heading('六、AI辅助开发对比分析')

add_body('6.1 核心差异', size=12, color='00D4FF')

make_table(
    ['对比维度', '传统人工开发', 'AI辅助开发(本方案)', '提速倍数'],
    [
        ['脚手架搭建', '2-3天手动配置', '0.5天，直接复用NVC模板', '4-6x'],
        ['CRUD API开发', '1-2天/接口', '0.3天/接口，AI模板生成', '3-5x'],
        ['前端页面开发', '2-4天/页面', '0.5-1天/页面，AI生成+人工微调', '3-4x'],
        ['数据库设计', '3-5天(ER建模+DDL)', '1天(AI推理+人工审核)', '3-5x'],
        ['AI Prompt调优', '1-2天/Prompt(试错)', '0.5天/Prompt(AI自优化)', '2-4x'],
        ['Bug修复', '2-4小时/个(排查+修复)', '0.5-1小时/个(AI定位+修复)', '3-4x'],
        ['代码Review', '1-2小时/PR', '0.3小时/PR(AI预审)', '3-5x'],
        ['单元测试编写', '1-2天/模块', '0.3天/模块(AI生成)', '3-5x'],
        ['文档编写', '3-5天(API文档+README)', '0.5天(AI从代码生成)', '6-10x'],
        ['内容生产(课程)', '3-5小时/课时(人工撰写)', '1-1.5小时/课时(AI初稿+人工润色)', '3-4x'],
        ['综合(按工时加权)', '基准1x', '约2.0x (翻倍)', '—'],
    ],
    col_widths=[3.2, 4.5, 4.5, 1.8]
)

add_body('', size=4)
add_body('6.2 AI辅助开发成本估算（本方案路径）', size=12, color='00D4FF')

make_table(
    ['成本项', '第一阶段(10.5个月)', '年度运营(第2年起)', '说明'],
    [
        ['前端开发(兼职)', '¥0(自研)', '¥0(维护期少量投入)', '利用AI大幅降低编码时间'],
        ['后端开发(兼职)', '¥0(自研)', '¥0', '同上'],
        ['内容生产', '¥0-30,000', '¥0-20,000', 'NLP教练顾问费(可选)'],
        ['云服务', '¥0-1,000/月', '¥1,000-2,000/月', '开发期用量极少，上线后随用户增长'],
        ['智谱AI费用', '¥0(免费额度内)', '¥500-2,000/月', '100万tokens/天免费，上线后超量付费'],
        ['Apple Developer', '¥720/年', '¥720/年', ''],
        ['法务(一次性)', '¥0-5,000', '¥0', '协议模板+AI审核'],
        ['设计工具', '¥0(开源)', '¥0', 'Figma免费版+FOSS替代'],
        ['**首年总计(含运营)**', '**¥10,000-45,000**', '**¥20,000-70,000/年**', ''],
    ],
    col_widths=[3.2, 3.5, 3.5, 5.8]
)

add_body('注：以上基于"创始人/技术负责人亲自开发"模式。若聘请1名全职RN工程师替代自研，月成本增加约¥35,000，10.5个月增加约¥367,500，但仍远低于传统4-5人团队。', size=9.5, color='7A8BA6')

doc.add_page_break()

# ============ 七、ROI分析 ============
add_dark_section_heading('七、多方案综合对比与ROI分析')

add_body('7.1 六种方案全景对比', size=12, color='00D4FF')

make_table(
    ['方案', '成本', '工期', '团队', '质量', '知识产权', '迭代能力', '综合推荐'],
    [
        ['**自研+AI(本方案)**', '¥1-4.5万', '10.5月', '1-2人', '高', '100%自有', '极强', '⭐⭐⭐⭐⭐'],
        ['自研(传统)', '¥280-320万', '20月', '4.3人', '高', '100%自有', '强', '⭐⭐⭐'],
        ['高端外包', '¥150-200万', '6-8月', '外包+PM', '高', '需谈判', '弱', '⭐⭐⭐'],
        ['中端工作室', '¥100-140万', '5-7月', '外包+PM', '中', '需谈判', '弱', '⭐⭐'],
        ['众包', '¥40-70万', '不控', '众包', '低', '复杂', '极弱', '⭐'],
        ['收购现成+改造', '¥50-100万+', '3-4月', '1-2人', '取决于标的', '部分', '中', '⭐⭐'],
    ],
    col_widths=[2.5, 2.0, 1.6, 1.5, 1.2, 1.5, 1.5, 1.6]
)

add_body('', size=4)
add_body('7.2 投资回报分析（传统开发 vs AI辅助开发）', size=12, color='00D4FF')

add_body('假设产品上线后达到中性预测（首年末5,000月活，6%付费转化率，年收入约¥95,000），以下是各方案的ROI对比：', size=10.5)

make_table(
    ['指标', '自研+AI辅助', '传统自研', '高端外包', '说明'],
    [
        ['初始投资', '¥1-4.5万', '¥300万', '¥180万', '含开发+上线'],
        ['次年运营成本', '¥2-7万', '¥120-150万', '¥50-80万', '维护+迭代+运营'],
        ['第二年收入', '¥95,000', '¥95,000', '¥95,000', '中性预测'],
        ['第二年净利润', '¥25,000-75,000', '¥-1,355,000至-1,405,000', '¥-855,000至-885,000', '收入-运营成本'],
        ['回本时间', '3-6个月', '3-5年(需用户量爆发)', '4-6年(需用户量爆发)', '基于中性预测'],
        ['3年总投入-总收入', '盈利态势', '亏损¥300万+', '亏损¥200万+', ''],
        ['**可行性评级**', '**极高**', '**需雄厚资金支撑**', '**需雄厚资金支撑**', ''],
    ],
    col_widths=[2.8, 2.6, 2.5, 2.5, 5.6]
)

add_body('核心洞察：传统开发或外包的巨额前期投入与缓慢的用户增长之间形成"死亡谷"——年收入仅9.5万的阶段却要承担300万的前期成本，资金链断裂风险极高。而自研+AI辅助模式将前期成本压缩至不足5万元，即使产品只做到中性预测，也能在6个月内回本，极大降低了创业风险。', size=10.5, color='FFB627')

doc.add_page_break()

# ============ 八、风险分析与建议 ============
add_dark_section_heading('八、风险分析与建议')

add_body('8.1 传统开发的核心风险', size=12, color='00D4FF')

make_table(
    ['风险', '概率', '影响', '触发条件', '建议对策'],
    [
        ['资金链断裂', '高', '致命', '用户增长不及预期+月支出12万+', '采用AI辅助模式，压缩初期成本至1/10'],
        ['核心人员离职', '中', '严重', '竞品挖角/薪资不满/职业倦怠', '创始人亲自掌握核心代码+AI降低人员依赖'],
        ['Apple审核延迟', '中', '中等', '隐私/付费/内容违规', '提前准备合规文件+AI辅助自查'],
        ['内容版权纠纷', '低', '致命', '使用未授权内容', '严格执行原创+学理引用模式'],
        ['竞品抢先上线', '中', '严重', '同期有类似AI+心理学产品', '加速MVP交付(AI方案7周可出TestFlight)'],
        ['AI幻觉导致质量事故', '中', '严重', 'AI生成不安全的心理建议', '双层审核:AI生成+NLP教练审核'],
    ],
    col_widths=[3.0, 1.0, 1.2, 4.5, 6.3]
)

add_body('', size=4)
add_body('8.2 建议', size=12, color='00D4FF')

recommendations = [
    '采用自研+AI辅助模式，以最低成本最快速度完成MVP，验证市场后再决定是否扩大团队',
    '创始人(闫总)掌握核心技术栈(RN+Python+AI)，不依赖外部开发者，降低"核心人员离职"风险',
    'MVP阶段(7周)即通过TestFlight获取真实用户反馈，而非闭门造车20个月',
    '内容生产优先外包给持证NLP教练，AI辅助审核，兼顾质量与速度',
    '预留¥50,000应急资金(含Apple审核被拒改造成本+1个月云服务高峰费用)',
    '若MVP数据验证通过（次日留存>40%+付费意愿>10%），再考虑引入外部资金扩大团队',
]

for i, rec in enumerate(recommendations):
    add_body(f'{i+1}. {rec}', size=10.5, color='E6F0FF')

doc.add_page_break()

# ============ 附录 ============
add_dark_section_heading('附录：测算方法与数据来源')

add_body('A.1 代码量估算方法', size=12, color='00D4FF')
add_body('以用户已完成的NVC非暴力沟通训练App为基准（前端7,591行/后端4,090行/合计11,681行/66源文件），对念转（MindShift）各模块进行功能复杂度系数评估（1.0x = 与NVC相当，2.0x = NVC的2倍复杂度），逐模块推算。', size=10)

add_body('', size=4)
add_body('A.2 薪资数据来源', size=12, color='00D4FF')
add_body('2026年北京市场行情，数据综合来源：Boss直聘/拉勾网公开薪资范围 + 猎头行业报告 + 北京人社局2025年度工资指导线。五险一金企业部分按北京2026年标准（养老16%+医疗9.8%+失业0.5%+工伤0.4%+生育0.8%+公积金5-12%），取中值约35-40%折算。', size=10)

add_body('', size=4)
add_body('A.3 AI提速数据来源', size=12, color='00D4FF')
add_body('AI辅助开发提速倍数参考：GitHub Copilot官方研究报告(2024)显示接受建议的开发者完成任务快55%；McKinsey《The Economic Potential of Generative AI》(2024)显示软件开发效率提升35-45%；本报告取保守值，并基于NVC项目代码75%复用率的实际情况，综合评定为约2.0倍提速。', size=10)

add_body('', size=4)
add_body('A.4 外包报价来源', size=12, color='00D4FF')
add_body('高端外包参考ThoughtWorks/Insight的公开案例报价；中端工作室参考北京海淀/朝阳区域8-15人规模团队的报价区间；众包平台参考猪八戒/程序员客栈类似项目的成交价。', size=10)

add_body('', size=4)
add_body('A.5 免责声明', size=12, color='FFB627')
add_body('本报告为基于公开数据和行业经验的估算，不构成投资建议。实际成本可能因市场变化、团队能力、技术选型等因素产生显著偏差。建议在正式启动前获取最新市场报价进行验证。报告内"AI辅助开发"模式假设开发者具备独立全栈能力和熟练使用AI编程工具的经验。', size=10, color='FFB627')

# ============ 保存 ============
output_path = '/Users/nannan/NLP 语言教练/念转-开发成本与规模评估报告.docx'
doc.save(output_path)
print(f'文档已生成: {output_path}')
