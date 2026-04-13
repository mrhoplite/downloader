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

            # This is the "Magic" configuration to bypass Data Center blocks
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                # Using an Android user-agent is the best way to get direct .mp4 links
                'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
                'http_headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                },
                # Bypassing the "Sign in to confirm" error
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Handling different platform response structures
                video_url = info.get('url')
                if not video_url and 'formats' in info:
                    # Look for a format that has both audio and video
                    formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') != 'none']
                    if formats:
                        video_url = formats[-1].get('url') # Get the highest quality

                title = info.get('title', 'Video File')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'url': video_url, 'title': title}).encode())

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # Send the error back so we can see it in the alert box
            self.wfile.write(json.dumps({'error': str(e), 'url': None}).encode())
