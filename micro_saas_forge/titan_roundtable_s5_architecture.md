# TITAN 圆桌 S5: 商业智能引擎架构蓝图
> 时间: 2026-03-02 13:45
> 模式: 串行辩论 (DeepSeek → Doubao → Qwen)

---

## DeepSeek (首席架构师)
# TITAN Engine v5.0 架构蓝图

## 1. 核心模块清单
1.  **signal_collector.py** - 多源原始信号采集
    - 职责：从API、RSS、爬虫收集原始商业信号（融资、招聘、产品更新）。
    - 输入：配置的源列表（Crunchbase, Product Hunt, LinkedIn）。
    - 输出：`List[RawSignal]`。
    - 关键函数：`fetch_all_sources() -> List[RawSignal]`。

2.  **demand_radar_v2.py** - 需求信号增强与聚合
    - 职责：清洗、去重、聚合原始信号，提取核心需求关键词。
    - 输入：`List[RawSignal]`。
    - 输出：`List[AggregatedDemandSignal]`。
    - 关键函数：`aggregate_and_enrich(signals: List[RawSignal]) -> List[AggregatedDemandSignal]`。

3.  **opportunity_scorer.py** - 机会评分与排序
    - 职责：使用LLM分析需求信号，根据市场规模、竞争度、趋势打分。
    - 输入：`List[AggregatedDemandSignal]`。
    - 输出：`List[ScoredOpportunity]`（带score 0-100）。
    - 关键函数：`score_opportunities(demands: List[AggregatedDemandSignal]) -> List[ScoredOpportunity]`。

4.  **competitor_analyzer.py** - 深度竞争格局分析
    - 职责：对高评分机会，深入分析现有玩家优劣势、定价、用户反馈。
    - 输入：`ScoredOpportunity` (score > 70)。
    - 输出：`CompetitorAnalysisReport`。
    - 关键函数：`generate_competitor_report(opportunity: ScoredOpportunity) -> CompetitorAnalysisReport`。

5.  **strategy_generator.py** - 市场进入策略生成
    - 职责：基于机会和竞争分析，生成具体行动策略（定位、渠道、MVP功能）。
    - 输入：`ScoredOpportunity`, `CompetitorAnalysisReport`。
    - 输出：`MarketEntryStrategy`。
    - 关键函数：`generate_entry_strategy(opp, report) -> MarketEntryStrategy`。

6.  **execution_tracker.py** - 策略执行与效果追踪
    - 职责：将策略分解为任务，连接外部工具（如CRM、广告平台API）追踪执行与ROI。
    - 输入：`MarketEntryStrategy`。
    - 输出：`ExecutionDashboardData`。
    - 关键函数：`track_kpis(strategy_id: str) -> Dict[str, float]`。

7.  **insight_engine.py** - 洞察生成与报告
    - 职责：汇总所有数据，生成周期性商业洞察报告（周报/月报），突出风险和机会。
    - 输入：所有模块的输出数据。
    - 输出：`InsightReport` (PDF/HTML)。
    - 关键函数：`generate_weekly_report() -> InsightReport`。

8.  **api_gateway.py** - 统一REST API网关
    - 职责：为前端仪表盘提供数据接口，管理模块间调用。
    - 输入：HTTP请求。
    - 输出：JSON响应。
    - 关键函数：`app = FastAPI()`，定义各端点。

## 2. 数据流图 (ASCII)
```
[外部数据源]
        |
        v
signal_collector.py (采集)
        |
        v
demand_radar_v2.py (聚合)
        |
        v
opportunity_scorer.py (评分) --> [低分机会丢弃]
        |
        v
competitor_analyzer.py (分析)
        |
        v
strategy_generator.py (生成策略)
        |
        v
execution_tracker.py (追踪) <--> [外部平台API]
        |
        v
insight_engine.py (生成报告)
        |
        v
api_gateway.py (服务前端)
        |
        v
[用户仪表盘]
```

## 3. 现有模块改造方案
- **demand_radar.py**: **重写**。保留核心“扫描”概念，但输入源从“产品需求”扩展为“商业信号”（融资、招聘等）。输出格式重构为`AggregatedDemandSignal`。
- **competitor_scanner.py**: **重写并重命名**为`competitor_analyzer.py`。分析目标从“竞品功能”变为“竞争格局、商业模式、用户反馈”。
- **browser_qa.py**: **删除**。产品生成路径已放弃，该模块无保留价值。
- **titan_brain.py**: **核心逻辑移植并拆分**。其“自治循环”思想保留，但拆解到新pipeline的`opportunity_scorer`、`strategy_generator`和`execution_tracker`中。原模块废弃。
- **forge_master.py / app_builder.py**: **彻底删除**。所有代码生成相关模块从代码库中移除，不再维护。

