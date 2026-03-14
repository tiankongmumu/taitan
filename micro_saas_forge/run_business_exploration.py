#!/usr/bin/env python3
"""
执行TITAN商业探索并输出结果
"""
import sys
from pathlib import Path
from datetime import datetime
import json

# 添加路径
root_dir = Path("d:/Project/1/micro_saas_forge")
sys.path.insert(0, str(root_dir))

from business_exploration_agents import BusinessExplorationAgent, ExplorationDomain, MarketAnalysis

def format_analysis_results(results):
    """格式化分析结果"""
    output = []
    
    # 按机会分数排序
    sorted_results = sorted(
        results.items(), 
        key=lambda x: x[1].opportunity_score, 
        reverse=True
    )
    
    output.append("=" * 80)
    output.append("🚀 TITAN商业探索分析报告")
    output.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"💓 TITAN心跳: #532 (记忆系统激活)")
    output.append("=" * 80)
    
    # 总体排名
    output.append("\n🏆 商业领域综合排名:")
    output.append("-" * 40)
    
    for i, (domain, analysis) in enumerate(sorted_results, 1):
        domain_name = domain.value.replace('_', ' ').title()
        score = analysis.opportunity_score
        
        # 星级表示
        stars = "★" * int(score * 5) + "☆" * (5 - int(score * 5))
        
        output.append(f"{i:2d}. {domain_name:25s} {stars:10s} {score:.2f}/1.0")
    
    # 详细分析每个领域
    output.append("\n" + "=" * 80)
    output.append("📊 详细领域分析")
    output.append("=" * 80)
    
    for domain, analysis in sorted_results:
        domain_name = domain.value.replace('_', ' ').title()
        
        output.append(f"\n🔍 {domain_name}")
        output.append("-" * 40)
        
        # 关键指标
        output.append(f"   📈 机会分数:      {analysis.opportunity_score:.2f}/1.0")
        output.append(f"   ⚔️  竞争水平:      {analysis.competition_level:.2f}/1.0")
        output.append(f"   🚧 进入门槛:      {analysis.entry_barrier:.2f}/1.0")
        output.append(f"   💰 收入潜力:      {analysis.revenue_potential:.2f}/1.0")
        output.append(f"   📈 增长趋势:      {analysis.growth_trend:.2f}/1.0")
        output.append(f"   🔧 技术可行性:    {analysis.technical_feasibility:.2f}/1.0")
        output.append(f"   ⏱️  预计时间线:    {analysis.estimated_timeline}")
        
        # 推荐行动
        output.append(f"\n   ✅ 推荐行动:")
        for action in analysis.recommended_actions:
            output.append(f"      • {action}")
        
        # 风险提示
        output.append(f"\n   ⚠️  风险提示:")
        for risk in analysis.risks:
            output.append(f"      • {risk}")
    
    # TITAN能力匹配分析
    output.append("\n" + "=" * 80)
    output.append("🤖 TITAN能力匹配分析")
    output.append("=" * 80)
    
    # 找出最适合TITAN的领域
    titan_optimized = sorted(
        sorted_results,
        key=lambda x: x[1].technical_feasibility * 0.7 + x[1].opportunity_score * 0.3,
        reverse=True
    )
    
    output.append("\n🎯 基于TITAN当前技术能力的最佳匹配:")
    for i, (domain, analysis) in enumerate(titan_optimized[:3], 1):
        domain_name = domain.value.replace('_', ' ').title()
        match_score = analysis.technical_feasibility * 0.7 + analysis.opportunity_score * 0.3
        
        output.append(f"{i}. {domain_name:25s} 匹配度: {match_score:.2f}")
        output.append(f"   技术可行性: {analysis.technical_feasibility:.2f} | 机会分数: {analysis.opportunity_score:.2f}")
    
    # 执行建议
    output.append("\n" + "=" * 80)
    output.append("🎯 TITAN商业执行建议")
    output.append("=" * 80)
    
    # 短期建议 (1-2周)
    output.append("\n📅 短期行动 (1-2周):")
    top_domain = sorted_results[0][0]
    top_name = top_domain.value.replace('_', ' ').title()
    
    output.append(f"1. 立即启动 {top_name} 概念验证")
    output.append(f"   • 创建最小可行产品(MVP)")
    output.append(f"   • 目标: {sorted_results[0][1].estimated_timeline}内上线")
    
    # 中期建议 (1个月)
    output.append("\n📅 中期规划 (1个月):")
    output.append(f"1. 并行探索 {sorted_results[1][0].value.replace('_', ' ').title()}")
    output.append(f"2. 建立收入验证机制")
    output.append(f"3. 开始用户获取测试")
    
    # 长期战略 (3个月)
    output.append("\n📅 长期战略 (3个月):")
    output.append("1. 建立2-3个盈利产品组合")
    output.append("2. 实现月收入稳定增长")
    output.append("3. 构建自动化运营系统")
    
    # 风险控制
    output.append("\n" + "=" * 80)
    output.append("🛡️  风险控制策略")
    output.append("=" * 80)
    
    output.append("\n🔒 技术风险控制:")
    output.append("• 优先选择技术可行性 > 0.7的领域")
    output.append("• 建立快速失败机制")
    output.append("• 保持代码模块化，便于切换")
    
    output.append("\n💰 商业风险控制:")
    output.append("• 小步快跑，避免大额投入")
    output.append("• 尽早验证付费意愿")
    output.append("• 建立用户反馈循环")
    
    # 记忆系统应用
    output.append("\n" + "=" * 80)
    output.append("🧠 记忆系统应用策略")
    output.append("=" * 80)
    
    output.append("\n💾 本次分析已记录到TITAN记忆:")
    output.append("• 8个商业领域的详细分析")
    output.append("• 机会分数和风险评估")
    output.append("• 技术可行性匹配数据")
    output.append("• 为未来决策提供历史参考")
    
    output.append("\n🎯 记忆增强决策:")
    output.append("• 下次商业讨论时，可检索本次分析")
    output.append("• 基于历史数据优化选择")
    output.append("• 避免重复分析相同领域")
    
    output.append("\n" + "=" * 80)
    output.append("💫 分析完成 - TITAN V5.7记忆系统首次实战应用")
    output.append("=" * 80)
    
    return "\n".join(output)

