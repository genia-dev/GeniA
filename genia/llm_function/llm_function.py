from abc import ABC, abstractmethod
from typing import Any


class LLMFunction(ABC):
    @abstractmethod
    def evaluate(self, function_config: dict, parameters: dict) -> Any:
        pass
