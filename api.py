import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from google.cloud import speech
from google.api_core.exceptions import GoogleAPICallError, InvalidArgument

app = Flask(__name__)
CORS(app)

# Specify your desired upload folder path here
# Example: UPLOAD_FOLDER = 'C:/Users/YourUsername/Documents/AudioUploads'
UPLOAD_FOLDER = "./sound_files"

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No audio file selected'}), 400
    if file and allowed_file(file.filename):
        filename = file.filename
        # Ensure the UPLOAD_FOLDER exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        time.sleep(5)

        client = speech.SpeechClient.from_service_account_file('./cloud_key.json')

        try:
            with open(file_path, "rb") as f:
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
        except InvalidArgument as e:
            print(f"Invalid argument passed to the API call: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=3000)