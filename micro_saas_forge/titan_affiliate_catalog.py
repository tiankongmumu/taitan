"""
TITAN Affiliate Catalog 💰
A central registry of all affiliate partnerships.
Used by the Engine to inject highly relevant contextual ads into the generated micro-SaaS tools.
"""

AFFILIATE_PROGRAMS = [
    {
        "id": "aliyun_ecs",
        "name": "阿里云 (Alibaba Cloud)",
        "tags": ["developer", "hosting", "database", "backend", "web", "server"],
        "ad_copy": "🚀 需要部署你的全栈项目？阿里云新老同享特惠服务器，低至 99元/年。",
        "badge_text": "Sponsored",
        "link": "https://www.aliyun.com/daily-act/ecs/activity_selection?userCode=shipmicro",
        "icon": "☁️"
    },
    {
        "id": "tencent_cloud",
        "name": "腾讯云 (Tencent Cloud)",
        "tags": ["developer", "hosting", "mini-program", "wechat"],
        "ad_copy": "⚡ 腾讯云轻量应用服务器，微信小程序/Web开发首选，点击领专属代金券。",
        "badge_text": "Sponsored",
        "link": "https://cloud.tencent.com/act/cps/redirect?redirect=1&from=shipmicro",
        "icon": "☁️"
    },
    {
        "id": "api2d",
        "name": "API2D (AI Proxy)",
        "tags": ["ai", "gpt", "claude", "prompt", "llm", "generator"],
        "ad_copy": "🤖 国内直连 GPT-4 / Claude 3！API2D 稳定中转接口，注册即赠测试额度。",
        "badge_text": "Recommended",
        "link": "https://api2d.com/",
        "icon": "🧠"
    },
    {
        "id": "feishu",
        "name": "飞书 (Feishu)",
        "tags": ["productivity", "team", "project management", "document", "office", "collaboration"],
        "ad_copy": "📝 还在用零散的工具管理项目？试试飞书，先进团队的协作利器。",
        "badge_text": "Ad",
        "link": "https://www.feishu.cn/",
        "icon": "💼"
    },
    {
        "id": "xiaobot",
        "name": "小报童",
        "tags": ["creator", "writing", "blog", "monetization", "newsletter", "markdown"],
        "ad_copy": "💰 想把你的知识变成被动收入？在小报童开通个人专栏，创作者拿 90% 收益！",
        "badge_text": "Creator Tools",
        "link": "https://xiaobot.net/",
        "icon": "📖"
    },
    {
        "id": "shipmicro",
        "name": "ShipMicro Pro",
        "tags": ["seo", "tools", "utility", "saas", "business", "default"],
        "ad_copy": "⚡ 喜欢这个工具？访问 ShipMicro 探索 50+ 个类似的免费效率神器。",
        "badge_text": "By Titan",
        "link": "https://shipmicro.com",
        "icon": "🚀"
    }
]
