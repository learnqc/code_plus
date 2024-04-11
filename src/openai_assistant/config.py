import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SINGLE_QUBIT_ASSISTANT_ID = os.getenv('SINGLE_QUBIT_ASSISTANT_ID')
ASSISTANT_ID: os.getenv('ASSISTANT_ID')

cfg = {
    'OPENAI_API_KEY': OPENAI_API_KEY,
    'SINGLE_QUBIT_ASSISTANT_ID': SINGLE_QUBIT_ASSISTANT_ID,
}
