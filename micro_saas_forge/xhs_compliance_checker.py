# -*- coding: utf-8 -*-
"""
TITAN Engine — 小红书合规检查器
基于社区公约2.0规则，自动检测并修复笔记内容违规项
"""
import re
from dataclasses import dataclass, field

# ============================================================
# 极限词库（2026年公约2.0标准）
# ============================================================
BANNED_WORDS = [
    # 绝对化用语
    "最佳", "最强", "最好", "最优", "最大", "最快", "最便宜", "最有效",
    "第一", "唯一", "首选", "NO.1", "No.1", "no.1",
    "国家级", "世界级", "顶级", "极品", "极致",
    "100%", "零风险", "绝对", "完美",
    # 医疗相关
    "根治", "治愈", "特效", "神药",
    # 虚假承诺
    "保证赚钱", "稳赚", "躺赚", "月入过万", "日入过千",
    "包教包会", "无条件退款",
]

# URL 正则
URL_PATTERN = re.compile(
    r'(?:https?://|www\.)[^\s<>\u4e00-\u9fff]+|'  # http/www links
    r'[a-zA-Z0-9][-a-zA-Z0-9]*\.(com|net|org|io|cn|cc|me|co|app|dev|xyz|top|site)',  # bare domains
    re.IGNORECASE
)

# 安全的域名（平台内部）
SAFE_DOMAINS = {"xiaohongshu.com", "xhslink.com", "xhs.com"}

# 最低字数要求
MIN_BODY_LENGTH = 100


@dataclass
class ComplianceIssue:
    level: str  # "error" | "warning"
    rule: str
    detail: str
    fix_suggestion: str


@dataclass
class ComplianceResult:
    passed: bool
    issues: list[ComplianceIssue] = field(default_factory=list)
    fixed_title: str = ""
    fixed_body: str = ""
    tags_to_add: list[str] = field(default_factory=list)


