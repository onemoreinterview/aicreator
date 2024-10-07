import datetime
import io
import os
from datetime import datetime

from flask import Flask, render_template, request

from CREATOR_1_COMPETITORS import text_to_speech, send_to_chatgpt, AdvancedRecorder, url, elapikey

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/roleplay1')
def roleplay1():
    return render_template('roleplay1.html')

@app.route('/roleplay2')
def roleplay2():
    return render_template('roleplay2.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return 'No audio file uploaded', 400

    audio_file = request.files['audio']
    # audio = io.BytesIO(audio_file.read())  #AudioSegment.from_file(audio_file)
    with open('input.wav', 'wb') as input_audio:
        input_audio.write(audio_file.read())

    transcription_text = AdvancedRecorder.transcribe_audio('input.wav')
    chat_response = send_to_chatgpt(transcription_text)
    response_audio = text_to_speech(chat_response, url, elapikey)

    # Process the audio file (example: apply a simple effect like reversing the audio)
    processed_audio = response_audio

    # Save the processed audio to a BytesIO object
    processed_audio_io = io.BytesIO()
    processed_audio.export(processed_audio_io, format="wav")

    # Move the cursor to the beginning of the BytesIO object
    processed_audio_io.seek(0)

    return processed_audio_io

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Construct the paths
    chatbot_path = 'chatbot1.txt'
    conversations_dir = 'conversations'
    conversation_path = os.path.join(conversations_dir, f'conversation_{timestamp}.txt')

    # Ensure the conversations directory exists
    os.makedirs(conversations_dir, exist_ok=True)

    # Copy the chat history
    try:
        with open(chatbot_path, 'r') as f_src, open(conversation_path, 'w') as f_dst:
            f_dst.write(f_src.read())
    except IOError as e:
        return f'Error saving conversation: {e}', 500

    # Clear the chat history
    try:
        with open(chatbot_path, 'r') as f:
            first_line = f.readline()
        with open(chatbot_path, 'w') as f:
            f.write(first_line)
    except IOError as e:
        return f'Error clearing chat: {e}', 500

    return 'Chat cleared successfully!'

if __name__ == '__main__':
    app.run(debug=True)
