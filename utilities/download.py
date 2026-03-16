import yt_dlp
import time
import os

class Downloader:
    def __init__(self, base_path="downloads", default_retries=3, default_delay=2, default_resolution=1080):
        self.base_path = base_path
        self.default_retries = default_retries
        self.default_delay = default_delay
        self.default_resolution = default_resolution

    def _execute_download(self, url, options, retries=None):
        max_retries = retries if retries is not None else self.default_retries
        attempt = 0

        while attempt < max_retries:
            try:
                with yt_dlp.YoutubeDL(options) as ydl:
                    error_code = ydl.download([url])
                    if error_code == 0:
                        print(f"Successfully downloaded: {url}")
                        return True
                    else:
                        raise Exception(f"yt-dlp returned error code: {error_code}")

            except Exception as e:
                attempt += 1
                print(f"Download error (Attempt {attempt}/{max_retries}): {e}")

                if attempt >= max_retries:
                    print("Reached maximum retries. Aborting download.")
                    return False

                options['nocache'] = True
                time.sleep(self.default_delay)

    def _build_options(self, base_options, filename=None, sub_path=None, **kwargs):
        opts = base_options.copy()

        if sub_path:
            full_dir = os.path.join(self.base_path, sub_path)
        else:
            full_dir = self.base_path

        if filename:
            if "." not in filename and "%(ext)s" not in filename:
                filename = f"{filename}.%(ext)s"
            final_name = filename
        else:
            final_name = '%(title)s.%(ext)s'

        opts['outtmpl'] = os.path.join(full_dir, final_name)

        opts.update(kwargs)
        return opts

    def download_audio(self, url, filename=None, sub_path=None, retries=None, **kwargs):
        base_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': kwargs.pop('ext', 'mp3'),
                'preferredquality': kwargs.pop('bitrate', '320'),
            }],
            'noplaylist': True,
        }
        opts = self._build_options(base_opts, filename, sub_path, **kwargs)
        return self._execute_download(url, opts, retries)

    def download_video(self, url, filename=None, sub_path=None, resolution=None, retries=None, **kwargs):
        res = resolution if resolution else self.default_resolution
        format_str = f'bestvideo[height<={res}]+bestaudio/best[height<={res}]/best'

        base_opts = {
            'format': format_str,
            'merge_output_format': kwargs.pop('ext', 'mp4'),
        }
        opts = self._build_options(base_opts, filename, sub_path, **kwargs)
        return self._execute_download(url, opts, retries)

    def download_thumbnail(self, url, filename=None, sub_path=None, retries=None, **kwargs):
        base_opts = {
            'skip_download': True,
            'writethumbnail': True,
        }
        opts = self._build_options(base_opts, filename, sub_path, **kwargs)
        return self._execute_download(url, opts, retries)

    def download_social_media(self, url, filename=None, sub_path=None, resolution=None, retries=None, **kwargs):
        res = resolution if resolution else self.default_resolution
        format_str = f'best[height<={res}]/bestvideo[height<={res}]+bestaudio/best'

        base_opts = {
            'format': format_str,
            'extractor_args': {'tiktok': {'api_hostname': 'api16-normal-c-useast1a.tiktokv.com'}},
        }
        opts = self._build_options(base_opts, filename, sub_path, **kwargs)
        return self._execute_download(url, opts, retries)

    def download_generic(self, url, filename=None, sub_path=None, retries=None, **kwargs):
        base_opts = {
            'format': 'bestvideo+bestaudio/best',
        }
        opts = self._build_options(base_opts, filename, sub_path, **kwargs)
        return self._execute_download(url, opts, retries)

if __name__ == "__main__":
    from nanoid import generate
    alphabet = "qwertyuiopasdfghjklzxcvbnm"
    name = "-".join([generate(size=4, alphabet=alphabet) for _ in range(5)])
    print(f"> Target name: {name}")
    test_url = "https://www.youtube.com/watch?v=_wZfYtYwxro"
    downloader = Downloader(default_retries=1)
    downloader.download_audio(test_url, filename=name)