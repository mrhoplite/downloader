# The URL to your new Cloudflare Proxy
        # We add the ?url= part so the worker knows what to fetch
        proxy_address = "https://m-proxy-api.zorawareu.workers.dev/?url="

        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            # This is the line that bypasses the bot check
            'proxy': proxy_address, 
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios'],
                    'skip': ['webpage']
                }
            }
        }
