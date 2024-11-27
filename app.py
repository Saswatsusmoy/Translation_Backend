import os
from flask import Flask, request, Response
from utils.audio_utils import convert_aac_to_wav
import azure.cognitiveservices.speech as speechsdk

app = Flask(__name__)

# Azure Speech Service credentials
speech_key = "3fcc10f1c7fc4c82af2cb58912dbbe9f"
service_region = "centralindia"

# Home route
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Speech Translation API! Use the /translate endpoint to upload audio files.", 200

# Favicon route
@app.route('/favicon.ico')
def favicon():
    return '', 204

# Function to handle real-time translation
def translate_audio_stream(wav_file_path):
    translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=speech_key,
        region=service_region,
    )
    translation_config.speech_recognition_language = "en-US"  # Source language
    translation_config.add_target_language("es")  # Target language (Spanish)
    translation_config.voice_name = "es-ES-AlvaroNeural"  # Voice for synthesized output

    # Configure audio input from the converted WAV file
    audio_config = speechsdk.audio.AudioConfig(filename=wav_file_path)
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=translation_config,
        audio_config=audio_config,
    )

    def result_callback(event):
        if event.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            print(f"Recognized: {event.result.text}")
            print(f"Translated: {event.result.translations['es']}")
            return event.result.get_audio()

    recognizer.recognizing.connect(result_callback)
    recognizer.recognized.connect(result_callback)

    recognizer.start_continuous_recognition()
    
    try:
        while True:
            pass  # Keep running until interrupted
    except KeyboardInterrupt:
        recognizer.stop_continuous_recognition()

@app.route('/translate', methods=['POST'])
def translate():
    try:
        # Save uploaded .aac file temporarily
        aac_file = request.files['file']
        input_path = f"./temp/{aac_file.filename}"
        output_path = input_path.replace(".aac", ".wav")
        
        os.makedirs("./temp", exist_ok=True)
        aac_file.save(input_path)

        # Convert .aac to .wav
        convert_aac_to_wav(input_path, output_path)

        # Perform real-time translation on the converted file
        translated_audio_stream = translate_audio_stream(output_path)

        # Clean up temporary files
        os.remove(input_path)
        os.remove(output_path)

        return Response(translated_audio_stream, mimetype="audio/wav")
    
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
