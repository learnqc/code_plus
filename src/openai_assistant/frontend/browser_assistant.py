#!/usr/bin/env panel serve --autoreload

import panel as pn
import logging
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from openai_assistant.core.assistant_proxy import OpenaiAssistantProxy


logging.basicConfig()
logger = logging.getLogger("my-logger")
logger.setLevel(logging.ERROR)

class BrowserPanelAssistant():

    def __init__(self, asst_proxy:OpenaiAssistantProxy, title="Assistant"):
        self.asst_proxy = asst_proxy
        self.title = title

    def build_template(self):
        template = pn.template.BootstrapTemplate(title=self.title)

        def callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
            response, tool_outputs = self.asst_proxy.send_user_message(contents)
            clean_response = response.strip('\"').replace('```', '')
            return clean_response

        def cb(*args):
            try:
                return callback(self, *args)
            except Exception as ex:
                logger.error(ex)
                chat_interface.send(
                    "Encountered an error; unable to retrieve assistant answer",
                    user="System",
                    respond=False,
                )

        def str_renderer(value):
            return pn.pane.Str(value, width=1000, styles={'font-size': '10pt'})

        chat_interface = pn.chat.ChatInterface(
            show_undo=False,
            show_rerun=False,
            show_reaction_icons=False,
            callback=cb,
            callback_exception='verbose',
            renderers=[str_renderer]
        )

        chat_interface.send(
            "Enter a message in the TextInput below",
            user="System",
            respond=False,
        )

        template.main.append(chat_interface)
        template.servable()

        return template
