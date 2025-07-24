from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
import os
import traceback
import mysql.connector

# Custom modules
from whisper_module import transcribe_audio
from dialect_mapper import detect_dialect_and_translate
from translate_module import translate_to_english
from users_db import init_user_db

app = Flask(__name__)
app.secret_key = "PPS"
CORS(app)

# Initialize DB table (only once)
try:
    init_user_db()
except Exception as e:
    print("⚠️ Skipping DB init (maybe table exists):", e)

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="users_db"
)

# ---------------- AUTH ROUTES ----------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']  # ❗ Plaintext as requested

        cur = db.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password))
        db.commit()
        cur.close()

        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and user['password'] == password:
            session['username'] = user['username']
            return redirect('/index')
        else:
            return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- TRANSLATION ROUTES ----------------

@app.route('/record_audio', methods=['POST'])
def record_audio():
    audio_file = "sample_audio.wav"
    text = transcribe_audio(audio_file)
    return jsonify({'transcribed_text': text})

# @app.route('/translate', methods=['POST'])
# def translate():
#     data = request.get_json()
#     input_text = data.get("input_text", "").strip()

#     if not input_text:
#         return jsonify({'error': 'Empty input text'}), 400

#     print("📥 Received text for translation:", input_text)

#     try:
#         standard_telugu, detected_dialect = detect_dialect_and_translate(input_text)
#         english_translation = translate_to_english(standard_telugu)

#         print("🔍 Dialect:", detected_dialect)
#         print("🧾 Standard Telugu:", standard_telugu)
#         print("🌍 English Translation:", english_translation)

#         return jsonify({
#             'dialect': detected_dialect,
#             'standard_telugu': standard_telugu,
#             'english_translation': english_translation
#         })
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({'error': 'Translation failed'}), 500

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    dialect_text = data.get("input_text", "")
    print(f"Received: {dialect_text}")

    standard_telugu, detected_dialect = detect_dialect_and_translate(dialect_text)
    print(f"Standard Telugu: {standard_telugu}, Dialect: {detected_dialect}")

    english_translation = translate_to_english(standard_telugu)
    print(f"English: {english_translation}")

    return jsonify({
        'dialect': detected_dialect,
        'standard_telugu': standard_telugu,
        'english_translation': english_translation
    })


@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    audio = request.files['audio_data']
    file_path = os.path.join("uploads", "recorded.wav")

    try:
        os.makedirs("uploads", exist_ok=True)
        audio.save(file_path)
        
        # Check if file has data
        file_size = os.path.getsize(file_path)
        print(f"✅ Saved file: {file_path} ({file_size} bytes)")

        if file_size < 5000:  # Less than 5 KB likely means silence
            return jsonify({'error': 'Audio too short or empty'}), 400

        text = transcribe_audio(file_path)
        print(f"✅ Transcribed Text: {text}")

        return jsonify({'transcribed_text': text})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Transcription failed: {str(e)}'}), 500


# ---------------- MAIN ----------------

if __name__ == '__main__':
    app.run(debug=True)
