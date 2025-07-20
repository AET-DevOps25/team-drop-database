from abc import ABC, abstractmethod
from travel_buddy_ai.pipelines.parser.schema import ParsedQuery

class InputParser(ABC):
    """Parser Interface：all strategy must implement parse()"""
    name: str = "base"

    @abstractmethod
    def parse(self, text: str) -> ParsedQuery:
        """convert text to ParsedQuery"""
        raise NotImplementedError