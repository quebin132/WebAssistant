from openai import OpenAI

from dotenv import dotenv_values
env_values = dotenv_values('.env')
openaikey = env_values['OPENAI_API_KEY']

class voice2text:
    def __init__(self) -> None:
        self.openai_key = openaikey
        self.client = OpenAI(api_key=self.openai_key)

    def transcribe_audio_file(self, record_name):
        with open(record_name, 'rb') as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model='whisper-1',
                file=audio_file,
                response_format="text",
                language='es'
            )
        print(transcript)
        return transcript