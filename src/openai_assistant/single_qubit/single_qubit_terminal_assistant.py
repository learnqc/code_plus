#!/usr/bin/env python

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))

from components.single_qubit_component import Display
from openai_assistant.config import cfg

import asyncio
import traceback
from openai_assistant.single_qubit.single_qubit_tool_executor import SingleQubitToolExecutor
from openai_assistant.frontend.terminal_assistant import TerminalAssistant
from openai_assistant.core.assistant_proxy import OpenaiAssistantProxy


asst_id = cfg["SINGLE_QUBIT_ASSISTANT_ID"]
tool_executor = SingleQubitToolExecutor(display=Display.TERMINAL)
asst_proxy = OpenaiAssistantProxy(asst_id, tool_executor)

if __name__ == '__main__':
    asst = TerminalAssistant(asst_proxy)
    try:
        asyncio.run(asst.run())
    except Exception as e:
        print(traceback.format_exc())