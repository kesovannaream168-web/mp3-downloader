import os
import yt_dlp
import subprocess
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def convert_to_mp3(input_file, title, artist):
    clean_title = "".join([c for c in title if c.isalnum() or c in (' ', '.', '_')]).strip()
    output_file = os.path.join(DOWNLOAD_FOLDER, f"{clean_title}.mp3")
    
    command = [
        'ffmpeg', '-y', '-i', input_file,
        '-metadata', f'title={title}',
        '-metadata', f'artist={artist}',
        '-codec:a', 'libmp3lame', '-qscale:a', '2',
        output_file
    ]
    subprocess.run(command, check=True)
    return f"{clean_title}.mp3"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'GET':
        return render_template('index.html')

    url = request.form.get('url')
    if not url:
        return "Please provide a URL", 400

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'cookiefile': 'cookies.txt', # Back to cookies, but with a twist
            'nocheckcertificate': True,
            # Force the 'web' client to bypass the OAuth rejection
            'extractor_args': {'youtube': {'player_client': ['web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown Title')
            uploader = info.get('uploader', 'Unknown Artist')
            downloaded_file = ydl.prepare_filename(info)

        mp3_filename = convert_to_mp3(downloaded_file, title, uploader)
        
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)

        return send_from_directory(DOWNLOAD_FOLDER, mp3_filename, as_attachment=True)

    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)