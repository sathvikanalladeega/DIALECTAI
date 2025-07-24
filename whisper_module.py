import whisper

model = whisper.load_model("medium")  # medium or large for better accuracy

def transcribe_audio(audio_path):
    try:
        # language="te" hints the model to expect Telugu (if supported)
        result = model.transcribe(audio_path, language="te")
        return result["text"]
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
