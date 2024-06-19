from flask import Flask, render_template, jsonify, Response
from pydub import AudioSegment
import wave
import pyaudio
import threading
import io
from CREATOR_1_COMPETITORS import AdvancedRecorder, send_to_chatgpt, text_to_speech, url, elapikey

app = Flask(__name__)

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
OUTPUT_FILENAME = "output.wav"

# Initialize PyAudio
audio = pyaudio.PyAudio()
frames = []
recording = False
stream = None
device_index = None  # Initialize as None, set later


def start_recording():
    global stream, frames, recording
    frames = []
    try:
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            input_device_index=device_index,
                            frames_per_buffer=CHUNK)
        recording = True
        while recording:
            data = stream.read(CHUNK)
            frames.append(data)
    except Exception as e:
        print(f"Error in start_recording: {e}")


def stop_recording():
    global stream, recording
    recording = False
    stream.stop_stream()
    stream.close()

    # Save the audio file
    wf = wave.open(OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return OUTPUT_FILENAME


def process_audio(input_file):
    # Load the audio file
    transcription_text = AdvancedRecorder.transcribe_audio(input_file)
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_input_devices', methods=['GET'])
def get_input_devices():
    input_devices = []
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            input_devices.append({"index": i, "name": info["name"]})
    return jsonify(input_devices)


@app.route('/set_device/<int:device_id>', methods=['POST'])
def set_device(device_id):
    global device_index
    device_index = device_id
    return jsonify({"status": "device_set", "device_index": device_index})


@app.route('/start_record', methods=['POST'])
def handle_start_record():
    thread = threading.Thread(target=start_recording)
    thread.start()
    return jsonify({"status": "recording_started"})


@app.route('/stop_record', methods=['POST'])
def handle_stop_record():
    file_path = stop_recording()
    processed_audio_io = process_audio(file_path)
    return Response(processed_audio_io, mimetype="audio/wav")


# if __name__ == '__main__':
#     app.run(debug=True)
