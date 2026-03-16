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

    download_path = 'downloads'
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    outtmpl = os.path.join(download_path, '%(title)s.%(ext)s')

    # FIX: Ensure ydl_opts is indented inside the download() function
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'cookiefile': 'cookies.txt',
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb', 'android'],
                'skip': ['authcheck'],
                # Uses the 2026 "Proof of Origin" framework
                'po_token': ['web+missing_pot']
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            # Find the actual path of the created mp3
            file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
            
            return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)