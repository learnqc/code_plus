from components.single_qubit_component import SingleQubit
from components.common import Display
from openai_assistant.core.tool_executor import ToolExecutorInterface

class SingleQubitToolExecutor(ToolExecutorInterface):
    def __init__(self, display=Display.BROWSER):
        self.tools = SingleQubit(display)

    def execute_tool(self, name, arguments):
        func = getattr(self.tools, name)
        return func(**arguments)