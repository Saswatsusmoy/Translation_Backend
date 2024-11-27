from flask import Flask, request, jsonify
import azure.cognitiveservices.speech as speechsdk
import threading

app = Flask(__name__)

# Azure Speech Service credentials
SPEECH_KEY = '3fcc10f1c7fc4c82af2cb58912dbbe9f'
SERVICE_REGION = 'centralindia'

# Function to handle speech-to-speech translation
def translate_speech():
    try:
        # Configure translation settings
        translation_config = speechsdk.translation.SpeechTranslationConfig(
            subscription=SPEECH_KEY,
            region=SERVICE_REGION
        )
        translation_config.speech_recognition_language = 'hi-IN'  # Source language
        translation_config.add_target_language('en')  # Target language

        # Configure microphone input
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        translator = speechsdk.translation.TranslationRecognizer(
            translation_config=translation_config,
            audio_config=audio_config
        )

        # Translation result handler
        def handle_result(evt):
            if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
                response_data = {
                    "recognized_text": evt.result.text,
                    "translations": evt.result.translations
                }
                return response_data

        # Error handler
        def handle_canceled(evt):
            if evt.cancellation_details.reason == speechsdk.CancellationReason.Error:
                return {"error": evt.cancellation_details.error_details}

        # Connect handlers
        translator.recognized.connect(handle_result)
        translator.canceled.connect(handle_canceled)

        # Start recognition and wait for completion
        translator.start_continuous_recognition()
    except Exception as e:
        return {"error": str(e)}

@app.route('/translate', methods=['POST'])
def translate():
    """
    Endpoint to start speech-to-speech translation.
    """
    try:
        threading.Thread(target=translate_speech, daemon=True).start()
        return jsonify({"message": "Translation started"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
