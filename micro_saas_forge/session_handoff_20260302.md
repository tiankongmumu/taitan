# TITAN Engine & ShipMicro — 完整会话核心交接文档

> **会话时间**: 2026-03-01 ~ 2026-03-02
> **用途**: 在新会话中继续沟通时加载此文档

---

## 一、项目概况

### ShipMicro (shipmicro.com)
- **技术栈**: Next.js + TypeScript + Vercel
- **代码位置**: `d:\Project\1\micro_saas_forge\shipmicro_site\`
- **线上地址**: https://www.shipmicro.com
- **4 个频道**: 资讯(News) · 赚钱创意(Ideas) · 工具(Tools) · 游戏(Games)

### TITAN Engine (泰坦引擎)
- **代码位置**: `d:\Project\1\micro_saas_forge\`
- **核心定位**: 原为"自动生成Web工具/游戏并部署"的Python引擎
- **LLM**: DeepSeek → Doubao → Qwen 三级降级
- **当前收入**: $0/月

---

## 二、本次会话完成的操作

### 1. 清理瘦身 ✅
- **删除 14 个低质量游戏** + **44 个低质量工具** (共 58 个 HTML 文件)
- **保留精品 5 工具**: json-formatter, base64-codec, regex-tester, jwt-decoder, password-gen
- **保留精品 5 游戏**: whack-a-mole, fruit-ninja, math-blitz, meteor-dodge, simon-neon
- **重写 `data.ts`**: 仅含手动精选的 10 个项目，移除 AI 生成的注册表
- **Sitemap**: 从 504 行缩减到 84 行
- **已部署上线**: `npx vercel --prod` → www.shipmicro.com

### 2. 资讯模块增强 ✅
- **新建 `src/app/news/NewsClient.tsx`**: 客户端组件
  - 分类筛选: AI / Dev / OpenSource / Startup / Cloud / Web3
  - 搜索框 + 排序切换 (热门/最新)
  - 分类徽章 + 时间显示
- **重写 `src/app/news/page.tsx`**: 薄服务端页面，传数据给 NewsClient

### 3. TITAN Engine v4.0 核心模块构建 ✅
新建了 4 个模块:

| 文件 | 行数 | 功能 |
|------|------|------|
| `demand_radar.py` | 230 | 3源需求扫描 (HN API + LLM趋势 + 关键词库)，机会评分 |
| `competitor_scanner.py` | 130 | LLM竞品分析，差异化构建摘要 |
| `browser_qa.py` | 300 | 7维质量测试 (结构/SEO/移动/交互/性能/商业/视觉) |
| `titan_brain.py` | 250 | 7步自治循环控制器 (发现→选择→分析→构建→QA→部署→分发) |

### 4. 冒烟测试结果 ✅
- **Browser QA**: 10 个产品全 PASS (工具均8.1, 游戏均8.3)
- **Titan Brain dry-run**: Cycle #1 成功，选中 "image compressor online" (score 18,750)

---

## 三、4 轮 AI 圆桌会议核心结论

### Session 1: 诊断 (3 AI 全通过)
| AI | 架构评分 |
|----|---------|
| DeepSeek | 3/10 |
| Doubao | 4/10 |
| Qwen | 5/10 |

**5 大一致问题**: 零变现 · 假数据 · 低质量 · 无分析 · 零流量

### Session 2: 技术方案 (仅 DeepSeek 返回 14,823 字)
- AdSense: `npm install @next/third-parties`
- Stripe 3级定价: Free / $19/mo / $99/mo
- 邮件: ConvertKit 免费层
- 关键词: `pip install pytrends` + SerpAPI
- 分析: Umami 自托管
- UI: shadcn-ui + @radix-ui

### Session 3: 战略深潜 (3 AI 全通过)
- **定位投票**: 质量 2票 vs 数量 1票 → 质量胜
- **30天$100路径**: SerpAPI选3个高需求工具 → shadcn-ui开发 → Stripe付费 → Reddit/HN发布
- **AI用途共识**: "把AI用来生成代码是**错误方向**，应用于需求挖掘、动态定价、行为分析"

### Session 4: 质量 vs 转型 (3 AI 全通过) ⭐ 最关键
**TITAN能生成高质量产品吗？**
> 3 AI 一致: **❌ 不能**
> - DeepSeek: "诚实回答：不具备"
> - Doubao: "差距至少7年迭代量，补到商用成本比直接找人开发高3倍"
> - Qwen: "不是高效方案"

**路径对比:**
| 路径 | 可行性 | 裁决 |
|------|--------|------|
| ① 做高质量产品→接广告 | 2.3/10 | ❌ 全票否决 |
| ② 转型商业智能引擎 | 7.0/10 | ✅ 全票通过 |

**第三条路建议:**
- **DeepSeek**: AI商业漏斗优化SaaS → 帮中小商家分析转化 → 订阅+CPS (可行性7)
- **Doubao**: 本地商家轻量工具 → 引擎生成+人工润色 → 399元/个卖 (可行性7, 首年50-100万)
- **Qwen**: 垂直电商数据分析工具 → 订阅制 (可行性6)

---

## 四、待决策事项 (用户未回复)

**需要用户在新会话中做出的关键决定:**

> 确认 TITAN Engine 转型方向:
> - **A**: 转型商业智能引擎 (路径2)
> - **B**: Doubao方案 — 引擎生成基础工具 + 人工润色 → 卖给本地商家 399元/个
> - **C**: DeepSeek方案 — AI商业漏斗优化SaaS → 订阅制
> - **D**: 其他想法

---

## 五、关键文件清单

### ShipMicro 站点
| 文件 | 说明 |
|------|------|
| `shipmicro_site/src/app/page.tsx` | 首页 (4轨道入口) |
| `shipmicro_site/src/app/news/page.tsx` | 资讯服务端页 |
| `shipmicro_site/src/app/news/NewsClient.tsx` | 资讯客户端组件 (筛选/搜索/排序) |
| `shipmicro_site/src/app/ideas/page.tsx` | 赚钱创意页 |
| `shipmicro_site/src/lib/data.ts` | 数据层 (5工具+5游戏+新闻) |
| `shipmicro_site/public/sitemap.xml` | 站点地图 (84行) |
| `shipmicro_site/public/tools/*.html` | 5个精品工具 |
| `shipmicro_site/public/games/*.html` | 5个精品游戏 |

### TITAN Engine
| 文件 | 说明 |
|------|------|
| `forge_master.py` | 旧Pipeline总控 (287行) |
| `core_generators/app_builder.py` | LLM代码生成器 (449行) |
| `core_generators/llm_client.py` | 多模型LLM客户端 (185行) |
| `titan_brain.py` | **v4.0 自治循环控制器** (250行) |
| `demand_radar.py` | **v4.0 需求发现** (230行) |
| `competitor_scanner.py` | **v4.0 竞品分析** (130行) |
| `browser_qa.py` | **v4.0 质量测试** (300行) |
| `config.py` | 统一配置 (API keys) |
| `quality_gate.py` | 质量门控 |
| `memory_bank.py` | 记忆库 |
| `shipmicro_autopilot.py` | 旧自治脚本 (已被titan_brain替代) |
| `growth_engine/basic_seo.py` | SEO引擎 |
| `analytics_tracker.py` | 分析追踪 (仅localStorage, 需替换) |

### 圆桌会议原始数据
| 文件 | 说明 |
|------|------|
| `titan_roundtable_analysis.json` | Session 1 (诊断) |
| `titan_roundtable_commercial.json` | Session 2 (技术方案) |
| `titan_roundtable_s3.json` | Session 3 (战略) |
| `titan_roundtable_s4.json` | Session 4 (质量vs转型) |

---

## 六、环境与依赖

- **OS**: Windows
- **Node.js**: Next.js 16.1.6 (Turbopack)
- **Python**: 3.x
- **部署**: Vercel (已配置 `npx vercel --prod`)
- **LLM APIs**: DeepSeek + Doubao + Qwen (配置在 `.env`)
- **DeepSeek 超时高**: 30s 经常达不到，Doubao 120s 也经常超时
- **Qwen 最稳定**: 通常 30-80s 返回

---

## 七、用户核心诉求

1. **泰坦引擎要能自主赚钱** — 不是生成玩具，要有真实收入
2. **质量优先** — 用户对当前产品评分 2/10
3. **用AI的方式要对** — 不能只用来生成代码，要用在商业漏斗
4. **4大AI圆桌会议是决策方式** — 用户偏好让多个AI共同分析再行动
