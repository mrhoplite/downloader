from http.server import BaseHTTPRequestHandler
import yt_dlp
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            url = data.get('url')

            if not url:
                raise ValueError("No URL provided")

            # High-compatibility settings for Cloud Hosting
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                # This force-uses a mobile user agent which often bypasses data center blocks
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
                'extract_flat': False,
                'socket_timeout': 10,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 'download=False' is crucial; Vercel will crash if you try to save the file
                info = ydl.extract_info(url, download=False)
                
                # Try to find the best direct URL
                video_url = info.get('url')
                if not video_url and 'formats' in info:
                    # Filter for formats that include both audio and video
                    for f in info['formats']:
                        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                            video_url = f.get('url')
                            break

                title = info.get('title', 'Downloaded Video')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                # Allow the browser to access this from your domain
                self.send_header('Access-Control-Allow-Origin', '*') 
                self.end_headers()
                self.wfile.write(json.dumps({'url': video_url, 'title': title}).encode())

        except Exception as e:
            self.send_response(200) # Send 200 so we can read the error in the console
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e), 'url': None}).encode())
