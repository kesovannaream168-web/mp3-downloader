import os
import yt_dlp
import subprocess
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

# Ensure the download folder exists
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
# Check if cookies.txt exists for debugging
if os.path.exists('cookies.txt'):
    print("✅ cookies.txt found in root directory")
else:
    print("❌ cookies.txt NOT FOUND in root directory")
def convert_to_mp3(input_file, title, artist):
    # Sanitize title to remove characters that might break file systems
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
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'cookiefile': 'cookies.txt',  # <--- Add this line!
}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown Title')
            uploader = info.get('uploader', 'Unknown Artist')
            downloaded_file = ydl.prepare_filename(info)

        # Convert to MP3 with dynamic artist
        mp3_filename = convert_to_mp3(downloaded_file, title, uploader)
        
        # Cleanup original video/audio file
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)

        return send_from_directory(DOWNLOAD_FOLDER, mp3_filename, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # The 'int(os.environ.get("PORT", 5000))' part is for the Cloud!
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)