## 4. 技术选型
- **数据库**: **PostgreSQL**。关系型数据（机会、策略、执行记录）复杂，需关联查询和事务。SQLite不适合生产级并发和复杂分析。
- **调度**: **APScheduler**。需要动态管理任务（如定时采集、生成报告），cron配置不够灵活。
- **存储**: **本地文件系统 + 未来对象存储**。MVP阶段报告、缓存文件可存本地。用户量增长后，非结构化数据（如爬取的原始页面）需迁移至S3兼容服务。
- **前端仪表盘**: **需要，使用Next.js (React)**。与现有技术栈一致，用于展示机会列表、策略看板、执行仪表盘。初期可简化，但必须提供数据可视化界面。

## 5. MVP范围
第一个能跑起来的最小版本包含：
1.  **signal_collector.py** (简化版): 仅集成1-2个免费API源（如Hacker News Algolia）。
2.  **demand_radar_v2.py**: 基础聚合与关键词提取。
3.  **opportunity_scorer.py**: 核心模块，使用降级链LLM进行评分。
4.  **api_gateway.py** (基础版): 提供`/opportunities`端点，返回评分后的机会列表。
5.  **一个极简Next.js前端页面**: 仅展示排序后的机会列表（标题、评分、简要原因）。

**数据流MVP**: 采集 -> 聚合 -> 评分 -> API -> 前端列表展示。**跳过**深度竞争分析、策略生成、执行追踪和报告生成，这些在V5.1迭代。

---

## Doubao (商业实战专家)
### 1. 架构评分：7/10
#### 优点：
- 线性pipeline逻辑清晰，MVP边界砍掉非核心模块的决策非常务实，历史遗留模块的裁剪完全符合业务转型方向
- LLM降级链复用现有技术栈，适配成本极低
#### 缺点：
- 缺失信号降噪、负反馈校准机制，容易出现垃圾输入→垃圾输出
- 完全没有埋入变现层的设计，上线后要改核心链路
- 数据存储选型提前透支了MVP阶段的开发成本

---
### 2. 补充/修正
#### 漏的关键模块：`signal_validator.py`
- 职责：前置过滤无效信号（水帖、广告、重复内容），避免下游LLM算力浪费
- 函数签名：`validate_signals(raw_signals: List[RawSignal], filter_rules: Dict) -> List[ValidatedRawSignal]`
- 规则可配置：比如Hacker News信号要求点赞>10、评论>5，Product Hunt信号要求上线24h内点赞>50
#### 过度工程化的部分：
- `execution_tracker.py`、`insight_engine.py`：完全可以推迟到V5.5再做，MVP阶段不需要
- PostgreSQL：MVP用SQLite完全足够，支持万级数据存储，省掉部署、运维成本，用户量破千再迁移不迟
- `CompetitorAnalysisReport`结构化输出：V5阶段先输出纯文本即可，不需要做字段定义，省掉LLM格式约束的调试成本

---
### 3. 数据源实操（全部0成本/低成本）
| 数据源API | 费用 | 限流 | 采集内容 |
| --- | --- | --- | --- |
| Hacker News Algolia Open API | 0元 | 10k请求/小时 | Show HN/Ask HN板块的需求提问、产品反馈 |
| Product Hunt Free Tier API | 0元 | 100请求/小时 | 新上线产品的评论、点赞数、赛道标签 |
| Crunchbase Free Tier API | 0元 | 1000请求/月 | 早期融资项目的赛道、用户规模、商业模式 |
| 第三方封装百度指数API | 0元 | 100请求/天 | 需求关键词的搜索趋势、用户画像 |
| Reddit Public API | 0元 | 100请求/分钟 | r/SaaS、r/Entrepreneur板块的需求提问 |

---
### 4. 变现模块细节
#### CPS通道：
- 新增模块：`affiliate_injector.py`，函数签名：`inject_affiliate(opp: ScoredOpportunity) -> str`
- 对接阿里云/腾讯云/各类SaaS工具的CPS联盟，在机会详情页植入推荐链接，前端加点击埋点统计转化率，用户付费后自动结算佣金
#### SEO通道：
- 新增模块：`static_content_generator.py`，函数签名：`generate_opp_post(opp: ScoredOpportunity) -> Markdown`
- 自动生成机会分析长文，同步到Next.js的静态路由，Vercel自动托管做搜索引擎收录，流量破千后接Google Adsense变现
#### API付费通道：
- `api_gateway.py`新增两个中间件：`api_key_auth.py`、`rate_limit.py`
- 分3档付费：免费版10请求/天、Pro版$29/月1000请求、企业版$299/月不限量，对接Stripe支付回调，自动生成/失效API密钥

