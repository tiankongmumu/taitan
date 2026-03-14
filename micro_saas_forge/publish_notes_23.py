# -*- coding: utf-8 -*-
"""快速发布笔记2和3"""
import asyncio
import sys
sys.path.insert(0, r"d:\Project\1\micro_saas_forge")
from xhs_auto_publisher import publish_note

NOTE_2 = {
    "title": "这个找合伙人神器 我怎么没早点发现！🤝",
    "body": "一个人创业真的太孤独了😭\n每天写代码 做设计 搞运营 还要想着怎么赚钱\n感觉自己像个陀螺\n\n直到我发现了这些宝藏工具：\n\n1️⃣ CoFoundersLab - 全球创业者对接平台\n海量创业者简历 按技能/行业/阶段筛选\n\n2️⃣ YC Co-Founder Matching\nY Combinator 官方平台 质量超高\n\n3️⃣ Indie Hackers 社区\n独立开发者聚集地 找到志同道合的人\n\n💡 小Tips：找合伙人先从小项目合作开始\n别一上来就谈股份！先看能不能一起干活\n\n📌 更多创业工具合集 → shipmicro.com\n\n#创业 #找合伙人 #独立开发者 #SaaS #效率工具",
    "image": r"C:\Users\86136\.gemini\antigravity\brain\2463c55a-c7ba-49d7-b91c-00e8b4d2491c\xhs_note2_cover_1772598686698.png"
}

NOTE_3 = {
    "title": "做SaaS不懂GDPR？这个工具救命了 🛡️",
    "body": "姐妹们做出海SaaS的注意了⚠️\n不合规GDPR分分钟被罚几百万欧元\n我差点就踩坑了！\n\n后来找到了这些救命工具：\n\n🔒 Cookie Bot - 自动管理Cookie弹窗\n一行代码搞定 支持全球合规\n\n🛡️ OneTrust - 企业级隐私管理\n大公司都在用 免费版就够小团队\n\n📋 Termly - 隐私政策自动生成\n3分钟生成隐私政策+Cookie策略\n\n✅ 用了这些工具后\n我的SaaS终于合规了 安心上线！\n\n💡 这些工具的完整对比测评\n我写在了小报童专栏里 搜「Mumu效率工坊」\n\n📌 工具合集 → shipmicro.com\n\n#GDPR #隐私合规 #SaaS出海 #效率工具 #独立开发者",
    "image": r"C:\Users\86136\.gemini\antigravity\brain\2463c55a-c7ba-49d7-b91c-00e8b4d2491c\xhs_note3_cover_1772598703530.png"
}

async def main():
    print("=" * 50)
    print("📕 发布笔记 2: 找合伙人神器")
    print("=" * 50)
    ok2 = await publish_note(NOTE_2["title"], NOTE_2["body"], [NOTE_2["image"]])
    
    if ok2:
        print("\n⏳ 等待 30 秒避免频控...\n")
        await asyncio.sleep(30)
    
    print("=" * 50)
    print("📕 发布笔记 3: GDPR合规种草")
    print("=" * 50)
    ok3 = await publish_note(NOTE_3["title"], NOTE_3["body"], [NOTE_3["image"]])
    
    print("\n" + "=" * 50)
    r2 = "✅" if ok2 else "❌"
    r3 = "✅" if ok3 else "❌"
    print(f"结果: 笔记2 {r2} | 笔记3 {r3}")

if __name__ == "__main__":
    asyncio.run(main())
