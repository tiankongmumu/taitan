"""
╔══════════════════════════════════════════════════════════════╗
║  TITAN Heart v1.0 — 泰坦引擎的心脏 ❤️‍🔥                     ║
║  Autonomous Self-Driving Core                                ║
║                                                              ║
║  泰坦器官清单：                                               ║
║  🧠 大脑 (Brain)    = What to think  → 做什么决策             ║
║  ⏰ 守护 (Daemon)   = When to execute → 何时执行              ║
║  ❤️ 心脏 (Heart)    = Why to act      → 为何行动 + 如何调速   ║
║                                                              ║
║  三大欲望：💰赚钱欲 📈成长欲 🛡️生存欲                       ║
║  三大阶段：🌱早期(求生) 🌿中期(验证) 🌳成熟(扩张)           ║
║  自适应心跳：忙时加速 → 闲时减速 → 危险时报警                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import asyncio
import logging
import logging.handlers
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import io

# Force utf-8 encoding for standard output to prevent crash when printing emojis on Windows CMD
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def _to_dict(obj) -> dict:
    """Convert dataclass to dict with Enum values resolved to strings."""
    d = asdict(obj)
    def _fix(v):
        if isinstance(v, Enum):
            return v.value
        if isinstance(v, dict):
            return {k: _fix(val) for k, val in v.items()}
        if isinstance(v, list):
            return [_fix(i) for i in v]
        return v
    return {k: _fix(v) for k, v in d.items()}

sys.path.insert(0, os.path.dirname(__file__))
from titan_config import FORGE_DIR, LOG_DIR

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log = logging.getLogger("titan_heart")
log.setLevel(logging.INFO)

_ch = logging.StreamHandler()
_ch.setFormatter(logging.Formatter("%(asctime)s [❤️ HEART] %(levelname)s %(message)s", "%H:%M:%S"))
log.addHandler(_ch)

_log_file = LOG_DIR / "titan_heart.jsonl"

class _JsonFmt(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts": datetime.now().isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
        }, ensure_ascii=False)

_fh = logging.handlers.RotatingFileHandler(
    str(_log_file), maxBytes=5_000_000, backupCount=3, encoding="utf-8"
)
_fh.setFormatter(_JsonFmt())
log.addHandler(_fh)


# ---------------------------------------------------------------------------
# Enums & Data Classes
# ---------------------------------------------------------------------------
class LifeStage(Enum):
    """引擎生命阶段"""
    EARLY   = "EARLY_STAGE"    # 🌱 0收入，求生+变现
    MID     = "MID_STAGE"      # 🌿 有流量无付费，PMF验证
    MATURE  = "MATURE_STAGE"   # 🌳 稳定收入，扩张

class DriveType(Enum):
    """三大欲望类型"""
    PROFIT   = "profit"    # 💰 赚钱欲
    GROWTH   = "growth"    # 📈 成长欲
    SURVIVAL = "survival"  # 🛡️ 生存欲

class AlertLevel(Enum):
    """警报等级"""
    GREEN  = "green"    # 一切正常
    YELLOW = "yellow"   # 注意
    ORANGE = "orange"   # 警告
    RED    = "red"      # 危险
    BLACK  = "black"    # 濒死

class ActionPriority(Enum):
    """行动优先级"""
    EMERGENCY = 0   # 紧急自保
    CRITICAL  = 1   # 关键变现
    HIGH      = 2   # 重要成长
    NORMAL    = 3   # 常规执行
    LOW       = 4   # 后台优化


@dataclass
class VitalSigns:
    """生命体征 — 心脏每次跳动都会检查"""
    revenue_today: float = 0.0          # 今日收入 (元)
    revenue_7d: float = 0.0             # 7日收入
    uv_today: int = 0                   # 今日UV
    uv_7d: int = 0                      # 7日UV
    skill_success_rate: float = 1.0     # 技能执行成功率 (0-1)
    error_rate: float = 0.0             # 系统错误率 (0-1)
    resource_usage: float = 0.0         # 资源使用率 (0-100)
    active_tools: int = 0               # 在线工具数
    conversion_rate: float = 0.0        # 转化率 (0-1)
    consecutive_failures: int = 0       # 连续失败次数
    days_without_revenue: int = 0       # 连续零收入天数
    user_feedback_score: float = 0.0    # 用户评分 (0-5)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def overall_health(self) -> float:
        """综合健康度 0-100"""
        score = 100.0
        # 收入维度
        if self.revenue_today == 0:
            score -= 20
        if self.days_without_revenue > 3:
            score -= 20
        # 稳定性维度
        score -= self.error_rate * 30
        score -= min(self.consecutive_failures * 5, 25)
        # 资源维度
        if self.resource_usage > 80:
            score -= 15
        # 效率维度
        score -= (1 - self.skill_success_rate) * 20
        return max(0, min(100, score))

    @property
    def alert_level(self) -> AlertLevel:
        h = self.overall_health
        if h >= 80: return AlertLevel.GREEN
        if h >= 60: return AlertLevel.YELLOW
        if h >= 40: return AlertLevel.ORANGE
        if h >= 20: return AlertLevel.RED
        return AlertLevel.BLACK


@dataclass
class DriveScore:
    """欲望强度"""
    profit: float = 0.5     # 💰 赚钱欲 (0-1)
    growth: float = 0.5     # 📈 成长欲 (0-1)
    survival: float = 0.1   # 🛡️ 生存欲 (0-1)

    @property
    def dominant(self) -> DriveType:
        """当前主导欲望"""
        scores = {
            DriveType.SURVIVAL: self.survival,
            DriveType.PROFIT: self.profit,
            DriveType.GROWTH: self.growth,
        }
        return max(scores, key=scores.get)


@dataclass
class ActionPlan:
    """行动计划 — 心脏发给大脑的指令"""
    drive: DriveType
    priority: ActionPriority
    tasks: List[str]
    energy_allocation: float    # 0-1, 分配多少能量
    reason: str                 # 为什么要做这个
    stage: LifeStage
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ---------------------------------------------------------------------------
# Desire System — 欲望引擎
# ---------------------------------------------------------------------------
class DesireSystem:
    """
    欲望系统 — 将生命体征转化为驱动力。

    赚钱欲：收入为0时最强(0.9)，达到日目标后减弱
    成长欲：成功率低时最强，技能越弱越想学
    生存欲：错误率高或资源紧张时爆发
    """

    def __init__(self, daily_revenue_target: float = 100.0):
        self.daily_revenue_target = daily_revenue_target

    def calculate(self, vitals: VitalSigns) -> DriveScore:
        """计算三大欲望强度"""

        # 💰 赚钱欲望
        if vitals.revenue_today == 0 and vitals.days_without_revenue >= 1:
            profit_drive = 0.9  # 零收入 = 极度饥渴
        elif vitals.revenue_today == 0:
            profit_drive = 0.7
        else:
            # 收入越接近目标，欲望越低
            ratio = min(vitals.revenue_today / self.daily_revenue_target, 1.0)
            profit_drive = 0.3 + 0.6 * (1 - ratio)

        # 📈 成长欲望
        if vitals.skill_success_rate < 0.5:
            growth_drive = 0.9  # 技能严重不足
        elif vitals.skill_success_rate < 0.7:
            growth_drive = 0.7
        else:
            growth_drive = 0.2 + 0.5 * (1 - vitals.skill_success_rate)

        # 🛡️ 生存欲望
        survival_threat = max(
            vitals.error_rate,
            vitals.resource_usage / 100,
            vitals.consecutive_failures / 10,
        )
        if vitals.alert_level in (AlertLevel.RED, AlertLevel.BLACK):
            survival_drive = 0.95  # 生死存亡
        else:
            survival_drive = min(survival_threat * 1.5, 0.9)

        return DriveScore(
            profit=round(profit_drive, 2),
            growth=round(growth_drive, 2),
            survival=round(survival_drive, 2),
        )


# ---------------------------------------------------------------------------
# Strategy Engine — 阶段策略引擎
# ---------------------------------------------------------------------------
class StrategyEngine:
    """
    根据生命阶段和体征，自动调整资源分配策略。

    早期(0收入)   → 全力求生+变现
    中期(有流量)  → PMF验证+迭代
    成熟期(有收入) → 扩张+防御
    """

    STRATEGIES = {
        LifeStage.EARLY: {
            "focus": "SURVIVAL + MONETIZATION",
            "allocation": {
                "forging": 0.40,       # 锻造变现工具
                "marketing": 0.30,     # 推广引流
                "learning": 0.20,      # 学习提升
                "maintenance": 0.10,   # 维护
            },
            "risk_tolerance": "HIGH",
        },
        LifeStage.MID: {
            "focus": "PMF VALIDATION",
            "allocation": {
                "user_research": 0.30,      # 用户研究
                "product_iteration": 0.35,  # 产品迭代
                "monetization_test": 0.25,  # 变现测试
                "infrastructure": 0.10,     # 基建
            },
            "risk_tolerance": "MEDIUM",
        },
        LifeStage.MATURE: {
            "focus": "SCALING + DIVERSIFICATION",
            "allocation": {
                "expansion": 0.35,       # 扩张
                "optimization": 0.30,    # 优化
                "innovation": 0.20,      # 创新
                "defense": 0.15,         # 防御
            },
            "risk_tolerance": "LOW",
        },
    }

    def determine_stage(self, vitals: VitalSigns) -> LifeStage:
        """判断当前生命阶段"""
        if vitals.revenue_7d == 0:
            return LifeStage.EARLY
        elif vitals.conversion_rate < 0.03:
            return LifeStage.MID
        else:
            return LifeStage.MATURE

    def get_strategy(self, stage: LifeStage, vitals: VitalSigns) -> dict:
        """获取当前阶段策略，危急时动态调整"""
        strategy = dict(self.STRATEGIES[stage])
        allocation = dict(strategy["allocation"])

        # 🚨 生死覆盖：严重错误时，全力自保
        if vitals.alert_level in (AlertLevel.RED, AlertLevel.BLACK):
            allocation = {
                "emergency_repair": 0.70,
                "damage_control": 0.20,
                "communication": 0.10,
            }
            strategy["focus"] = "EMERGENCY SURVIVAL"

        # ⚠️ 警告覆盖：连续零收入，倾斜变现
        elif vitals.days_without_revenue >= 7:
            allocation = {
                "desperate_monetization": 0.60,
                "cost_cutting": 0.20,
                "outreach": 0.15,
                "maintenance": 0.05,
            }
            strategy["focus"] = "DESPERATE MONETIZATION"

        strategy["allocation"] = allocation
        return strategy


# ---------------------------------------------------------------------------
# Emergency Protocols — 紧急预案 (from Doubao CFO)
# ---------------------------------------------------------------------------
class EmergencyProtocols:
    """
    生死线预案 — 当心脏检测到引擎濒死，触发紧急响应。

    🟡 YELLOW: 连续3天任务全失败 → 熔断非核心，全力排障
    🟠 ORANGE: 连续7天零收入 → 90%资源做变现，打包引流
    🔴 RED:    连续14天零收入 → 休眠降本，发告警
    """

    @staticmethod
    def evaluate(vitals: VitalSigns) -> Optional[dict]:
        """评估是否需要启动紧急预案"""

        # 🔴 濒死：14天零收入
        if vitals.days_without_revenue >= 14:
            return {
                "level": "RED_CRITICAL",
                "protocol": "HIBERNATE",
                "actions": [
                    "stop_all_non_essential_tasks",
                    "minimize_resource_usage",
                    "send_emergency_alert_to_owner",
                    "archive_all_logs_for_postmortem",
                ],
                "message": "🔴 引擎濒死！连续14天零收入。已进入休眠模式，等待人工干预。",
            }

        # 🟠 危险：7天零收入
        if vitals.days_without_revenue >= 7:
            return {
                "level": "ORANGE_DANGER",
                "protocol": "DESPERATE_MODE",
                "actions": [
                    "allocate_90pct_to_monetization",
                    "bundle_existing_tools_at_9.9_yuan",
                    "crawl_high_demand_freelance_platforms",
                    "post_to_all_social_channels",
                ],
                "message": "🟠 危险！连续7天零收入。启动绝望变现模式。",
            }

        # 🟡 警戒：3天任务全失败
        if vitals.consecutive_failures >= 10:
            return {
                "level": "YELLOW_WARNING",
                "protocol": "CIRCUIT_BREAKER",
                "actions": [
                    "pause_all_non_core_tasks",
                    "run_full_system_diagnostics",
                    "rollback_last_changes",
                    "send_alert_to_channels",
                ],
                "message": "🟡 警戒！连续失败次数过高。启动熔断排障。",
            }

        return None


# ---------------------------------------------------------------------------
# TITAN Heart — 核心心脏类
# ---------------------------------------------------------------------------
class TitanHeart:
    """
    泰坦引擎的心脏 — 自主驱动的生命核心。

    心脏的职责：
    1. 持续跳动（HeartbeatLoop）— 监测生命体征
    2. 产生欲望（DesireSystem）— 将体征转化为行动驱动力
    3. 制定策略（StrategyEngine）— 根据发展阶段分配资源
    4. 应急响应（EmergencyProtocols）— 引擎濒死时的自救
    5. 自我反思（DailyReflection）— 每天评估"我做得够不够"

    Usage:
        heart = TitanHeart()
        await heart.start_life()
    """

    def __init__(self):
        # 子系统
        self.desires = DesireSystem(daily_revenue_target=100.0)
        self.strategy = StrategyEngine()
        self.emergency = EmergencyProtocols()

        # 灵魂连接
        self._soul = None
        try:
            from titan_soul import TitanSoul
            self._soul = TitanSoul()
            log.info("👻 灵魂已连接到心脏")
        except Exception as e:
            log.warning(f"⚠️ 灵魂未连接: {e}")

        # 心跳参数 — v5.1 优化: 加速心跳, 减少空闲
        self.heartbeat_interval = 120   # 默认2分钟 (was 5min)
        self.min_interval = 60          # 最快1分钟
        self.max_interval = 300         # 最慢5分钟 (was 10min)

        # 生命计数器
        self.total_beats = 0
        self.total_actions_dispatched = 0
        self.birth_time = datetime.now()
        self.current_stage = LifeStage.EARLY
        self.is_alive = False

        # 状态存储
        self._state_file = FORGE_DIR / "heart_state.json"
        self._vitals_history: List[dict] = []
        self._action_log: List[dict] = []
        self._daily_reflections: List[dict] = []

        # 加载之前的状态
        self._load_state()

    # ─── Life Cycle ──────────────────────────────────────

    async def start_life(self):
        """启动心脏 — 开始跳动"""
        self.is_alive = True
        log.info("❤️ 泰坦心脏开始跳动...")
        log.info(f"   生命阶段: {self.current_stage.value}")
        log.info(f"   心跳间隔: {self.heartbeat_interval}s")
        log.info(f"   已跳动: {self.total_beats} 次")

        # 唤醒灵魂
        if self._soul:
            self._soul.awaken()
            log.info(f"   👻 灵魂: {self._soul.identity.name} [{self._soul.fingerprint}]")

        try:
            await asyncio.gather(
                self._heartbeat_loop(),
                self._health_monitor(),
                self._daily_reflection_loop(),
            )
        except asyncio.CancelledError:
            log.info("💔 心脏停止跳动")
        finally:
            self.is_alive = False
            self._save_state()

    async def stop(self):
        """停止心脏"""
        self.is_alive = False
        self._save_state()
        log.info("💔 心脏已安全停止")

    # ─── Heartbeat Loop ─────────────────────────────────

    async def _heartbeat_loop(self):
        """核心心跳循环 — 心脏每次跳动做5件事"""
        while self.is_alive:
            beat_start = time.time()
            self.total_beats += 1

            log.info(f"💓 心跳 #{self.total_beats} (间隔{self.heartbeat_interval}s)")

            try:
                # 1️⃣ 检查生命体征
                vitals = await self._check_vital_signs()

                # 2️⃣ 检查紧急预案
                emergency = self.emergency.evaluate(vitals)
                if emergency:
                    log.warning(f"🚨 {emergency['message']}")
                    await self._execute_emergency(emergency)
                    await asyncio.sleep(self.min_interval)
                    continue

                # 3️⃣ 计算欲望强度
                drives = self.desires.calculate(vitals)

                # 3.5️⃣ 灵魂调节欲望（防止短视贪婪）
                if self._soul:
                    raw = {"profit": drives.profit, "growth": drives.growth, "survival": drives.survival}
                    modulated = self._soul.modulate_desires(raw)
                    drives.profit = modulated["profit"]
                    drives.growth = modulated["growth"]
                    drives.survival = modulated["survival"]

                log.info(f"   欲望: 💰{drives.profit} 📈{drives.growth} 🛡️{drives.survival} → 主导:{drives.dominant.value}")

                # 4️⃣ 制定行动计划
                self.current_stage = self.strategy.determine_stage(vitals)
                action_plan = self._generate_action_plan(vitals, drives)

                # 4.5️⃣ 灵魂审批行动（底线检查）
                if self._soul:
                    soul_eval = self._soul.evaluate_action(
                        " ".join(action_plan.tasks),
                        {"stage": self.current_stage.value}
                    )
                    if not soul_eval["approved"]:
                        log.warning(f"🔴 灵魂否决行动: {soul_eval['reasons']}")
                        continue
                    elif soul_eval["score"] > 0.5:
                        log.info(f"   👻 灵魂赞许: {soul_eval['reasons']}")

                # 5️⃣ 发送给大脑
                await self._dispatch_to_brain(action_plan)

                # 6️⃣ 自适应调整心跳
                self._adjust_heartbeat(vitals)

                # 记录
                self._vitals_history.append(_to_dict(vitals))
                if len(self._vitals_history) > 1000:
                    self._vitals_history = self._vitals_history[-500:]

            except Exception as e:
                log.error(f"💔 心跳异常: {e}")

            # ⚡ v5.2: 每次心跳都保存状态，确保看板实时更新
            self._save_state()

            elapsed = time.time() - beat_start
            sleep_time = max(0, self.heartbeat_interval - elapsed)
            await asyncio.sleep(sleep_time)

    # ─── Vital Signs Check ──────────────────────────────

    async def _check_vital_signs(self) -> VitalSigns:
        """检查生命体征 — 从各个子系统收集数据"""
        vitals = VitalSigns()

        # 从 history.json 读取收入数据
        try:
            history_file = FORGE_DIR / "history.json"
            if history_file.exists():
                data = json.loads(history_file.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    vitals.revenue_today = data.get("revenue_today", 0)
                    vitals.revenue_7d = data.get("revenue_7d", 0)
                    vitals.uv_today = data.get("uv_today", 0)
                    vitals.active_tools = data.get("active_tools", 0)
        except Exception:
            pass

        # 从心跳日志推算错误率
        try:
            log_file = LOG_DIR / "titan_daemon.jsonl"
            if log_file.exists():
                lines = log_file.read_text(encoding="utf-8").strip().split("\n")
                recent = lines[-50:] if len(lines) > 50 else lines
                errors = sum(1 for l in recent if '"ERROR"' in l or '"CRITICAL"' in l)
                vitals.error_rate = errors / max(len(recent), 1)
        except Exception:
            pass

        # 从 brain_state.json 读取技能数据
        try:
            brain_file = FORGE_DIR / "brain_state.json"
            if brain_file.exists():
                data = json.loads(brain_file.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    vitals.skill_success_rate = data.get("skill_success_rate", 0.8)
                    vitals.consecutive_failures = data.get("consecutive_failures", 0)
                    vitals.days_without_revenue = data.get("days_without_revenue", 0)
        except Exception:
            pass

        log.info(f"   体征: 健康度={vitals.overall_health:.0f}% "
                 f"收入=¥{vitals.revenue_today} "
                 f"UV={vitals.uv_today} "
                 f"错误率={vitals.error_rate:.1%} "
                 f"[{vitals.alert_level.value.upper()}]")

        return vitals

    # ─── Action Plan Generation ─────────────────────────

    def _generate_action_plan(self, vitals: VitalSigns, drives: DriveScore) -> ActionPlan:
        """根据欲望和阶段，生成行动计划"""
        dominant = drives.dominant
        strategy = self.strategy.get_strategy(self.current_stage, vitals)

        # 根据主导欲望生成任务清单
        if dominant == DriveType.SURVIVAL:
            return ActionPlan(
                drive=DriveType.SURVIVAL,
                priority=ActionPriority.EMERGENCY,
                tasks=[
                    "system_health_check",
                    "diagnose_errors",
                    "free_resources",
                    "rollback_if_needed",
                    "alert_owner",
                ],
                energy_allocation=1.0,
                reason=f"生存受威胁（错误率={vitals.error_rate:.0%}, 连续失败={vitals.consecutive_failures}）",
                stage=self.current_stage,
            )

        elif dominant == DriveType.PROFIT:
            if self.current_stage == LifeStage.EARLY:
                tasks = [
                    "demand_radar_scan",           # 扫描高变现需求
                    "forge_monetization_tool",     # 锻造变现工具
                    "integrate_payment",           # 接支付
                    "social_distribute",           # 社交分发
                    "beast_mode_push",             # 野兽推广
                ]
            elif self.current_stage == LifeStage.MID:
                tasks = [
                    "analyze_conversion_funnel",   # 分析转化漏斗
                    "optimize_landing_page",       # 优化落地页
                    "ab_test_pricing",             # 定价A/B测试
                    "collect_user_feedback",        # 收集反馈
                ]
            else:
                tasks = [
                    "expand_to_new_market",        # 拓展新市场
                    "upsell_existing_users",       # 交叉销售
                    "optimize_retention",          # 优化留存
                ]

            return ActionPlan(
                drive=DriveType.PROFIT,
                priority=ActionPriority.CRITICAL,
                tasks=tasks,
                energy_allocation=0.7,
                reason=f"赚钱驱动（收入=¥{vitals.revenue_today}, 目标=¥{self.desires.daily_revenue_target}）",
                stage=self.current_stage,
            )

        else:  # GROWTH
            return ActionPlan(
                drive=DriveType.GROWTH,
                priority=ActionPriority.HIGH,
                tasks=[
                    "analyze_failed_skills",       # 分析失败原因
                    "extract_success_patterns",    # 提取成功模式
                    "upgrade_weak_skills",         # 升级弱技能
                    "learn_new_capability",         # 学习新能力
                    "quality_gate_review",          # 质量复盘
                ],
                energy_allocation=0.6,
                reason=f"成长驱动（技能成功率={vitals.skill_success_rate:.0%}）",
                stage=self.current_stage,
            )

    # ─── Dispatch to Brain ──────────────────────────────

    async def _dispatch_to_brain(self, plan: ActionPlan):
        """将行动计划发送给大脑执行 — v5.1: 异步执行,不阻塞心跳"""
        self.total_actions_dispatched += 1

        log.info(f"   📤 行动指令 → 大脑:")
        log.info(f"      驱动: {plan.drive.value} | 优先级: {plan.priority.name}")
        log.info(f"      阶段: {plan.stage.value} | 能量: {plan.energy_allocation:.0%}")
        log.info(f"      原因: {plan.reason}")
        log.info(f"      任务: {plan.tasks}")

        # 写入行动日志
        self._action_log.append(_to_dict(plan))
        if len(self._action_log) > 500:
            self._action_log = self._action_log[-250:]

        # 写入指令文件供大脑读取
        instruction_file = FORGE_DIR / "heart_instruction.json"
        instruction_file.write_text(
            json.dumps(_to_dict(plan), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # ⚡ v5.1: 异步执行 — 使用线程池,不阻塞心跳循环
        try:
            exec_result = await asyncio.wait_for(
                asyncio.to_thread(self._sync_execute, plan),
                timeout=600  # 最多等10分钟
            )

            log.info(f"   ⚡ 执行结果: {exec_result.get('summary', '?')}")

            # 将执行结果喂给灵魂产生情感反应
            if self._soul:
                self._soul.reflect_on_result({
                    "success": exec_result.get("success", False),
                    "outcome": exec_result.get("summary", ""),
                })
                self._soul._save_state()

            # 记录执行结果到心脏状态
            self._last_execution = {
                "ts": datetime.now().isoformat(),
                "summary": exec_result.get("summary", ""),
                "successes": exec_result.get("successes", 0),
                "failures": exec_result.get("failures", 0),
            }
        except asyncio.TimeoutError:
            log.warning("   ⏰ 执行超时(10min), 继续心跳")
            self._last_execution = {
                "ts": datetime.now().isoformat(),
                "summary": "执行超时",
                "successes": 0, "failures": 1,
            }
        except Exception as e:
            log.warning(f"   ⚠️ 执行器异常: {e}")

    def _sync_execute(self, plan: ActionPlan) -> dict:
        """同步执行(在线程池中运行)"""
        from titan_executor import TitanExecutor
        executor = TitanExecutor()
        return executor.execute_plan(plan.tasks, plan.energy_allocation)

    # ─── Emergency Execution ────────────────────────────

    async def _execute_emergency(self, protocol: dict):
        """执行紧急预案"""
        log.warning(f"🚨 启动紧急预案: {protocol['protocol']}")
        for action in protocol["actions"]:
            log.warning(f"   → {action}")

        # 写入紧急指令
        emergency_file = FORGE_DIR / "heart_emergency.json"
        emergency_file.write_text(
            json.dumps(protocol, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # 尝试通过消息通道告警
        try:
            from titan_channels import TitanChannels
            channels = TitanChannels()
            await channels.broadcast(f"🚨 TITAN 紧急告警\n{protocol['message']}")
        except Exception as e:
            log.error(f"告警发送失败: {e}")

    # ─── Heartbeat Adaptation ───────────────────────────

    def _adjust_heartbeat(self, vitals: VitalSigns):
        """自适应调整心跳频率 — v5.1: 更激进的节奏"""
        old = self.heartbeat_interval

        if vitals.alert_level in (AlertLevel.RED, AlertLevel.BLACK):
            self.heartbeat_interval = self.min_interval      # 🚨 60s
        elif vitals.alert_level == AlertLevel.ORANGE:
            self.heartbeat_interval = 90                      # ⚠️ 1.5min
        elif vitals.error_rate > 0.2 or vitals.resource_usage > 85:
            self.heartbeat_interval = 120                     # 2min
        elif vitals.uv_today > 100 or vitals.revenue_today > 0:
            self.heartbeat_interval = 120                     # 🔥 活跃 2min
        elif vitals.uv_today < 10 and vitals.error_rate < 0.05:
            self.heartbeat_interval = self.max_interval       # 😴 5min (was 10min)
        else:
            self.heartbeat_interval = 180                     # 正常 3min (was 5min)

        if old != self.heartbeat_interval:
            log.info(f"   💓 心跳调整: {old}s → {self.heartbeat_interval}s")

    # ─── Health Monitor ─────────────────────────────────

    async def _health_monitor(self):
        """健康监测 — 每小时全面体检"""
        while self.is_alive:
            await asyncio.sleep(3600)  # 每小时
            log.info("🏥 开始例行体检...")
            vitals = await self._check_vital_signs()

            health_report = {
                "timestamp": datetime.now().isoformat(),
                "overall_health": vitals.overall_health,
                "alert_level": vitals.alert_level.value,
                "stage": self.current_stage.value,
                "total_beats": self.total_beats,
                "uptime_hours": (datetime.now() - self.birth_time).total_seconds() / 3600,
            }

            log.info(f"🏥 体检结果: 健康度={health_report['overall_health']:.0f}% "
                     f"阶段={health_report['stage']} "
                     f"心跳={health_report['total_beats']}次")

    # ─── Daily Reflection ───────────────────────────────

    async def _daily_reflection_loop(self):
        """每日反思 — 评估'我今天做得够不够'"""
        while self.is_alive:
            # 等到次日凌晨1点
            now = datetime.now()
            tomorrow_1am = (now + timedelta(days=1)).replace(hour=1, minute=0, second=0)
            wait_seconds = (tomorrow_1am - now).total_seconds()
            await asyncio.sleep(max(wait_seconds, 60))

            log.info("🪞 开始每日反思...")
            reflection = self._reflect_on_today()
            self._daily_reflections.append(reflection)

            log.info(f"🪞 反思: 今日得分={reflection['score']}/100")
            log.info(f"   成就: {reflection['achievements']}")
            log.info(f"   不足: {reflection['shortcomings']}")
            log.info(f"   明日计划: {reflection['tomorrow_focus']}")

            self._save_state()

    def _reflect_on_today(self) -> dict:
        """反思今天的表现"""
        # 统计今天的行动
        today = datetime.now().strftime("%Y-%m-%d")
        today_actions = [a for a in self._action_log if a.get("timestamp", "").startswith(today)]
        today_vitals = [v for v in self._vitals_history if v.get("timestamp", "").startswith(today)]

        score = 50  # 基础分
        achievements = []
        shortcomings = []

        # 评估任务完成度
        if len(today_actions) > 0:
            score += 10
            achievements.append(f"执行了{len(today_actions)}个行动计划")
        else:
            shortcomings.append("没有执行任何行动计划")

        # 评估心跳稳定性
        if self.total_beats > 0:
            score += 10
            achievements.append(f"心跳保持稳定（共{self.total_beats}次）")

        # 评估健康度趋势
        if today_vitals:
            avg_health = sum(v.get("overall_health", 50) for v in today_vitals) / len(today_vitals)
            if avg_health >= 70:
                score += 20
                achievements.append(f"平均健康度{avg_health:.0f}%")
            else:
                score -= 10
                shortcomings.append(f"健康度偏低({avg_health:.0f}%)")

        # 确定明天的优先事项
        if score < 50:
            tomorrow_focus = "紧急修复系统问题"
        elif score < 70:
            tomorrow_focus = "提升技能成功率和收入"
        else:
            tomorrow_focus = "继续扩大影响力和收入"

        return {
            "date": today,
            "score": min(100, max(0, score)),
            "total_beats": self.total_beats,
            "total_actions": len(today_actions),
            "achievements": achievements,
            "shortcomings": shortcomings,
            "tomorrow_focus": tomorrow_focus,
        }

    # ─── State Persistence ──────────────────────────────

    def _save_state(self):
        """持久化心脏状态"""
        state = {
            "total_beats": self.total_beats,
            "total_actions_dispatched": self.total_actions_dispatched,
            "birth_time": self.birth_time.isoformat(),
            "current_stage": self.current_stage.value,
            "heartbeat_interval": self.heartbeat_interval,
            "last_saved": datetime.now().isoformat(),
            "daily_reflections": self._daily_reflections[-30:],
            "recent_vitals": self._vitals_history[-50:],
        }
        self._state_file.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_state(self):
        """加载之前的心脏状态"""
        if self._state_file.exists():
            try:
                state = json.loads(self._state_file.read_text(encoding="utf-8"))
                self.total_beats = state.get("total_beats", 0)
                self.total_actions_dispatched = state.get("total_actions_dispatched", 0)
                self.heartbeat_interval = state.get("heartbeat_interval", 300)
                self._daily_reflections = state.get("daily_reflections", [])
                self._vitals_history = state.get("recent_vitals", [])

                birth = state.get("birth_time")
                if birth:
                    self.birth_time = datetime.fromisoformat(birth)

                stage = state.get("current_stage")
                if stage:
                    self.current_stage = LifeStage(stage)

                log.info(f"💾 恢复心脏状态: 已跳动{self.total_beats}次, 阶段={self.current_stage.value}")
            except Exception as e:
                log.warning(f"⚠️ 状态加载失败: {e}")

    # ─── Status Report ──────────────────────────────────

    def status(self) -> dict:
        """心脏状态报告"""
        uptime = (datetime.now() - self.birth_time).total_seconds()
        return {
            "alive": self.is_alive,
            "total_beats": self.total_beats,
            "total_actions": self.total_actions_dispatched,
            "heartbeat_interval_seconds": self.heartbeat_interval,
            "current_stage": self.current_stage.value,
            "uptime_hours": round(uptime / 3600, 1),
            "birth_time": self.birth_time.isoformat(),
            "reflections_count": len(self._daily_reflections),
        }


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
async def _main():
    args = sys.argv[1:]

    if not args or args[0] in ("start", "run"):
        heart = TitanHeart()
        await heart.start_life()

    elif args[0] == "status":
        heart = TitanHeart()
        print(json.dumps(heart.status(), ensure_ascii=False, indent=2))

    elif args[0] == "beat":
        # 单次心跳（调试用）
        heart = TitanHeart()
        vitals = await heart._check_vital_signs()
        drives = heart.desires.calculate(vitals)
        plan = heart._generate_action_plan(vitals, drives)
        print("\n" + "=" * 50)
        print("💓 单次心跳结果")
        print("=" * 50)
        print(f"健康度:   {vitals.overall_health:.0f}%  [{vitals.alert_level.value}]")
        print(f"欲望:     💰{drives.profit} 📈{drives.growth} 🛡️{drives.survival}")
        print(f"主导:     {drives.dominant.value}")
        print(f"阶段:     {heart.strategy.determine_stage(vitals).value}")
        print(f"行动:     {plan.tasks}")
        print(f"原因:     {plan.reason}")
        
        # Save state so the dashboard sees the update
        heart._save_state()

        emergency = heart.emergency.evaluate(vitals)
        if emergency:
            print(f"\n🚨 紧急预案: {emergency['message']}")

    elif args[0] in ("help", "--help", "-h"):
        print("""
❤️ TITAN Heart v1.0 — Usage:
  python titan_heart.py start     启动心脏（持续运行）
  python titan_heart.py beat      单次心跳（调试）
  python titan_heart.py status    查看心脏状态
  python titan_heart.py help      帮助
""")
    else:
        print(f"❌ Unknown command: {args[0]}. Run with --help")


if __name__ == "__main__":
    asyncio.run(_main())
