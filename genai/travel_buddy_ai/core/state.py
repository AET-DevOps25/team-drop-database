"""
全局状态管理
"""
from typing import Optional
from travel_buddy_ai.services.qa_system_fixed import AttractionQASystem

class AppState:
    """应用全局状态"""
    def __init__(self):
        self.qa_system: Optional[AttractionQASystem] = None
    
    def set_qa_system(self, qa_system: AttractionQASystem):
        """设置QA系统实例"""
        self.qa_system = qa_system
    
    def get_qa_system(self) -> Optional[AttractionQASystem]:
        """获取QA系统实例"""
        return self.qa_system

# 全局状态实例
app_state = AppState()