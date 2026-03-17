import os
import time
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

    # Adding a small delay to mimic human behavior
    time.sleep(1)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extractor_args': {
            'youtube': {
                'player_client': ['web'],
                'skip': ['authcheck'],
                # YOUR TOKEN APPLIED HERE
                'po_token': ['web+Cgtqb2Zla1lkd0ppdyjM8OLNBjIKCgJLSBIEGgAgRGLfAgrcAjE2LllUPTVNSmIxQVV4ZHVMczNIN0JXZWo5RVlYS0pmaVMtNUMxNzRJNWIzRXJXQnZVYWh2Ml9fWmJFRDNYYUtzR0p6SXFMbU0xVXFFVTliZVF2Mnh6bGxxZ29heWxheUFXLVVwT3R2OGRwaklSSW53NGdRaW9ZV293aXRrNXVEa1lBWkJnNkxJMjV5QVlYb2MwUVY4QVZiWjdHN3lmYjRIb1RkR0x3TWxPR3IydG5ITXQ3dmY3cjNHLWRVdUhLUngwdTZfTVFteWVSNEtQeDhzY1Y5VG83WlhtejFSZEhVT29Nam9EWmZyQkhDU01pa1lLYkNyZGtzaWlWSncxbzdkMllYLV83UVBweGFPT09ONDI3a2tzQmpkQ3VPNkJLeWJEYUMyVDFrUG12S1ZPTXhlU2dfT0dvREc1dEVVcHFFWFZzeHFpTzVSanNSSEFCQk9ZWWJfbDdINW1Vdw%3D%3D'],
                # Standard visitor data to match web client
                'visitor_data': 'CgtxV293aXRrNXVEay4=', 
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
            
            return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(f"Download Error: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)