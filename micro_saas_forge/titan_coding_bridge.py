"""
╔══════════════════════════════════════════════════════════════╗
║  TITAN Coding Bridge v1.0 — Antigravity 编码升级系统 🌉     ║
║                                                              ║
║  当泰坦遇到复杂编码任务时，自动升级给 Antigravity (AI助手)    ║
║  完成高质量编码。                                             ║
║                                                              ║
║  流程:                                                        ║
║  ❤️心脏 → ⚡执行器 → 🧠大脑(构建失败) → 🌉桥接器            ║
║    → 📝写入编码请求 → 🔔通知用户 → 👨‍💻Antigravity编码      ║
║    → ✅回写结果 → ❤️心脏(下次心跳使用)                       ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.dirname(__file__))
from titan_config import FORGE_DIR, LOG_DIR

log = logging.getLogger("coding_bridge")

# 请求目录
REQUESTS_DIR = FORGE_DIR / "coding_requests"
REQUESTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 复杂度评估
# ---------------------------------------------------------------------------
class TaskComplexity(Enum):
    """任务复杂度等级"""
    SIMPLE = "simple"       # API可以搞定 (简单工具, 单页应用)
    MEDIUM = "medium"       # API试试, 失败则升级
    COMPLEX = "complex"     # 直接升级给Antigravity
    CRITICAL = "critical"   # 紧急, 必须人工介入


class RequestStatus(Enum):
    """请求状态"""
    PENDING = "pending"         # 等待Antigravity处理
    IN_PROGRESS = "in_progress" # Antigravity正在处理
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消


# ---------------------------------------------------------------------------
# 编码请求
# ---------------------------------------------------------------------------
@dataclass
class CodingRequest:
    """一个编码请求 — 泰坦写给Antigravity的"""
    id: str = ""
    title: str = ""
    description: str = ""
    complexity: str = "complex"
    priority: int = 1           # 1=最高, 5=最低
    status: str = "pending"

    # 上下文信息
    keyword: str = ""           # 市场关键词
    monthly_volume: int = 0     # 月搜索量
    revenue_model: str = ""     # 变现模式
    differentiation: str = ""   # 差异化描述
    build_complexity: str = ""  # 构建复杂度

    # 失败记录 (如果是升级来的)
    previous_attempts: int = 0  # API尝试次数
    failure_reasons: List[str] = field(default_factory=list)
    error_logs: List[str] = field(default_factory=list)

    # 产出要求
    expected_output: str = ""   # 期望产出描述
    target_dir: str = ""        # 代码输出目录
    tech_stack: List[str] = field(default_factory=list)

    # 时间戳
    created_at: str = ""
    completed_at: str = ""

    # Antigravity的回复
    result_summary: str = ""    # 完成摘要
    result_files: List[str] = field(default_factory=list)  # 产生的文件列表

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CodingRequest":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# 复杂度检测器
# ---------------------------------------------------------------------------
def assess_complexity(keyword: str, build_complexity: str = "",
                      previous_failures: int = 0,
                      error_patterns: List[str] = None) -> TaskComplexity:
    """
    评估任务复杂度，决定是API自动完成还是升级给Antigravity.

    升级条件:
    1. build_complexity == "COMPLEX" → 直接升级
    2. previous_failures >= 2 → API已经失败2次，升级
    3. 包含特定关键词(game, 3D, AI, real-time) → 升级
    4. 月搜索量 > 100000 (高价值) → 升级以确保质量
    """
    if error_patterns is None:
        error_patterns = []

    # 硬规则: 标记为COMPLEX的直接升级
    if build_complexity.upper() == "COMPLEX":
        return TaskComplexity.COMPLEX

    # 多次失败 → 升级
    if previous_failures >= 3:
        return TaskComplexity.CRITICAL
    if previous_failures >= 2:
        return TaskComplexity.COMPLEX

    # 关键词复杂度检测
    complex_keywords = [
        "game", "3d", "real-time", "realtime", "multiplayer",
        "editor", "ide", "compiler", "simulator", "emulator",
        "video", "audio", "streaming", "canvas", "webgl",
        "ai", "machine learning", "neural", "blockchain",
    ]
    kw_lower = keyword.lower()
    for ck in complex_keywords:
        if ck in kw_lower:
            return TaskComplexity.COMPLEX

    # 常见失败模式 → 升级
    critical_errors = ["Turbopack build failed", "Expected '</', got '<eof>'"]
    for err in error_patterns:
        for ce in critical_errors:
            if ce in err:
                return TaskComplexity.COMPLEX

    # 默认: 让API先试
    if build_complexity.upper() == "MEDIUM":
        return TaskComplexity.MEDIUM

    return TaskComplexity.SIMPLE


# ---------------------------------------------------------------------------
# Coding Bridge — 核心桥接器
# ---------------------------------------------------------------------------
class CodingBridge:
    """
    泰坦和Antigravity之间的编码请求桥梁.

    泰坦侧:
      bridge.create_request(...)   → 创建请求
      bridge.get_pending()         → 查看待处理
      bridge.check_completed()     → 检查已完成的请求

    Antigravity侧 (由用户触发):
      bridge.get_next_request()    → 获取下一个请求
      bridge.mark_completed(...)   → 标记完成
    """

    def __init__(self):
        self.requests_dir = REQUESTS_DIR

    def create_request(
        self,
        title: str,
        description: str,
        keyword: str = "",
        monthly_volume: int = 0,
        revenue_model: str = "",
        differentiation: str = "",
        build_complexity: str = "",
        previous_attempts: int = 0,
        failure_reasons: List[str] = None,
        error_logs: List[str] = None,
        expected_output: str = "",
        tech_stack: List[str] = None,
        priority: int = 1,
    ) -> CodingRequest:
        """创建一个新的编码请求"""
        req_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        complexity = assess_complexity(
            keyword=keyword,
            build_complexity=build_complexity,
            previous_failures=previous_attempts,
            error_patterns=error_logs or [],
        )

        req = CodingRequest(
            id=req_id,
            title=title,
            description=description,
            complexity=complexity.value,
            priority=priority,
            keyword=keyword,
            monthly_volume=monthly_volume,
            revenue_model=revenue_model,
            differentiation=differentiation,
            build_complexity=build_complexity,
            previous_attempts=previous_attempts,
            failure_reasons=failure_reasons or [],
            error_logs=error_logs or [],
            expected_output=expected_output or f"一个基于'{keyword}'的完整Web应用",
            target_dir=str(FORGE_DIR / "generated_apps" / keyword.replace(" ", "-")),
            tech_stack=tech_stack or ["Next.js", "TypeScript", "TailwindCSS"],
            created_at=datetime.now().isoformat(),
        )

        # 保存请求文件
        req_file = self.requests_dir / f"{req_id}_{keyword.replace(' ', '_')[:30]}.json"
        req_file.write_text(
            json.dumps(req.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        log.info(f"🌉 编码请求已创建: [{req_id}] {title} (复杂度={complexity.value})")

        # 写入一份人类可读的摘要
        self._write_summary(req)

        return req

    def _write_summary(self, req: CodingRequest):
        """写入人类可读的请求摘要"""
        summary_file = self.requests_dir / "PENDING_REQUESTS.md"
        pending = self.get_pending()

        lines = [
            "# 🌉 TITAN → Antigravity 待处理编码请求\n",
            f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"待处理请求: {len(pending)} 个\n",
            "---\n",
        ]

        for p in pending:
            lines.append(f"## [{p.id}] {p.title}\n")
            lines.append(f"- **关键词**: {p.keyword} (月搜索量: {p.monthly_volume:,})\n")
            lines.append(f"- **复杂度**: {p.complexity} | **优先级**: P{p.priority}\n")
            lines.append(f"- **变现模式**: {p.revenue_model}\n")
            lines.append(f"- **差异化**: {p.differentiation}\n")
            lines.append(f"- **API尝试**: {p.previous_attempts}次失败\n")
            if p.failure_reasons:
                lines.append(f"- **失败原因**: {'; '.join(p.failure_reasons[:3])}\n")
            lines.append(f"- **期望产出**: {p.expected_output}\n")
            lines.append(f"- **目标目录**: {p.target_dir}\n")
            lines.append(f"- **创建时间**: {p.created_at}\n")
            lines.append("\n---\n")

        summary_file.write_text("".join(lines), encoding="utf-8")

    def get_pending(self) -> List[CodingRequest]:
        """获取所有待处理的请求"""
        pending = []
        for f in sorted(self.requests_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                req = CodingRequest.from_dict(data)
                if req.status == "pending":
                    pending.append(req)
            except Exception:
                pass
        return sorted(pending, key=lambda r: r.priority)

    def get_next_request(self) -> Optional[CodingRequest]:
        """获取优先级最高的待处理请求"""
        pending = self.get_pending()
        return pending[0] if pending else None

    def mark_in_progress(self, req_id: str):
        """标记请求为处理中"""
        self._update_status(req_id, RequestStatus.IN_PROGRESS)

    def mark_completed(self, req_id: str, summary: str = "", files: List[str] = None):
        """标记请求为已完成"""
        for f in self.requests_dir.glob(f"{req_id}*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                data["status"] = RequestStatus.COMPLETED.value
                data["completed_at"] = datetime.now().isoformat()
                data["result_summary"] = summary
                data["result_files"] = files or []
                f.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                log.info(f"🌉 编码请求已完成: [{req_id}] {summary[:80]}")

                # 更新摘要
                self._write_summary(CodingRequest.from_dict(data))
            except Exception as e:
                log.error(f"标记完成失败: {e}")

    def _update_status(self, req_id: str, status: RequestStatus):
        """更新请求状态"""
        for f in self.requests_dir.glob(f"{req_id}*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                data["status"] = status.value
                f.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except Exception:
                pass

    def check_completed(self) -> List[CodingRequest]:
        """检查已完成的请求"""
        completed = []
        for f in self.requests_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                req = CodingRequest.from_dict(data)
                if req.status == "completed":
                    completed.append(req)
            except Exception:
                pass
        return completed

    def status_report(self) -> str:
        """生成状态报告"""
        pending = self.get_pending()
        completed = self.check_completed()
        total = len(list(self.requests_dir.glob("*.json")))

        return (
            f"🌉 编码桥接状态: "
            f"{len(pending)}待处理 / {len(completed)}已完成 / {total}总计"
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    args = sys.argv[1:]

    bridge = CodingBridge()

    if not args or args[0] == "status":
        print(bridge.status_report())
        pending = bridge.get_pending()
        if pending:
            print(f"\n待处理:")
            for p in pending:
                print(f"  [{p.id}] P{p.priority} {p.title} ({p.keyword})")

    elif args[0] == "test":
        # 创建测试请求
        req = bridge.create_request(
            title="构建在线秒表工具",
            description="一个专业的在线秒表，支持分圈计时、声音提醒、分享结果链接",
            keyword="online stopwatch with laps",
            monthly_volume=135000,
            revenue_model="AdSense + premium features",
            differentiation="Clean full-screen design with voice countdown",
            build_complexity="MEDIUM",
            previous_attempts=2,
            failure_reasons=["Turbopack build failed", "JSX未闭合"],
        )
        print(f"\n✅ 测试请求已创建: {req.id}")
        print(f"   请打开: {REQUESTS_DIR / 'PENDING_REQUESTS.md'}")

    elif args[0] == "next":
        req = bridge.get_next_request()
        if req:
            print(json.dumps(req.to_dict(), ensure_ascii=False, indent=2))
        else:
            print("没有待处理的请求")

    elif args[0] == "complete" and len(args) > 1:
        bridge.mark_completed(args[1], summary=" ".join(args[2:]) or "已完成")
        print(f"✅ 已标记 {args[1]} 为完成")

    elif args[0] in ("help", "--help"):
        print("""
🌉 TITAN Coding Bridge — Usage:
  python titan_coding_bridge.py status     查看请求状态
  python titan_coding_bridge.py test       创建测试请求
  python titan_coding_bridge.py next       获取下一个请求
  python titan_coding_bridge.py complete <id> [summary]  标记完成
""")


if __name__ == "__main__":
    _main()
