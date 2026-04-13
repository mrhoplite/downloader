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

            # Your Cloudflare Proxy URL
            # Note: We use the direct worker URL here
            proxy_url = "https://m-proxy-api.zorawareu.workers.dev/?url="

            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                # We pass the proxy to yt-dlp
                'proxy': proxy_url,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # We only want the info, no downloading!
                info = ydl.extract_info(url, download=False)
                
                # Extract the direct link
                video_url = info.get('url')
                if not video_url and 'formats' in info:
                    # Select the best format with both audio and video
                    best_format = next((f for f in info['formats'][::-1] if f.get('acodec') != 'none' and f.get('vcodec') != 'none'), info['formats'][-1])
                    video_url = best_format.get('url')

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'url': video_url, 
                    'title': info.get('title', 'Video')
                }).encode())

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
