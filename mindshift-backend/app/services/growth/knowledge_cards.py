from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

# 30 pre-written NLP knowledge cards
_KNOWLEDGE_CARDS: list[dict[str, str]] = [
    # VAKOG sensory systems
    {
        "topic": "感官系统",
        "title": "VAKOG 五大感知系统",
        "content": "视觉(V)、听觉(A)、感觉(K)、嗅觉(O)、味觉(G)构成我们的经验世界。觉察你偏好的感官通道，可以更有效地沟通和影响他人。",
        "quote": "思维通过感官来构建我们的内在世界。",
        "author": "理查·班德勒",
        "technique_name": "感官觉察",
        "practical_tip": "今天与3个人交谈时，留意他们使用的感官词汇(如\'看到\'、\'听到\'、\'感觉\')，尝试匹配对方的感官偏好。",
    },
    {
        "topic": "感官系统",
        "title": "视觉型 vs 听觉型 vs 感觉型",
        "content": "视觉型的人说话快、多用\u201c看\u201d类词汇；听觉型语速平稳、注重声音；感觉型说话慢、多身体感受词。识别后可建立更深亲和力。",
        "quote": "共鸣从觉察开始。",
        "author": "约翰·葛瑞德",
        "technique_name": "感官匹配",
        "practical_tip": "观察一位朋友说话时的眼睛移动方向——上方向是视觉，水平是听觉，下方是感觉。",
    },
    {
        "topic": "感官系统",
        "title": "次感元——感官的子属性",
        "content": "每种感官都有次感元：视觉有亮度/大小/距离，听觉有音量/音调/节奏，感觉有温度/压力/位置。改变次感元就能改变体验。",
        "quote": "次感元是心智的调色板。",
        "author": "NLP 核心原则",
        "technique_name": "次感元调整",
        "practical_tip": "回想一件让你紧张的事，在脑海中把画面变暗、变小、移到远处，感受情绪的变化。",
    },
    # Anchoring techniques
    {
        "topic": "锚定技巧",
        "title": "情绪锚的力量",
        "content": "锚定是一种条件反射技术，将特定的刺激（触碰、声音、词）与积极状态关联。随时触发锚点，即可快速进入理想状态。",
        "quote": "掌控你的状态，就能掌控你的命运。",
        "author": "安东尼·罗宾斯",
        "technique_name": "资源锚",
        "practical_tip": "找到一个你感到自信的时刻，在那个巅峰状态下，用力按住自己的手背，重复3次建立锚点。",
    },
    {
        "topic": "锚定技巧",
        "title": "叠锚——多重资源的叠加",
        "content": "将多种积极情绪状态（自信、平静、专注）依次锚定在同一触发点上，形成强大的\u201c叠锚\u201d，一次触发同时激活多种资源。",
        "quote": "叠加的力量远超单一资源。",
        "author": "NLP 进阶训练",
        "technique_name": "叠锚",
        "practical_tip": "在锚定\u201c自信\u201d后，再叠加\u201c放松\u201d状态在同一锚点上，感受两种状态的融合。",
    },
    {
        "topic": "锚定技巧",
        "title": "滑动锚——从负面到正面",
        "content": "将负面状态的锚点逐渐\u201c滑动\u201d转化为正面锚点。这是处理习惯性负面反应的有效技术，适合轻微情绪管理。",
        "quote": "转化而非对抗，是 NLP 的核心智慧。",
        "author": "NLP 实践指引",
        "technique_name": "滑动锚",
        "practical_tip": "识别一个你常有的轻微负面反应(如紧张)，找到一个相反的积极状态，练习将两者通过触碰桥接。",
    },
    # Reframing
    {
        "topic": "换框技术",
        "title": "意义换框——改变理解方式",
        "content": "\u201c我不是焦虑，我是身体在为重要的事做准备。\u201d 给同一个行为赋予不同的意义，情绪的体验就会改变。",
        "quote": "地图不是疆域——你对现实的解读不是现实本身。",
        "author": "阿尔弗雷德·柯日布斯基",
        "technique_name": "意义换框",
        "practical_tip": "找到一件你最近\u201c抱怨\u201d的事，写出3种不同的积极解读方式。",
    },
    {
        "topic": "换框技术",
        "title": "情境换框——换个场景看问题",
        "content": "\u201c我的倔强在对抗权威时是问题，但在坚持原则时是优点。\u201d 问自己：这个特质在什么情境下是有价值的？",
        "quote": "没有无用的行为，只有不合适的情境。",
        "author": "NLP 前提假设",
        "technique_name": "情境换框",
        "practical_tip": "列出你自认为的3个\u201c缺点\u201d，为每个找到至少一个它们能发挥积极作用的情境。",
    },
    {
        "topic": "换框技术",
        "title": "时间线换框——从未来看现在",
        "content": "想象5年后的自己回看今天的困境，你会怎么评价它？时间线换框能瞬间降低问题的压迫感，打开新的视角。",
        "quote": "所有的问题在更大的时间框架中都会找到解答。",
        "author": "泰德·詹姆斯",
        "technique_name": "时间线换框",
        "practical_tip": "闭上眼睛，想象5年后成功的自己，问\u201c他/她\u201d对今天这个困扰有什么建议。",
    },
    # Milton Model
    {
        "topic": "语言模式",
        "title": "米尔顿模型——模糊语言的魅力",
        "content": "使用模糊、开放的语言（如\u201c你可能会注意到一种变化\u201d）绕过意识的抗拒，直接与潜意识沟通，是催眠治疗的核心。",
        "quote": "模糊给了对方用自己的方式理解的空间。",
        "author": "米尔顿·艾瑞克森",
        "technique_name": "米尔顿模型",
        "practical_tip": "今天试着用\u201c你可能会发现...\u201d\u201c有些人自然地...\u201d这样开放的表达，观察对方的反应。",
    },
    {
        "topic": "语言模式",
        "title": "预设——巧妙植入前提",
        "content": "\u201c当你开始改变时，你会选择什么方式？\u201d 这句话预设了\u201c你会开始改变\u201d。预设是 NLP 中引导思维的高效工具。",
        "quote": "语言是思维的脚手架。",
        "author": "NLP 语言模型",
        "technique_name": "预设",
        "practical_tip": "设计3个包含积极预设的问句(如\u201c你学得这么快，下一个想掌握什么？\u201d)。",
    },
    {
        "topic": "语言模式",
        "title": "引述模式——借他人之口传递信息",
        "content": "\u201c我有个朋友曾告诉我，当你真正放松时，学习效率会翻倍。\u201d 通过引述间接传递信息，降低对方防备。",
        "quote": "善用故事和隐喻，比直接说教更有效。",
        "author": "米尔顿·艾瑞克森",
        "technique_name": "引述模式",
        "practical_tip": "找1个你想传达的观点，用一个\u201c朋友的故事\u201d来包装它，今天讲给一个人听。",
    },
    # Meta Model
    {
        "topic": "沟通技巧",
        "title": "元模型——澄清模糊的语言",
        "content": "当有人说\u201c我总是失败\u201d，问\u201c总是？每一次都如此吗？\u201d 元模型通过追问精确含义来挑战限制性概括。",
        "quote": "精准的语言带来精准的思维。",
        "author": "约翰·葛瑞德 & 理查·班德勒",
        "technique_name": "元模型提问",
        "practical_tip": "今天当听到\u201c永远/从不/所有人/没有人\u201d这些绝对化词汇时，温和地问一个澄清问题。",
    },
    {
        "topic": "沟通技巧",
        "title": "删除、扭曲、概括——语言的三大过滤机制",
        "content": "我们说话时自动进行了删除(省略信息)、扭曲(改变意义)、概括(归纳规则)。觉察这些模式，沟通更清晰。",
        "quote": "我们说的不是事实，只是我们对事实的删减、扭曲和概括。",
        "author": "NLP 沟通理论",
        "technique_name": "过滤觉察",
        "practical_tip": "复盘你今天说过的一句话，找出其中被删除/扭曲/概括的内容，还原完整信息。",
    },
    {
        "topic": "沟通技巧",
        "title": "流失逆转——补全被删除的信息",
        "content": "\u201c我很焦虑\u201d——问\u201c关于什么焦虑？\u201d \u201c他们不喜欢我\u201d——问\u201c具体是谁？\u201d 补全信息是打破内耗的有效方法。",
        "quote": "每一个模糊的表达背后都藏着改变的机会。",
        "author": "NLP 实践者手册",
        "technique_name": "信息补全",
        "practical_tip": "找自己一个\u201c内心声音\u201d(如\u201c我不够好\u201d)，用元模型追问直到获得具体的、可行动的信息。",
    },
    # Submodality
    {
        "topic": "感官系统",
        "title": "次感元映射——以感官改变体验",
        "content": "将愉快的次感元（明亮、温暖、近）映射到不愉快的记忆上，可以改变对过去的体验。这是 NLP 快速改变的核心技术之一。",
        "quote": "改变次感元，就是改变体验本身。",
        "author": "史蒂夫·安德里亚斯",
        "technique_name": "次感元映射",
        "practical_tip": "选一个轻度不愉快的记忆，用\u201c明亮、彩色、温暖、平静\u201d的次感元重新编码它，感受变化。",
    },
    {
        "topic": "感官系统",
        "title": "Swish 模式——快速改变习惯反应",
        "content": "在触发画面和理想状态画面之间建立一个快速的\u201c切换\u201d(Swish)，重复多次后，大脑自动从旧反应转向新反应。",
        "quote": "大脑喜欢高效——给它一个更好的选项。",
        "author": "理查·班德勒",
        "technique_name": "Swish 模式",
        "practical_tip": "想想一个你想改变的小习惯（如拖延），创建\u201c触发画面\u201d和\u201c行动画面\u201d，用 Swish 练习。",
    },
    # State management
    {
        "topic": "状态管理",
        "title": "状态是选择不是运气",
        "content": "NLP 的核心原则：你的状态由内在表征决定，你可以主动选择。改变呼吸、姿势、焦点，瞬间改变状态。",
        "quote": "卓越表现始于卓越状态。",
        "author": "安东尼·罗宾斯",
        "technique_name": "状态切换",
        "practical_tip": "下次感到低落时，挺直腰背、抬头、深呼吸3次、回忆一件开心的事——只需30秒改变状态。",
    },
    {
        "topic": "状态管理",
        "title": "心锚提取法——从过去借力量",
        "content": "回忆你人生中3个最有力量的时刻，提取其中的共同要素（姿势、呼吸、信念），创建你的\u201c心锚组合\u201d。",
        "quote": "你拥有你需要的所有资源。",
        "author": "NLP 前提假设",
        "technique_name": "心锚提取",
        "practical_tip": "写下3个你最自豪的成就，找出你在其中展现的核心品质，这些就是你随时可调用的资源。",
    },
    {
        "topic": "状态管理",
        "title": "清晨状态设定——一天的基调",
        "content": "醒来后的前5分钟决定了你一天的情绪基调。用一个简单的锚定仪式（深呼吸+积极画面+目标确认）设定状态。",
        "quote": "掌控早晨，就掌控了一天。",
        "author": "NLP 日常实践",
        "technique_name": "晨间仪式",
        "practical_tip": "明早醒来后，先不要看手机，做3次深呼吸、想象今天最理想的状态、说出一个积极目标。",
    },
    # Rapport building
    {
        "topic": "沟通技巧",
        "title": "镜像协调——建立深层亲和力",
        "content": "自然地匹配对方的身体姿势、呼吸节奏和语速，可以在潜意识层面建立信任和连接。关键是自然，而非模仿。",
        "quote": "亲和力是沟通的土壤。",
        "author": "NLP 亲和力原则",
        "technique_name": "镜像协调",
        "practical_tip": "在下次会议中，自然地匹配谈话对象的说话速度和坐姿，感受交流深度的变化。",
    },
    {
        "topic": "沟通技巧",
        "title": "节奏引领——从跟随到引导",
        "content": "先通过镜像匹配对方的节奏建立亲和力（跟随），然后逐渐改变自己的节奏（引领），对方会自然地跟上你。",
        "quote": "先加入对方的世界，再带他去新的地方。",
        "author": "NLP 沟通框架",
        "technique_name": "节奏引领",
        "practical_tip": "与一个情绪低落的人聊天时，先匹配他的语调和节奏，3分钟后逐渐变为更积极的语调。",
    },
    {
        "topic": "沟通技巧",
        "title": "回馈式倾听——让对方感到被理解",
        "content": "用自己的话复述对方的核心意思和情感，不是鹦鹉学舌，而是提炼和共情。这是建立信任最快的方式之一。",
        "quote": "被理解是人类最深层的需求之一。",
        "author": "卡尔·罗杰斯",
        "technique_name": "回馈式倾听",
        "practical_tip": "今天在倾听时，在回应前先复述对方的话\u201c所以你是说...\u201d，感受对话的变化。",
    },
    # More technique cards
    {
        "topic": "信念转化",
        "title": "信念审计——审视限制性信念",
        "content": "列出你内心深处关于自己的\u201c应该\u201d和\u201c不能\u201d。问：这是事实还是观点？这个信念在服务我还是限制我？",
        "quote": "你相信什么，你就能成为什么。",
        "author": "罗伯特·迪尔茨",
        "technique_name": "信念审计",
        "practical_tip": "写下3个以\u201c我不能...\u201d开头的信念，把每个改为\u201c我选择不...\u201d或\u201c我还没学会...\u201d，感受差别。",
    },
    {
        "topic": "信念转化",
        "title": "新信念植入——用体验打破旧信念",
        "content": "找到一个与你限制性信念相反的真实体验，在那个体验中充分沉浸，让它成为你新的\u201c反例证据库\u201d。",
        "quote": "一个真实的体验胜过一百个理性的争辩。",
        "author": "NLP 信念改变",
        "technique_name": "反例植入",
        "practical_tip": "找一个你\u201c不相信自己能做到\u201d的领域，找出至少一次你做得不错的真实经历，充分回忆那个具体场景。",
    },
    {
        "topic": "信念转化",
        "title": "六步换框——与内在部分对话",
        "content": "识别\u201c问题行为\u201d背后的正面意图，然后与内在部分协商找到3种更能满足这个意图的\u201c新行为\u201d。这是经典的 NLP 技术。",
        "quote": "每一个行为背后都有一个正面的意图。",
        "author": "NLP 前提假设",
        "technique_name": "六步换框",
        "practical_tip": "选一个你想改变的习惯，问自己：这个行为曾经保护过我什么？它想帮我达成什么？",
    },
    # Integration
    {
        "topic": "综合练习",
        "title": "NLP 整合——从技术到本能",
        "content": "NLP 的最终目标不是\u201c使用技术\u201d，而是将这些觉察和模式内化为自然的反应方式。练习到\u201c不需要想起\u201d。",
        "quote": "真正的精进是让技巧消失于无形。",
        "author": "NLP 精进指南",
        "technique_name": "内化练习",
        "practical_tip": "选一个你正在练习的 NLP 技术，今天在3个不同的情境中有意识地应用它。",
    },
    {
        "topic": "综合练习",
        "title": "觉察日记——成长的加速器",
        "content": "每天花5分钟记录：1个 NLP 觉察、1个成功应用、1个想尝试的技术。持续的自我觉察是 NLP 成长的核心。",
        "quote": "觉察是所有改变的第一步。",
        "author": "念转 MindShift",
        "technique_name": "觉察日记",
        "practical_tip": "从今天开始，每天睡前用手机记录一个 NLP 觉察，连续7天。",
    },
    {
        "topic": "综合练习",
        "title": "生态检查——你的改变是否和谐",
        "content": "在做出任何改变前，问自己：这个改变对生活的各个方面（工作、关系、健康、精神）有什么影响？确保改变是生态的。",
        "quote": "最好的改变是让整个系统变得更好的改变。",
        "author": "NLP 生态原则",
        "technique_name": "生态检查",
        "practical_tip": "对你想做的一个改变，画一个四象限(工作/关系/健康/精神)，评估改变的正面和潜在负面影响。",
    },
    {
        "topic": "综合练习",
        "title": "卓越圈——通往卓越的路径",
        "content": "在地板上画一个\u201c卓越圈\u201d，站在里面，回忆所有卓越体验，充分沉浸。走出圈子后，未来需要时随时站回去激活资源。",
        "quote": "卓越不是一种行为，而是一种习惯。",
        "author": "亚里士多德",
        "technique_name": "卓越圈",
        "practical_tip": "想象地上有一个圈，走进去时体会你最有力量的状态，走出来。练习3次后，下次需要时只需想象那个圈。",
    },
]


def get_daily_card() -> dict[str, Any]:
    """Get the daily NLP knowledge card.

    Uses date-based rotation through 30 pre-written cards.
    Returns: {topic, title, content, quote, author, technique_name, practical_tip}
    """
    today = datetime.now(timezone.utc).date()
    # Use date-based deterministic selection
    day_index = today.toordinal() % len(_KNOWLEDGE_CARDS)

    card = _KNOWLEDGE_CARDS[day_index]

    return {
        "topic": card["topic"],
        "title": card["title"],
        "content": card["content"],
        "quote": card["quote"],
        "author": card["author"],
        "technique_name": card["technique_name"],
        "practical_tip": card["practical_tip"],
        "date": today.isoformat(),
    }
