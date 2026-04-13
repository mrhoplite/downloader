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

            # 2026 Bypass Strategy: Use internal testing clients
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                # Impersonate a mobile browser to avoid the 'Sign in' wall
                'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android_test', 'web_embedded'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Try to get a direct MP4 URL
                video_url = None
                formats = info.get('formats', [])
                # Find the best format that has both audio and video
                for f in reversed(formats):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                        video_url = f.get('url')
                        break
                
                if not video_url:
                    video_url = info.get('url')

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'url': video_url,
                    'title': info.get('title', 'Video Download')
                }).encode())

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # Send the exact error so we can debug it
            self.wfile.write(json.dumps({'error': str(e)}).encode())
