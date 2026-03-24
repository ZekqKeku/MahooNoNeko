import yt_dlp
import time
import os
import math

class Download:
    def __init__(self, base_path="downloads", default_retries=3, default_delay=2, default_resolution=1080):
        self.base_path = base_path
        self.default_retries = default_retries
        self.default_delay = default_delay
        self.default_resolution = default_resolution

        self._quality_costs = {
            480: 0,
            720: 0,
            1080: 0,
            1440: 100,
            2160: 150
        }

        self._audio_costs = {
            'mp3': 0,
            'm4a': 0,
            'wav': 50,
            'flac': 50
        }

    def verify_media(self,
        url: str,
        max_length: int,
        max_size_gb: float,
        resolution: int = None,
        audio_format: str = 'mp3',
        is_audio: bool = False
    ) -> dict:
        base_cost = 10
        multiplier_per_minute = 2

        q_cost = 0
        if is_audio:
            q_cost = self._audio_costs.get(audio_format.lower(), 0)
        elif resolution is not None:
            q_cost = self._quality_costs.get(resolution, 0)

        options = {
            'noplaylist': True,
            'quiet': True,
            'skip_download': True
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info_dict = ydl.extract_info(url, download=False)

                if info_dict.get('is_live', False):
                    return {"success": False, "error": "live_stream"}

                duration_sec = info_dict.get('duration') or 0
                filesize = info_dict.get('filesize') or info_dict.get('filesize_approx') or 0

        except Exception as e:
            print(f"Error checking media: {e}")
            return {"success": False, "error": "fetch_error"}

        if duration_sec > max_length:
            return {"success": False, "error": "too_long", "duration": duration_sec, "max_length": max_length}

        max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        if filesize > max_size_bytes:
            estimated_gb = round(filesize / (1024**3), 2)
            return {"success": False, "error": "too_heavy", "filesize_gb": estimated_gb, "max_size_gb": max_size_gb}

        duration_min = math.ceil(duration_sec / 60)
        total_cost = base_cost + (duration_min * multiplier_per_minute) + q_cost

        return {
            "success": True,
            "cost": int(total_cost),
            "duration": duration_sec
        }

    def get_path(self, sub_path=None, file_name=None, ext=None):
        path = self.base_path
        if sub_path:
            path = os.path.join(path, sub_path)

        if file_name:
            if ext:
                full_file_name = f"{file_name}.{ext}"
            elif "." not in file_name and "%(ext)s" not in file_name:
                full_file_name = f"{file_name}.%(ext)s"
            else:
                full_file_name = file_name

            return os.path.join(path, full_file_name)

        return path

    def _execute_download(self, url, options, retries=None):
        max_retries = retries if retries is not None else self.default_retries
        attempt = 0

        while attempt < max_retries:
            try:
                with yt_dlp.YoutubeDL(options) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    print(f"Successfully downloaded: {url}")
                    return {
                        'success': True,
                        'duration': info_dict.get('duration', 0) if info_dict else 0
                    }

            except Exception as e:
                attempt += 1
                print(f"Download error (Attempt {attempt}/{max_retries}): {e}")

                if attempt >= max_retries:
                    print("Reached maximum retries. Aborting download.")
                    return {'success': False, 'duration': 0}

                options['nocache'] = True
                time.sleep(self.default_delay)

    def _build_options(self, base_options, file_name=None, sub_path=None, **kwargs):
        opts = base_options.copy()

        if sub_path:
            full_dir = os.path.join(self.base_path, sub_path)
        else:
            full_dir = self.base_path

        if file_name:
            if "." not in file_name and "%(ext)s" not in file_name:
                file_name = f"{file_name}.%(ext)s"
            final_name = file_name
        else:
            final_name = '%(title)s.%(ext)s'

        opts['outtmpl'] = os.path.join(full_dir, final_name)

        opts.update(kwargs)
        return opts

    def download_audio(self, url, file_name=None, sub_path=None, retries=None, **kwargs):
        base_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': kwargs.pop('ext', 'mp3'),
                'preferredquality': kwargs.pop('bitrate', '320'),
            }],
            'noplaylist': True,
        }
        opts = self._build_options(base_opts, file_name, sub_path, **kwargs)
        return self._execute_download(url, opts, retries)

    def download_video(self, url, file_name=None, sub_path=None, resolution=None, retries=None, **kwargs):
        social_media_domains = ['tiktok.com', 'instagram.com']

        if any(domain in url for domain in social_media_domains):
            return self.download_social_media(
                url,
                file_name=file_name,
                sub_path=sub_path,
                resolution=resolution,
                retries=retries,
                **kwargs
            )

        res = resolution if resolution else self.default_resolution
        format_str = f'bestvideo[height<={res}]+bestaudio/best[height<={res}]/best'

        base_opts = {
            'format': format_str,
            'merge_output_format': kwargs.pop('ext', 'mp4'),
        }
        opts = self._build_options(base_opts, file_name, sub_path, **kwargs)
        return self._execute_download(url, opts, retries)

    def download_thumbnail(self, url, file_name=None, sub_path=None, retries=None, **kwargs):
        base_opts = {
            'skip_download': True,
            'writethumbnail': True,
        }
        opts = self._build_options(base_opts, file_name, sub_path, **kwargs)
        return self._execute_download(url, opts, retries)

    def download_social_media(self, url, file_name=None, sub_path=None, resolution=None, retries=None, **kwargs):
        res = resolution if resolution else self.default_resolution
        format_str = f'best[height<={res}]/bestvideo[height<={res}]+bestaudio/best'

        base_opts = {
            'format': format_str,
            'extractor_args': {},
        }

        if 'tiktok.com' in url:
            base_opts['extractor_args']['tiktok'] = {'api_hostname': 'api16-normal-c-useast1a.tiktokv.com'}

        elif 'instagram.com' in url:
            base_opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            base_opts['playlist_items'] = '1'

        opts = self._build_options(base_opts, file_name, sub_path, **kwargs)
        return self._execute_download(url, opts, retries)

    def download_generic(self, url, file_name=None, sub_path=None, retries=None, **kwargs):
        base_opts = {
            'format': 'bestvideo+bestaudio/best',
        }
        opts = self._build_options(base_opts, file_name, sub_path, **kwargs)
        return self._execute_download(url, opts, retries)

    def remove_file(self, file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Successfully removed file: {file_path}")
                return True
            else:
                print(f"File not found, could not remove: {file_path}")
                return False
        except Exception as e:
            print(f"Error removing file: {e}")
            return False