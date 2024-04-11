from abc import ABC, abstractmethod

class ToolExecutorInterface(ABC):
    @abstractmethod
    def execute_tool(self, name, arguments):
        pass
