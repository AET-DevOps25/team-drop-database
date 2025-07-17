#!/usr/bin/env python3
"""
Test fixed version Q&A system
"""

from travel_buddy_ai.services.qa_system_fixed import AttractionQASystem

def test_qa_system():
    """Test Q&A system"""
    print("🧪 Starting to test fixed version Q&A system...")
    print("=" * 50)
    
    try:
        qa_system = AttractionQASystem()
        print("✅ Q&A system initialized successfully\n")
        
        # Test questions list
        test_questions = [
            "Plan a five-day itinerary for me",
            "Are there any free attractions?", 
            "Which places are good for photography?",
            "Recommend some historical and cultural attractions",
            "Where can I do outdoor activities?",
            "What are the fun places in Munich?",
            "Recommend some museums"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"🔍 Test question {i}: {question}")
            print("-" * 40)
            
            result = qa_system.ask(question)
            
            print(f"✅ Search successful, found {result['results_count']} relevant results\n")
            print(f"🤖 AI Answer:")
            print(result['answer'])
            print("=" * 50 + "\n")
        
        print("🎉 Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_qa_system()
