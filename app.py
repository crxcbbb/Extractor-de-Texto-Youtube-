import re
from flask import Flask, request, jsonify, render_template, send_from_directory
import speech_recognition as sr
import yt_dlp as youtube_dl
import os

if not os.path.exists('downloads'):
    os.makedirs('downloads')

app = Flask(__name__)
r = sr.Recognizer()

def download_audio(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'ffmpeg_location': 'C:/Users/cgonzalezc/Desktop/codigo/app web m/Extractor de Texto (Youtube)/ffmpeg-2024-08-11-git-43cde54fc1-full_build/bin/ffmpeg.exe',
            'ffprobe_location': 'C:/Users/cgonzalezc/Desktop/codigo/app web m/Extractor de Texto (Youtube)/ffmpeg-2024-08-11-git-43cde54fc1-full_build/bin/ffprobe.exe',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            base, ext = os.path.splitext(file_path)
            new_file = base + '.wav'
            if os.path.exists(new_file):
                return new_file
            else:
                print(f"El archivo {new_file} no se encontró.")
                return None
    except Exception as e:
        print(f"Error al descargar el audio: {e}")
        return None

def process_audio(file_path):
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)
        try:
            text = r.recognize_google(audio, language='es-ES')
            return clean_text(text)
        except Exception as e:
            print(f"Error al procesar el audio: {e}")
            return "Lo siento, no pude entender lo que dijiste."

def clean_text(text):
    text = re.sub(r'\b(um|eh|ah)\b', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([.,;])([^\s])', r'\1 \2', text)
    sentences = re.split(r'(?<=[.!?]) +', text)
    sentences = [s.capitalize() for s in sentences]
    organized_text = '\n\n'.join(sentences)
    return organized_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract_text', methods=['POST'])
def extract_text():
    data = request.get_json()
    video_url = data['url']
    audio_file = download_audio(video_url)
    if audio_file:
        text = process_audio(audio_file)
        os.remove(audio_file)
        return jsonify({'text': text})
    else:
        return jsonify({'text': 'Error al descargar el audio del video.'}), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5000)