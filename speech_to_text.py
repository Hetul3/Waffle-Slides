from google.cloud import speech
from google.api_core.exceptions import GoogleAPICallError, InvalidArgument

client = speech.SpeechClient.from_service_account_file('cloud_key.json')
file_name = "tobeornottobegi.wav"

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