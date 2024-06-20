import os

import httpx
import sounddevice as sd
import soundfile as sf
# import numpy as np
import requests
from colorama import Fore, Style, init
from pydub import AudioSegment
#from pydub.playback import play
from openai import OpenAI
import time
#from pynput import keyboard
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
elapikey = os.getenv('ELAB_API_KEY')
url = os.getenv('URL')


# first_audio = AudioSegment.from_mp3('first message.wav')
init()


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


client = OpenAI(api_key=api_key)

conversation1 = []
chatbot1 = open_file('chatbot1.txt')
file_path = 'chatbot1.txt'


def send_to_chatgpt(transcription_text):
    # Add user message from transcription
    with open(file_path, 'a') as file:  # 'a' opens the file in append mode
        file.write(f"\nuser: {transcription_text}")  # Use the transcription text as the user's message

    # Prepare the messages list
    messages = []
    with open(file_path, 'r') as file:
        for line in file:
            # Assuming each line is in the format "role: message"
            role, content = line.strip().split(": ", 1)  # Split on the first colon and space
            messages.append({"role": role, "content": content})

    # Create the chat completion
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    # Extract and print the response text
    chat_response_text = response.choices[0].message.content

    # print(chat_response_text)

    # Append the response text to the file
    with open(file_path, 'a') as file:  # 'a' opens the file in append mode
        file.write(f"\nassistant: {chat_response_text}")  # Write the role and content in the expected format

    return chat_response_text


def text_to_speech(text, url, elapikey):
    CHUNK_SIZE = 1024

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elapikey
    }

    data = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.9,
            "similarity_boost": 1
        }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    audio = AudioSegment.from_mp3('output.mp3')
    # audiopause = AudioSegment.from_mp3('pause.mp3')
    # play(audio)
    return audio


class AdvancedRecorder:

    def __init__(self):
        pass
    # def __init__(self, fs=44100, filename='myrecording.wav'):
    #     self.fs = fs
    #     self.filename = filename
    #     self.recording = False
    #     self.frames = []
    #     self.stream = sd.InputStream(callback=self.audio_callback, samplerate=self.fs, channels=1)
    #
    # def audio_callback(self, indata, frames, time, status):
    #     if self.recording:
    #         self.frames.append(indata.copy())
    #
    # def toggle_recording(self):
    #     if not self.recording:
    #         self.start_recording()
    #     else:
    #         self.stop_recording_and_process()
    #
    # def start_recording(self):
    #     self.recording = True
    #     self.frames = []
    #     self.stream.start()
    #     print("Recording started...")
    #
    # def stop_recording_and_process(self):
    #     self.recording = False
    #     self.stream.stop()
    #     recording = np.concatenate(self.frames, axis=0)
    #     sf.write(self.filename, recording, self.fs)
    #     print("Recording stopped.")
    #     transcription_text = self.transcribe_audio()

        # print("Transcribed:", transcription_text)
    @staticmethod
    def transcribe_audio(filepath):
        with open(filepath, 'rb') as file:
            transcription_response = client.audio.transcriptions.create(model="whisper-1", file=file)
            transcription_text = transcription_response.text  # or adjust based on actual API response
        return transcription_text


recorder = AdvancedRecorder()

press_count = 0
max_presses = 2


# def on_press(key):
#     global listener
#     if key == keyboard.Key.space:
#         if recorder.recording:
#             recorder.stop_recording_and_process()
#             transcription_text = recorder.transcribe_audio()
#             chat_response = send_to_chatgpt(transcription_text)  # Send transcription to ChatGPT and get response
#             text_to_speech(chat_response, url, elapikey)  # Convert response to speech
#             recorder.start_recording()  # Restart recording after processing
#
#
# def start_main_loop():
#     print(Fore.YELLOW + "Recording started. Press the space bar to stop and restart recording." + Style.RESET_ALL)
#     recorder.start_recording()  # Start recording immediately
#     listener = keyboard.Listener(on_press=on_press)
#     listener.start()
#
#     try:
#         while True:
#             time.sleep(0.1)  # Sleep a little to prevent busy waiting
#     except KeyboardInterrupt:
#         print("Exiting program...")
#         listener.stop()
#         return


# if __name__ == "__main__":
#     start_main_loop()
