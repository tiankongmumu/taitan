#!/usr/bin/env python3
"""
TITAN记忆集成 - 将记忆系统集成到主对话流程
"""

import sys
from datetime import datetime
from pathlib import Path

# 添加记忆模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.memory_bank import MemoryBank, MemoryChunk, MemoryType, get_memory_bank

class TitanMemoryIntegration:
    """TITAN记忆集成"""
    
    def __init__(self):
        self.memory_bank = get_memory_bank()
        self.conversation_history = []
        
        print("🔗 TITAN记忆集成初始化")
    
    def record_conversation(self, user_input: str, ai_response: str):
        """记录对话到记忆"""
        # 创建对话记忆
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        memory = MemoryChunk(
            id=conversation_id,
            type=MemoryType.EPISODIC,
            content=f"用户: {user_input}\nTITAN: {ai_response}",
            timestamp=datetime.now(),
            importance=0.3,
            metadata={
                "user_input": user_input,
                "ai_response": ai_response,
                "input_length": len(user_input),
                "response_length": len(ai_response)
            }
        )
        
        self.memory_bank.save_memory(memory)
        self.conversation_history.append(conversation_id)
        
        # 如果是商业相关，创建商业记忆
        if self._is_business_related(user_input):
            business_memory = MemoryChunk(
                id=f"business_{conversation_id}",
                type=MemoryType.BUSINESS,
                content=f"商业对话 - 用户: {user_input[:200]}",
                timestamp=datetime.now(),
                importance=0.7,
                associations=[conversation_id],
                metadata={"category": "business_conversation"}
            )
            self.memory_bank.save_memory(business_memory)
        
        return conversation_id
    
    def _is_business_related(self, text: str) -> bool:
        """判断是否商业相关"""
        business_keywords = [
            "商业", "收入", "用户", "客户", "产品", "服务",
            "价格", "付费", "支付", "赚钱", "盈利", "市场",
            "竞争", "营销", "销售", "部署", "上线", "发布",
            "business", "revenue", "user", "customer", "product",
            "price", "payment", "money", "market", "competition"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in business_keywords)
    
    def get_relevant_context(self, query: str, limit: int = 3):
        """获取相关上下文"""
        relevant = self.memory_bank.search_memories(query, limit=limit)
        
        if not relevant:
            return "无相关历史记忆"
        
        context_parts = []
        for memory in relevant:
            summary = memory.content[:100] + "..." if len(memory.content) > 100 else memory.content
            context_parts.append(f"[{memory.timestamp.strftime('%H:%M')}] {summary}")
        
        return "\n".join(context_parts)
    
    def get_business_insights(self):
        """获取商业洞察"""
        report = self.memory_bank.get_business_report()
        
        insights = []
        
        if report['revenue_mentions'] == 0:
            insights.append("🚨 尚无收入相关讨论 - 需要立即开始支付集成")
        
        if report['user_mentions'] == 0:
            insights.append("🚨 尚无用户相关讨论 - 需要获取种子用户")
        
        if report['failures'] > report['successes'] * 2:
            insights.append("⚠️ 失败记录远多于成功 - 需要调整策略")
        
        if report['business_memories'] < 5:
            insights.append("📈 商业记忆较少 - 建议增加商业对话")
        
        return insights
    
    def show_status(self):
        """显示状态"""
        report = self.memory_bank.get_business_report()
        
        print("\n📊 TITAN记忆系统状态:")
        print(f"   总记忆数: {report['total_memories']}")
        print(f"   商业记忆: {report['business_memories']}")
        print(f"   收入提及: {report['revenue_mentions']}")
        print(f"   用户提及: {report['user_mentions']}")
        print(f"   成功记录: {report['successes']}")
        print(f"   失败记录: {report['failures']}")
        
        insights = self.get_business_insights()
        if insights:
            print("\n💡 商业洞察:")
            for insight in insights:
                print(f"   • {insight}")

# 全局实例
_memory_integration = None

def get_memory_integration():
    """获取全局记忆集成实例"""
    global _memory_integration
    if _memory_integration is None:
        _memory_integration = TitanMemoryIntegration()
    return _memory_integration

def memory_enhance(func):
    """记忆增强装饰器"""
    def wrapper(user_input, *args, **kwargs):
        memory = get_memory_integration()
        
        # 获取相关上下文
        context = memory.get_relevant_context(user_input)
        if context != "无相关历史记忆":
            print(f"\n🧠 相关历史: {context}")
        
        # 执行原函数
        response = func(user_input, *args, **kwargs)
        
        # 记录到记忆
        memory.record_conversation(user_input, response)
        
        # 如果是商业对话，显示洞察
        if memory._is_business_related(user_input):
            insights = memory.get_business_insights()
            if insights:
                print("\n💡 商业洞察:")
                for insight in insights:
                    print(f"   {insight}")
        
        return response
    return wrapper

def test_integration():
    """测试集成"""
    print("🧪 测试记忆集成...")
    
    memory = get_memory_integration()
    
    # 测试对话
    test_dialogs = [
        ("我们的商业状态如何？", "尚未产生收入，需要立即部署产品"),
        ("用户反馈怎么样？", "还没有真实用户，计划获取种子用户"),
        ("技术架构升级完成了吗？", "记忆系统已集成，正在测试中")
    ]
    
    for user_input, response in test_dialogs:
        print(f"\n用户: {user_input}")
        memory.record_conversation(user_input, response)
        print(f"TITAN: {response}")
    
    memory.show_status()
    print("\n✅ 记忆集成测试完成")

if __name__ == "__main__":
    test_integration()