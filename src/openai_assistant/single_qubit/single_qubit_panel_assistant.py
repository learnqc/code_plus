#!/usr/bin/env python -m panel serve

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))

from openai_assistant.config import cfg
from openai_assistant.single_qubit.single_qubit_tool_executor import SingleQubitToolExecutor
from openai_assistant.frontend.browser_assistant import BrowserPanelAssistant
from openai_assistant.core.assistant_proxy import OpenaiAssistantProxy


asst_id = cfg["SINGLE_QUBIT_ASSISTANT_ID"]
tool_executor = SingleQubitToolExecutor()
asst_proxy = OpenaiAssistantProxy(asst_id, tool_executor)
template = BrowserPanelAssistant(asst_proxy, title='Building Quantum Software - Single Qubit Assistant').build_template()