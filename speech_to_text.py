from google.cloud import speech
from google.api_core.exceptions import GoogleAPICallError, InvalidArgument
import os

class Listener(object):
    def __init__(self):
        self._cached_stamp = 0
        self.filename = './uploads'

    def check_if_change(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp

client = speech.SpeechClient.from_service_account_file('./cloud_key.json')
file_name = "tobeornottobe.wav"

try:
    with open(file_name, "rb") as f:
        data = f.read()

    audio_file = speech.RecognitionAudio(content=data)

    config = speech.RecognitionConfig(
        sample_rate_hertz=44100,
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        language_code='en-US',
        enable_automatic_punctuation=True
    )

    response = client.recognize(config=config, audio=audio_file)
    print(response)
except GoogleAPICallError as e:
    print(f"An error occurred during the API call: {e}")
except GoogleAPICallError as e:
    print(f"An error occurred during the API call: {e}")
except InvalidArgument as e:
    print(f"Invalid argument passed to the API call: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")