import io

from flask import Flask, render_template, request

from CREATOR_1_COMPETITORS import text_to_speech, send_to_chatgpt, AdvancedRecorder, url, elapikey

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
    with open('chatbot1.txt', 'r') as f:
        first_line = f.readline()

    with open('chatbot1.txt', 'w') as f:
        f.write(first_line)

    return 'Chat cleared successfully!' 

if __name__ == '__main__':
    app.run(debug=True)