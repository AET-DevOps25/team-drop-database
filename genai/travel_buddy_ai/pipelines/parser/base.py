from abc import ABC, abstractmethod
from travel_buddy_ai.pipelines.parser.schema import ParsedQuery

class InputParser(ABC):
    """顶层 Parser 接口：所有策略必须实现 parse()"""
    name: str = "base"

    @abstractmethod
    def parse(self, text: str) -> ParsedQuery:
        """将自然语言解析为结构化查询"""
        raise NotImplementedError