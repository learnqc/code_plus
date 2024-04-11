import random
import sys
import textwrap
import io

import logging

import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from openai_assistant.core.assistant_proxy import OpenaiAssistantProxy

logging.basicConfig()
logger = logging.getLogger("my-logger")
logger.setLevel(logging.ERROR)

class TerminalAssistant():

    def __init__(self, asst_proxy:OpenaiAssistantProxy):
        self.asst_proxy = asst_proxy

    async def run(self):
        while (True):
            user_input = input('\nType command:\n')
            if (user_input.lower() == "exit"):
                break

            if(user_input):
                try:
                    response = self.asst_proxy.send_user_message(user_input)
                    if isinstance(response, str):
                        print("\n\U0001F4E3 Assistant: ", end="\n")
                        s = response.strip().replace('```', '')
                        print(textwrap.fill(s, 100))
                    else:
                        sys.stdout.write("Assistant: ")
                        for msg in response:
                            sys.stdout.write(str(msg))
                except Exception as e:
                    logger.error(e)
                    print("System: Encountered an error; unable to retrieve assistant answer", end="\n")
