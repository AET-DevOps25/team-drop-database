"""
Global state management
"""
from typing import Optional
from travel_buddy_ai.services.qa_system_fixed import AttractionQASystem

class AppState:
    """Application global state"""
    def __init__(self):
        self.qa_system: Optional[AttractionQASystem] = None
    
    def set_qa_system(self, qa_system: AttractionQASystem):
        """Set QA system instance"""
        self.qa_system = qa_system
    
    def get_qa_system(self) -> Optional[AttractionQASystem]:
        """Get QA system instance"""
        return self.qa_system

# Global state instance
app_state = AppState()