---
### 5. Solo Dev风险
- MVP阶段完全可以单人维护，全栈开发2周即可上线
- 核心瓶颈两个：
  1. `signal_collector.py`的反爬适配：各数据源的爬取规则每月都会调整，占30%维护时间
  2. `opportunity_scorer.py`的Prompt迭代：评分准确性需要不断根据用户反馈调优Prompt，占40%维护时间
- 其余模块都是一次性开发，后续基本不需要改动，长期用户破万后再考虑加人维护

（全文1127字）

---

## Qwen (CTO 最终裁决)
### 最终架构决定

1. **signal_collector.py** - 多源原始信号采集
2. **signal_validator.py** - 信号验证与过滤
3. **demand_radar_v2.py** - 需求信号增强与聚合
4. **opportunity_scorer.py** - 机会评分与排序
5. **competitor_analyzer.py** - 深度竞争格局分析
6. **strategy_generator.py** - 市场进入策略生成
7. **affiliate_injector.py** - CPS通道注入
8. **static_content_generator.py** - SEO内容生成
9. **api_gateway.py** - API网关
10. **api_key_auth.py** - API密钥认证中间件

### 优先级排序

- **P0**: signal_collector.py, signal_validator.py, demand_radar_v2.py, opportunity_scorer.py
- **P1**: competitor_analyzer.py, strategy_generator.py, affiliate_injector.py, static_content_generator.py
- **P2**: api_gateway.py, api_key_auth.py

### 技术栈最终选型

- **数据库**: SQLite
- **调度**: Celery + Redis
- **存储**: Vercel自带的静态文件存储
- **前端**: Next.js + Vercel

### 砍掉什么

- **execution_tracker.py**: 这个模块在MVP阶段不需要，可以推迟到后续版本。
- **insight_engine.py**: 同样在MVP阶段不需要，可以推迟到后续版本。
- **PostgreSQL**: 使用SQLite即可满足MVP阶段的需求。

### 第一周交付物

#### 1. 数据收集与验证
- **signal_collector.py**
  - 职责：从API、RSS、爬虫收集原始商业信号（融资、招聘、产品更新）。
  - 输入：配置的源列表（Crunchbase, Product Hunt, LinkedIn）。
  - 输出：`List[RawSignal]`。
  - 关键函数：`fetch_all_sources() -> List[RawSignal]`。

- **signal_validator.py**
  - 职责：前置过滤无效信号（水帖、广告、重复内容），避免下游LLM算力浪费。
  - 函数签名：`validate_signals(raw_signals: List[RawSignal], filter_rules: Dict) -> List[ValidatedRawSignal]`。
  - 规则可配置：比如Hacker News信号要求点赞>10、评论>5，Product Hunt信号要求上线24h内点赞>50。

#### 2. 需求信号增强与聚合
- **demand_radar_v2.py**
  - 职责：清洗、去重、聚合原始信号，提取核心需求关键词。
  - 输入：`List[ValidatedRawSignal]`。
  - 输出：`List[AggregatedDemandSignal]`。
  - 关键函数：`aggregate_and_enrich(signals: List[ValidatedRawSignal]) -> List[AggregatedDemandSignal]`。

#### 3. 机会评分与排序
- **opportunity_scorer.py**
  - 职责：使用LLM分析需求信号，根据市场规模、竞争度、趋势打分。
  - 输入：`List[AggregatedDemandSignal]`。
  - 输出：`List[ScoredOpportunity]`（带score 0-100）。
  - 关键函数：`score_opportunities(demands: List[AggregatedDemandSignal]) -> List[ScoredOpportunity]`。

#### 4. 基本前端展示
- **Next.js前端**
  - 创建一个简单的前端页面，展示收集到的信号和评分结果。
  - 页面包括：
    - 信号列表
    - 评分结果
    - 基本的筛选和排序功能

#### 5. 数据库初始化
- **SQLite数据库**
  - 初始化数据库表结构，用于存储原始信号、验证后的信号、聚合后的信号和评分结果。
  - 表结构示例：
    - `raw_signals` (id, source, content, timestamp)
    - `validated_signals` (id, raw_signal_id, is_valid, validation_rules)
    - `aggregated_signals` (id, validated_signal_ids, keywords, aggregated_content)
    - `scored_opportunities` (id, aggregated_signal_id, score, market_size, competition, trend)

### 总结

通过第一周的交付物，我们可以证明方向A是可行的。我们能够从多个数据源收集信号，进行验证和聚合，并使用LLM对这些信号进行评分。同时，我们可以通过一个简单的前端页面展示这些结果，为后续的深度竞争分析和市场进入策略生成打下坚实的基础。
