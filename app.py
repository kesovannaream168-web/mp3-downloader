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

    # Indentation Fixed: This must be inside the download function
    outtmpl = os.path.join(download_path, '%(title)s.%(ext)s')

    ydl_opts = {
        # 'bestaudio' is sometimes hidden; asking for general 'best' helps bypass blocks
        'format': 'bestaudio/best', 
        'outtmpl': outtmpl,
        'cookiefile': 'cookies.txt', # Ensure this 22KB file is in your repo
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb'], # Most stable clients for PO tokens
                'skip': ['authcheck'],
                'po_token': ['web+missing_pot'] # Key 2026 bypass
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info is now correctly indented inside the 'with' block
            info = ydl.extract_info(video_url, download=True)
            # Find the actual path of the created mp3
            file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
            
            return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # Render uses the PORT environment variable
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)