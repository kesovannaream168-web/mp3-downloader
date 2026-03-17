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

    # FIXED: Indentation now correctly inside the download() function
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        # REMOVE the global 'cookiefile' line or set it to None here
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extractor_args': {
            'youtube': {
                'player_client': ['ios'],
                'skip': ['authcheck'],
                # This ensures we don't send cookies to the iOS client, 
                # which fixes the 'Skipping client ios' warning
                'no_cookies': True, 
                'po_token': ['web+missing_pot']
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            # Find the actual path and ensure it points to the final .mp3
            file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
            
            return send_file(file_path, as_attachment=True)
    except Exception as e:
        # Logs the specific error to Render so you can see why it failed
        print(f"Download Error: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)