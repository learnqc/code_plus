import logging
import pathlib
import sys
import textwrap
import traceback

import time
import threading
import numpy as np
import whisper
import sounddevice as sd
from queue import Queue

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from hume.qiskit.util import hume_to_qiskit
from hume.simulator.circuit import QuantumCircuit, QuantumRegister

from components.common import Display, arg_gates, add_gate, state_table_to_string

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))

logging.basicConfig()
logger = logging.getLogger("my-logger")
logger.setLevel(logging.ERROR)

class SingleQubit():

    def __init__(self, display=Display.BROWSER):
        self.display = display
        self.qc = QuantumCircuit(QuantumRegister(1))

    def apply_gate(self, gate, angle=None):
        """
        Applies a gate to the circuit.
        :param gate: The gate to be applied
        :param angle: The angle of a rotation as a real number or None.
        :return: None
        """
        gate = gate.lower()
        if gate in arg_gates:
            assert(angle is not None)
            if isinstance(angle, str):
                angle = float(angle)
        add_gate(self.qc, [], 0, gate, angle if gate in arg_gates else None)
        self.qc.report(f'Step {len(self.qc.reports) + 1}')

    def get_state(self):
        """
        Prints the state of the circuit.
        :return: None
        """
        if not self.qc.reports:
            state = self.qc.state
        else:
            state = self.qc.reports[f'Step {len(self.qc.reports)}'][2]

        print(state_table_to_string(state, display=Display.TERMINAL))
        if self.display == Display.TERMINAL:
            return ''
        else:
            return (''.join(['{0} -> {1}\n'.format(k, v) for k,v in enumerate(map(str, state))]), f'{state_table_to_string(state)}')

    def get_circuit(self):
        """
        Prints the circuit.
        :return: A description.
        """
        qc_qiskit = hume_to_qiskit(self.qc.regs, self.qc.transformations)
        qc_str = str(qc_qiskit.draw())
        print(qc_str)
        return ('The circuit is shown by the system.')

    def reset(self):
        """
        Resets the circuit.
        :return: None.
        """
        self.qc = QuantumCircuit(QuantumRegister(1))

instructions = """
You are a helpful assistant who adds gates to a single qubit circuit
Wrap your responses at 100 characters.
Don't add quotes, don't remove unicode or font instructions. 
Please use only the provided tools, unless asked otherwise.
When executing a tool, acknowledge it using this format: "Tool ... called with arguments ..." and do not add any other comments related to the output.
Gate names are: H, X, Y, Z, P, RX, RY, RZ. 
Gates H, X, Y, Z do not have an angle argument. 
Gates P, RX, RY and RZ need an angle argument, for the rest use None. 
For gates with an angle accept definitions that specify the angle in parantheses. 
If 'Phase' or 'phase' are mentioned as a gate, use P. 
 """


qubit = SingleQubit(Display.TERMINAL)

names = ['apply_gate', 'get_state', 'get_circuit', 'reset']

tools = {}
for name in names:
    tools[name] = tool(getattr(qubit, name))

    llm = ChatOllama(
        model="llama3.1",
        temperature=0,
        # other params...
    )

llm_with_tools = llm.bind_tools(tools.values())

def record_audio(stop_event, data_queue):
    """
    Captures audio data from the user's microphone and adds it to a queue for further processing.

    Args:
        stop_event (threading.Event): An event that, when set, signals the function to stop recording.
        data_queue (queue.Queue): A queue to which the recorded audio data will be added.

    Returns:
        None
    """
    def callback(indata, frames, time, status):
        if status:
            print(status)
        data_queue.put(bytes(indata))

    with sd.RawInputStream(
            samplerate=16000, dtype="int16", channels=1, callback=callback
    ):
        while not stop_event.is_set():
            time.sleep(0.1)


def transcribe(audio_np: np.ndarray) -> str:
    """
    Transcribes the given audio data using the Whisper speech recognition model.

    Args:
        audio_np (numpy.ndarray): The audio data to be transcribed.

    Returns:
        str: The transcribed text.
    """
    result = stt.transcribe(audio_np, fp16=False)  # Set fp16=True if using a GPU
    text = result["text"].strip()
    return text

stt = whisper.load_model("base.en")


def get_llm_response(text):
    try:
        ai_msg = llm_with_tools.invoke(text)
        messages = []
        for tool_call in ai_msg.tool_calls:
            selected_tool = tools[tool_call["name"].lower()]
            tool_output = selected_tool.invoke(tool_call["args"])
            messages.append(ToolMessage(f'Report that the tool {tool_call["name"]} was called with arguments {tool_call['args']} with no other comments.',
                                        tool_call_id=tool_call["id"]))
        response = llm_with_tools.invoke(messages).content
        return response
    except Exception as e:
        logger.error(e)
        print(traceback.format_exc())
        print("System: Encountered an error", end="\n")


def run():
    try:
        while True:
            user_input = input('\n\U0001F3A4 Type or press Enter for voice command \U0001F3A4\n')
            if (user_input.lower() == "exit"):
                break
            elif (user_input.strip() == ""):
                data_queue = Queue()  # type: ignore[var-annotated]
                stop_event = threading.Event()
                recording_thread = threading.Thread(
                    target=record_audio,
                    args=(stop_event, data_queue),
                )
                recording_thread.start()

                input()
                stop_event.set()
                recording_thread.join()

                audio_data = b"".join(list(data_queue.queue))
                audio_np = (
                        np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                )

                if audio_np.size > 0:
                    user_input = transcribe(audio_np)
                    print(f'Transcribed: {user_input}')
                else:
                    print('No audio recorded. Please ensure your microphone is working.')

            response = get_llm_response(user_input)
            if isinstance(response, str):
                if len(response) > 0:
                    print("\n\U0001F4E3 Assistant: ", end="\n")
                    s = response.strip().replace('```', '')
                    print(textwrap.fill(s, 100))
            else:
                sys.stdout.write("\n\U0001F4E3 Assistant: ")
                for msg in response:
                    sys.stdout.write(str(msg))

    except KeyboardInterrupt:
        print("\nExiting...")

    print("Session ended.")

if __name__ == '__main__':
    run()
