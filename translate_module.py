from googletrans import Translator
import time

translator = Translator()

def translate_to_english(text):
    if not text.strip():
        return "Unable to translate. No input provided."
    try:
        result = translator.translate(text, src='te', dest='en')
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return "Translation failed."