def check_compliance(title: str, body: str, is_ai_generated: bool = True) -> ComplianceResult:
    """
    检查小红书笔记内容合规性
    
    Args:
        title: 笔记标题
        body: 笔记正文
        is_ai_generated: 是否为AI生成内容
    
    Returns:
        ComplianceResult 包含所有问题和修复建议
    """
    issues: list[ComplianceIssue] = []
    fixed_title = title
    fixed_body = body
    tags_to_add: list[str] = []
    
    full_text = f"{title}\n{body}"
    
    # ─── 1. 外链检测 ───
    urls = URL_PATTERN.findall(full_text)
    for url_match in urls:
        url = url_match if isinstance(url_match, str) else url_match[0]
        is_safe = any(safe in url.lower() for safe in SAFE_DOMAINS)
        if not is_safe:
            issues.append(ComplianceIssue(
                level="error",
                rule="外链禁止",
                detail=f"检测到外部链接: {url}",
                fix_suggestion="替换为「看我主页简介」或删除"
            ))
            # 自动修复：替换URL为安全文案
            fixed_body = fixed_body.replace(url, "看我主页简介")
            fixed_title = fixed_title.replace(url, "看我主页简介")
    
    # ─── 2. 极限词检测 ───
    for word in BANNED_WORDS:
        if word in full_text:
            issues.append(ComplianceIssue(
                level="warning",
                rule="极限词",
                detail=f"检测到极限词: 「{word}」",
                fix_suggestion=f"建议替换为更温和的表述"
            ))
            # 自动修复部分极限词
            replacements = {
                "最佳": "超棒的", "最强": "超强", "最好": "很好的",
                "最优": "优质的", "第一": "领先", "唯一": "少见的",
                "100%": "非常高", "绝对": "非常", "完美": "出色",
            }
            if word in replacements:
                fixed_body = fixed_body.replace(word, replacements[word])
                fixed_title = fixed_title.replace(word, replacements[word])
    
    # ─── 3. 字数检查 ───
    body_len = len(body.replace("\n", "").replace(" ", ""))
    if body_len < MIN_BODY_LENGTH:
        issues.append(ComplianceIssue(
            level="error",
            rule="字数不足",
            detail=f"正文仅 {body_len} 字，最低要求 {MIN_BODY_LENGTH} 字",
            fix_suggestion="增加更多有价值的内容"
        ))
    
    # ─── 4. AI内容标注 ───
    if is_ai_generated:
        ai_tags = ["#AI辅助创作", "#AI生成"]
        has_ai_tag = any(tag in body for tag in ai_tags)
        if not has_ai_tag:
            issues.append(ComplianceIssue(
                level="warning",
                rule="AI标注缺失",
                detail="AI生成内容未标注，2026年新规要求必须声明",
                fix_suggestion="添加 #AI辅助创作 标签"
            ))
            tags_to_add.append("#AI辅助创作")
    
    # ─── 5. 标题长度检查 ───
    if len(title) > 20:
        # 小红书搜索权重：前10字 > 60%
        pass  # 不是硬性规则，但提醒
    
    if len(title) < 5:
        issues.append(ComplianceIssue(
            level="warning",
            rule="标题过短",
            detail=f"标题仅 {len(title)} 字",
            fix_suggestion="建议标题 10-20 字，前10字包含核心关键词"
        ))
    
    # ─── 6. 评论引导私下交易检测 ───
    private_trade_patterns = ["想要的私信我", "私我下单", "加我微信", "加V"]
    for pattern in private_trade_patterns:
        if pattern in full_text:
            issues.append(ComplianceIssue(
                level="error",
                rule="引导私下交易",
                detail=f"检测到: 「{pattern}」",
                fix_suggestion="删除此类引导，使用官方渠道"
            ))
    
    # 添加AI标签到正文末尾
    if tags_to_add:
        tag_str = " ".join(tags_to_add)
        if tag_str not in fixed_body:
            fixed_body = fixed_body.rstrip() + f"\n\n{tag_str}"
    
    errors = [i for i in issues if i.level == "error"]
    passed = len(errors) == 0
    
    return ComplianceResult(
        passed=passed,
        issues=issues,
        fixed_title=fixed_title,
        fixed_body=fixed_body,
        tags_to_add=tags_to_add,
    )


def print_report(result: ComplianceResult):
    """打印合规检查报告"""
    status = "✅ 通过" if result.passed else "❌ 未通过"
    print(f"\n{'='*50}")
    print(f"📋 小红书合规检查报告 — {status}")
    print(f"{'='*50}")
    
    if not result.issues:
        print("  所有检查项通过！")
        return
    
    for issue in result.issues:
        icon = "🔴" if issue.level == "error" else "🟡"
        print(f"  {icon} [{issue.rule}] {issue.detail}")
        print(f"     → {issue.fix_suggestion}")
    
    if result.tags_to_add:
        print(f"\n  📌 需要添加标签: {', '.join(result.tags_to_add)}")
    
    print(f"{'='*50}")


# ============================================================
# 测试
# ============================================================
if __name__ == "__main__":
    # 测试用例1: 有问题的笔记
    print("测试1: 有外链和极限词的笔记")
    r1 = check_compliance(
        title="这是最强的AI工具！",
        body="这个工具绝对是最佳选择\n详情看 shipmicro.com\n想要的私信我",
        is_ai_generated=True
    )
    print_report(r1)
    print(f"  修复后标题: {r1.fixed_title}")
    print(f"  修复后正文: {r1.fixed_body[:100]}...")
    
    # 测试用例2: 合规的笔记
    print("\n测试2: 合规的笔记")
    r2 = check_compliance(
        title="这个AI工具太好用了 🚀",
        body="自己搞SaaS创业的姐妹们\n" * 10 + "\n#AI辅助创作",
        is_ai_generated=True
    )
    print_report(r2)
