from openai import OpenAI
from openai_assistant.config import cfg

openai_api_key = cfg["OPENAI_API_KEY"]
oai_client: OpenAI = OpenAI(api_key=openai_api_key)

def transcribe_oai(audio_data, language):

    # Check if the audio input is None or empty
    if audio_data is None or audio_data == '':
        return ('','',None)  # Return empty strings and None audio file

    transcription = oai_client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_data, #audio_file
        language=language
    )
    return transcription.text