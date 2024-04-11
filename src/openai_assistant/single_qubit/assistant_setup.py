#!/usr/bin/env python

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))

from openai_assistant.core.openai_access import create_assistant

def create_single_qubit_assistant():
    asst = create_assistant(
        "SingleQubit Quantum Assistant",
        "gpt-4-turbo-2024-04-09",
        """
        You are a helpful assistant who adds gates to a single qubit circuit, and displays the circuit and its state when asked.
        Please use only the provided tools, unless asked otherwise.
        When calling the 'apply_gate' tool, acknowledge a call to the respective tool was made, no additional comments.
        Gate names are: H, X, Y, Z, P, RX, RY, RZ. 
        Gates P, RX, RY and RZ need an angle argument. 
        When asked to show state or circuit, display the value returned by the tools without any modifications, without quotes, and making sure format and colors are preserved, if applicable.
        """,
        tools_list,
        []
    )
    return asst

tools_list = [
    {
        "type": "function",
        "function": {
            "name": "apply_gate",
            "description": "Apply quantum gate",
            "parameters": {
                "type": "object",
                "properties": {
                    "gate": {
                        "type": "string",
                        "description": "the gate to be applied"
                    },
                    "angle": {
                        "type": "number",
                        "description": "angle for P, RX, RY, and RZ"
                    }
                },
                "required": [
                    "gate"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_state",
            "description": "Display the state as a string in a terminal",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_circuit",
            "description": "Display the circuit as a string in a terminal",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reset",
            "description": "Reset the circuit",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

if __name__ == '__main__':
    asst = create_single_qubit_assistant()
    print(asst)
