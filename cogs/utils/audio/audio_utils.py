"""
Some utilities for downloading/dealing with audio.
"""

import youtube_dl
from uuid import uuid4
import concurrent.futures
import logging


log = logging.getLogger()


# Default options for most downloads
# Thanks to imayhaveborkedit for most of these
base_ytdl_options = {
    "format": "bestaudio/best",
    "outtmpl": ".tmp/%(title)s-%(id)s.%(ext)s",
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "no_warnings": True,
    "source_address": "0.0.0.0",
    "quiet": True
}

youtube_dl.utils.bug_reports_message = lambda: ''

# TODO: Create a generator for playlist downloads


class Downloader:

    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.client = youtube_dl.YoutubeDL(base_ytdl_options)

    def download_audio(self, url):
        """Download audio using yt-dl to a given path-like object."""
        with self.client:
            self.client.download([url])  # needs to be a list, otherwise it treats the string as an iterable
            log.info("Downloaded audio for {}".format(url))
        return

    def download_stats(self, url):
        with self.client:
            info = self.client.extract_info(url, download=False)
            info["expected_filename"] = self.client.prepare_filename(info)
            log.info("Extracted info for {}".format(url))
        return info

    async def download_stats_threaded(self, url):
        future = self.executor.submit(self.download_stats, url)

        # This should finish once the downloading is done
        concurrent.futures.wait([future], 30, return_when=concurrent.futures.FIRST_COMPLETED)
        return future.result()

    async def download_audio_threaded(self, url):
        """Adding an async wrapper around this """

        download_path = self.executor.submit(self.download_audio, url)

        # This should finish once the downloading is done
        # concurrent.futures.wait([download_path], 30, return_when=concurrent.futures.FIRST_COMPLETED)
        return download_path.result()