def save_results_to_file(results, output_path):
    """保存结果到文件"""
    # 文本格式
    text_output = format_analysis_results(results)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_output)
    
    print(f"✅ 分析报告已保存: {output_path}")
    
    # JSON格式（供程序读取）
    json_data = {}
    for domain, analysis in results.items():
        json_data[domain.value] = {
            "opportunity_score": analysis.opportunity_score,
            "competition_level": analysis.competition_level,
            "entry_barrier": analysis.entry_barrier,
            "revenue_potential": analysis.revenue_potential,
            "growth_trend": analysis.growth_trend,
            "technical_feasibility": analysis.technical_feasibility,
            "recommended_actions": analysis.recommended_actions,
            "risks": analysis.risks,
            "estimated_timeline": analysis.estimated_timeline
        }
    
    json_path = output_path.replace('.txt', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON数据已保存: {json_path}")
    
    return text_output

def main():
    """主函数"""
    print("🚀 启动TITAN商业探索分析...")
    print("=" * 60)
    
    # 创建探索Agent
    agent = BusinessExplorationAgent()
    
    # 执行全领域分析
    print("\n🔍 开始多维度商业分析...")
    results = agent.explore_all_domains()
    
    # 输出结果
    print("\n📊 生成分析报告...")
    output_path = root_dir / "business_exploration_report.txt"
    
    report = save_results_to_file(results, output_path)
    
    # 在控制台显示摘要
    print("\n" + "=" * 60)
    print("📋 分析摘要:")
    print("=" * 60)
    
    # 显示前三名
    sorted_results = sorted(
        results.items(), 
        key=lambda x: x[1].opportunity_score, 
        reverse=True
    )
    
    print("\n🏆 前三推荐领域:")
    for i, (domain, analysis) in enumerate(sorted_results[:3], 1):
        domain_name = domain.value.replace('_', ' ').title()
        print(f"{i}. {domain_name}")
        print(f"   机会分数: {analysis.opportunity_score:.2f} | 技术可行性: {analysis.technical_feasibility:.2f}")
        print(f"   预计时间: {analysis.estimated_timeline}")
        print(f"   关键行动: {analysis.recommended_actions[0]}")
        print()
    
    # 显示TITAN最佳匹配
    titan_optimized = sorted(
        sorted_results,
        key=lambda x: x[1].technical_feasibility * 0.7 + x[1].opportunity_score * 0.3,
        reverse=True
    )
    
    print("🤖 TITAN最佳技术匹配:")
    best_match = titan_optimized[0]
    domain_name = best_match[0].value.replace('_', ' ').title()
    print(f"   {domain_name} (技术匹配度: {best_match[1].technical_feasibility:.2f})")
    
    print("\n" + "=" * 60)
    print("✅ 商业探索分析完成!")
    print(f"📄 完整报告: {output_path}")
    print("🧠 所有分析已记录到TITAN记忆系统")
    print("=" * 60)

if __name__ == "__main__":
    main()