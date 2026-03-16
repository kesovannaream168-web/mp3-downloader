import os
from flask import Flask, request, render_template, send_file
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    if not video_url:
        return "Error: No URL provided", 400

    # Ensure the downloads folder exists
    download_path = 'downloads'
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Output template for the file
    outtmpl = os.path.join(download_path, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio/best','formats': 'missing_pot',
        'outtmpl': outtmpl,
        'cookiefile': 'cookies.txt',
        'noplaylist': True,
        # This line is crucial for bypassing the bot check
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extractor_args': {
            'youtube': {
                # These arguments help bypass "Sign in" requirements
                'skip': ['authcheck', 'webpage_download'],
                'player_client': ['android', 'web']
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            # Find the actual path of the created mp3
            file_path = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # Render uses the PORT environment variable
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)