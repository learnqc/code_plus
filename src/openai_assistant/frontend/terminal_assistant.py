import random
import sys
import textwrap
import io
import speech_recognition as sr

import logging

import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from openai_assistant.core.assistant_proxy import OpenaiAssistantProxy
from openai_assistant.frontend.speech_to_text import transcribe_oai

logging.basicConfig()
logger = logging.getLogger("my-logger")
logger.setLevel(logging.ERROR)

class TerminalAssistant():

    def __init__(self, asst_proxy:OpenaiAssistantProxy):
        self.asst_proxy = asst_proxy

    async def run(self):
        recognizer = sr.Recognizer()
        while (True):
            user_input = input('\n\U0001F3A4 Type or press Enter for voice command \U0001F3A4 ')
            if (user_input.lower() == "exit"):
                break
            if (user_input.lower() == ""):
                print("Listening for 6 seconds...")
                with sr.Microphone() as source:
                    audio_data = recognizer.listen(source, phrase_time_limit=6)
                print("Recognizing......")
                try:
                    # Recognize the speech
                    audio_bytes = io.BytesIO(audio_data.get_wav_data())
                    audio_bytes.name = 'audio.wav'
                    text = transcribe_oai(audio_bytes, "en")

                    print("\n\U0001F442 Recognized command: ")
                    print(textwrap.fill(text, 100))

                    if(text.lower().strip() == "exit" or text.lower().strip() == "exit."):
                        break
                    user_input = text
                except sr.UnknownValueError:
                    user_input = None
                    print("Speech recognition could not understand the audio.")
                except sr.RequestError as e:
                    user_input = None
                    print(f"Could not request results from service: {e}")
                except Exception as e:
                    user_input = None
                    print(f"Speech recognition failed: {e}")

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
