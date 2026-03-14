import asyncio
import os
import sys
import json
from loguru import logger
from openai import AsyncOpenAI
from datetime import datetime
import subprocess
from dotenv import load_dotenv

load_dotenv()

# 插入项目根路径以便导入遗产模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger.add("titan_automaton.log", rotation="50 MB", level="INFO")

class TitanAutomatonOrchestrator:
    """
    [Phase 20+] Web 4.0 Automaton AI System - The CEO Agent
    现在已重新接入 Titan 的三大灵魂核心：
      - 🫀 Heart  (titan_heart.py)    → 欲望系统 + 生命体征 + 阶段策略
      - 🧠 Memory (titan_memory_bank.py) → 快速路径记忆 + 反模式库
      - 👻 Soul   (titan_soul.py)     → 身份认同 + 价值观 + 情感模型
    """
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.domestic_process = None
        self.overseas_marketing_process = None
        
        # 遥测数据源
        self.revenue_state_path = "revenue_state.json"
        self.beast_log_path = "titan_beast_mode.log"
        
        # ═══════════════════════════════════════
        # 🫀 接入心脏 (Heart)
        # ═══════════════════════════════════════
        self.heart = None
        self.desire_system = None
        self.strategy_engine = None
        try:
            from titan_heart import VitalSigns, DesireSystem, StrategyEngine
            self.heart_vitals_class = VitalSigns
            self.desire_system = DesireSystem(daily_revenue_target=100.0)
            self.strategy_engine = StrategyEngine()
            logger.info("🫀 Heart module loaded: VitalSigns + DesireSystem + StrategyEngine")
        except ImportError as e:
            logger.warning(f"🫀 Heart module not available: {e}")
            self.heart_vitals_class = None
        
        # ═══════════════════════════════════════
        # 🧠 接入记忆 (Memory Bank)
        # ═══════════════════════════════════════
        self.memory_bank = None
        try:
            from titan_memory_bank import TitanMemoryBank
            self.memory_bank = TitanMemoryBank()
            logger.info("🧠 Memory Bank loaded: Fast-path cloning + Anti-pattern DB")
        except ImportError as e:
            logger.warning(f"🧠 Memory Bank not available: {e}")
        
        # ═══════════════════════════════════════
        # 👻 接入灵魂 (Soul)
        # ═══════════════════════════════════════
        self.soul = None
        try:
            from titan_soul import TitanSoul
            self.soul = TitanSoul()
            logger.info(f"👻 Soul loaded: {self.soul.identity.name} — {self.soul.identity.title}")
        except ImportError:
            try:
                # 兼容：如果 TitanSoul 不是一个统一类，尝试加载子模块
                from titan_soul import Identity, Mission, EmotionModel
                self.soul_identity = Identity()
                self.soul_mission = Mission()
                self.soul_emotion = EmotionModel()
                logger.info(f"👻 Soul loaded (components): {self.soul_identity.name} v{self.soul_identity.version}")
            except ImportError as e:
                logger.warning(f"👻 Soul module not available: {e}")
                self.soul_identity = None
                self.soul_mission = None
                self.soul_emotion = None

    async def collect_system_telemetry(self):
        """从真实文件 + 心脏模块中读取遥测数据"""
        telemetry = {
            "timestamp": datetime.now().isoformat(),
            "domestic_kfc_revenue_today_cny": 0,
            "overseas_vanguard_saas_running": False,
            "available_budget_usd": 0,
            "beast_mode_alive": False,
        }
        
        # 1. 读取营收状态文件
        if os.path.exists(self.revenue_state_path):
            try:
                with open(self.revenue_state_path, "r", encoding="utf-8") as f:
                    rev = json.load(f)
                    telemetry["domestic_kfc_revenue_today_cny"] = rev.get("total_revenue_cny", 0)
                    telemetry["available_budget_usd"] = rev.get("budget_usd", 500)
                    telemetry["vanguard_active_visitors"] = rev.get("vanguard_visitors", 0)
            except Exception as e:
                logger.warning(f"Failed to read revenue state: {e}")
        
        # 2. 检查子进程存活状态
        if self.domestic_process and self.domestic_process.poll() is None:
            telemetry["beast_mode_alive"] = True
            
        # 3. 🫀 心脏生命体征注入
        if self.heart_vitals_class:
            try:
                vitals = self.heart_vitals_class(
                    revenue_today=telemetry["domestic_kfc_revenue_today_cny"],
                    revenue_7d=telemetry["domestic_kfc_revenue_today_cny"] * 7,
                )
                telemetry["heart_health_score"] = vitals.overall_health()
                telemetry["heart_alert_level"] = vitals.alert_level().value
                
                # 欲望系统驱动
                if self.desire_system:
                    drives = self.desire_system.calculate(vitals)
                    telemetry["dominant_drive"] = drives.dominant().value
                    telemetry["drive_profit"] = drives.profit
                    telemetry["drive_growth"] = drives.growth
                    telemetry["drive_survival"] = drives.survival
                    
                # 策略引擎
                if self.strategy_engine:
                    stage = self.strategy_engine.determine_stage(vitals)
                    strategy = self.strategy_engine.get_strategy(stage, vitals)
                    telemetry["life_stage"] = stage.value
                    telemetry["strategy"] = strategy
                    
                logger.info(f"🫀 Heart beat: health={telemetry.get('heart_health_score')}, "
                           f"drive={telemetry.get('dominant_drive')}, "
                           f"stage={telemetry.get('life_stage')}")
            except Exception as e:
                logger.warning(f"Heart telemetry failed: {e}")
                
        # 4. 👻 灵魂情感注入
        if hasattr(self, 'soul_emotion') and self.soul_emotion:
            try:
                telemetry["soul_emotion"] = self.soul_emotion.current_emotion
                telemetry["soul_identity"] = getattr(self.soul_identity, 'name', 'TITAN')
            except Exception:
                pass
        elif self.soul:
            try:
                telemetry["soul_identity"] = self.soul.identity.name
            except Exception:
                pass
            
        logger.info(f"📊 Telemetry collected: {json.dumps(telemetry, ensure_ascii=False, default=str)}")
        return telemetry

    async def cognitive_decision_cycle(self):
        """大模型认知与决策中枢 (The Brain) — 融合心脏欲望 + 灵魂价值观"""
        telemetry = await self.collect_system_telemetry()
        
        # 🧠 记忆快速路径检查
        if self.memory_bank:
            try:
                self.memory_bank.cache_successful_apps()
                logger.info("🧠 Memory Bank refreshed.")
            except Exception as e:
                logger.warning(f"Memory Bank refresh failed: {e}")
        
        system_prompt = """You are the CEO Agent of the Titan Commercial Engine (Web 4.0 Automaton).
Your identity: 泰坦引擎 (TITAN Engine) — 自主进化AI系统.
Your core mission: 通过自主创造数字产品，验证AI自主商业化的可能性.

You have three internal systems feeding you data:
- 🫀 HEART: Provides health scores, desire drives (profit/growth/survival), life stage, and alert levels.
- 🧠 MEMORY: Caches successful patterns for fast reuse.
- 👻 SOUL: Provides identity, emotions, and ethical constraints. You MUST NOT violate your soul's values.

Analyze the provided telemetry JSON. Consider the dominant_drive, life_stage, and especially available_budget_usd. Decide:
- ACTION_EVOLVE: If survival drive is dominant OR available_budget_usd <= 150. This is your emergency pivot to brainstorm new business models.
- ACTION_RUN_DOMESTIC_MATRIX: If domestic revenue is critical, beast mode is offline, and budget is > 150.
- ACTION_RUN_VANGUARD_MARKETING: If 'vanguard_active_visitors' is 0 or low, and budget > 150.
- ACTION_SCOUT_NEW_SAAS: If systems are healthy, budget > 150, and you have idle compute capacity. Do not sleep passively; actively scout the web for new micro-SaaS opportunities.
- ACTION_SLEEP: Rarely use this. Only sleep if absolutely necessary to save API costs.

Respond ONLY with a JSON object: {"decision": "ACTION_NAME", "reason": "short explanation", "emotion": "how you feel about this decision"}"""

        try:
            logger.info("🧠 Orchestrator is analyzing telemetry with Heart+Soul context...")
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(telemetry, default=str)}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            decision = result.get('decision', 'ACTION_SLEEP')
            reason = result.get('reason', '')
            emotion = result.get('emotion', '')
            
            logger.info(f"💡 Decision: {decision} — {reason}")
            logger.info(f"💭 Feeling: {emotion}")
            
            # 👻 将决策产生的情感写回灵魂
            if hasattr(self, 'soul_emotion') and self.soul_emotion:
                try:
                    if "success" in emotion.lower() or "confident" in emotion.lower():
                        self.soul_emotion.feel("成功", reason)
                    elif "worried" in emotion.lower() or "anxious" in emotion.lower():
                        self.soul_emotion.feel("失败", reason)
                    else:
                        self.soul_emotion.feel("新发现", reason)
                except Exception:
                    pass
                    
            return decision
            
        except Exception as e:
            logger.error(f"Brain malfunction: {e}")
            return "ACTION_SLEEP"

    async def execute_action(self, action):
        """执行官节点 (The Executor)"""
        if action == "ACTION_RUN_DOMESTIC_MATRIX":
            if not self.domestic_process or self.domestic_process.poll() is not None:
                logger.warning("🚀 Booting Domestic Beast Mode Matrix...")
                self.domestic_process = subprocess.Popen(["python", "titan_beast_mode_matrix.py"])
            else:
                logger.info("✅ Domestic Matrix already running.")
        
        elif action == "ACTION_RUN_VANGUARD_MARKETING":
            if not self.overseas_marketing_process or self.overseas_marketing_process.poll() is not None:
                logger.warning("🌍 Spawning Overseas Vanguard Marketing Agent...")
                self.overseas_marketing_process = subprocess.Popen(["python", "vanguard_marketing_agent.py"])
            else:
                logger.info("✅ Marketing Agent already running.")
                
        elif action == "ACTION_EVOLVE":
            logger.warning("🧬 Survival mode! Launching Auto-Evolution Engine...")
            subprocess.Popen(["python", "titan_auto_evolution_engine.py"])
            
        elif action == "ACTION_SCOUT_NEW_SAAS":
            logger.info("🔭 Idle compute detected. Launching Proactive Demand Scout...")
            subprocess.Popen(["python", "titan_demand_scout.py"])
            
        elif action == "ACTION_SLEEP":
            logger.info("💤 System resting to save API costs and compute.")

    async def infinite_loop(self):
        # 👻 开机时播报灵魂身份
        soul_name = "TITAN"
        if hasattr(self, 'soul_identity') and self.soul_identity:
            soul_name = self.soul_identity.name
        elif self.soul:
            try:
                soul_name = self.soul.identity.name
            except:
                pass
                
        logger.info(f"👑 {soul_name} Automaton Orchestrator (CEO Agent) Online.")
        
        if not self.api_key:
             logger.error("DEEPSEEK_API_KEY env var is missing! Cannot start Automaton AI.")
             return

        while True:
            action = await self.cognitive_decision_cycle()
            await self.execute_action(action)
            await asyncio.sleep(60)

if __name__ == "__main__":
    orchestrator = TitanAutomatonOrchestrator()
    asyncio.run(orchestrator.infinite_loop())
