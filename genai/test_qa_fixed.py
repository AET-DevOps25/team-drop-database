#!/usr/bin/env python3
"""
测试修正版问答系统
"""

from qa_system_fixed import AttractionQASystem

def test_qa_system():
    """测试问答系统"""
    print("🧪 开始测试修正版问答系统...")
    print("=" * 50)
    
    try:
        qa_system = AttractionQASystem()
        print("✅ 问答系统初始化成功\n")
        
        # 测试问题列表
        test_questions = [
            "给我规划一个五天的行程",
            "有什么免费的景点吗？", 
            "哪些地方适合拍照？",
            "推荐一些历史文化景点",
            "有什么户外活动的地方？",
            "慕尼黑有什么好玩的？",
            "推荐一些博物馆"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"🔍 测试问题 {i}: {question}")
            print("-" * 40)
            
            result = qa_system.ask(question)
            
            print(f"✅ 搜索成功，找到 {result['results_count']} 个相关结果\n")
            print(f"🤖 AI回答:")
            print(result['answer'])
            print("=" * 50 + "\n")
        
        print("🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_qa_system()
