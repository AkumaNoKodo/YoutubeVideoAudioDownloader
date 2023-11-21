import subprocess
import time
from datetime import datetime
import validators
from pytube import YouTube
import os


def timing_decorator(func):
    """
    A decorator to measure and print the execution time of a function.

    Args:
    func (function): The function to be wrapped.

    Returns:
    function: The wrapped function with timing functionality.
    """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"Process time: {func.__name__}: {time.perf_counter() - start_time} [second]")
        return result

    return wrapper


def download_youtube_videos_from_file(file_path: str, ffmpeg_path: str) -> None:
    """
    Reads a file containing YouTube URLs and initiates the download process for each URL.

    This function processes each line of the input file as a separate YouTube URL. It supports an optional
    prefix 'a' for each URL to indicate downloading in audio-only mode. Each line should either be a single URL,
    or an 'a' followed by a space and then the URL.

    Args:
    file_path (str): The file system path to a text file containing YouTube URLs, one per line.
                     Optional 'a ' prefix per line to download audio only.
    ffmpeg_path (str): The full path to the "ffmpeg.exe" file.
    """
    with open(file_path, 'r') as file:
        for line in file:
            audio_only = False
            bad_line_message = f"Bad line: {line}"
            url = line.strip().split(" ")
            if not url:
                print(bad_line_message)
                continue

            if len(url) > 2:
                print(bad_line_message)
                continue

            if len(url) == 2 and validators.url(url[1]):
                if url[0] == "a":
                    audio_only = True
                    url = url[1]
                else:
                    print(bad_line_message)
                    continue

            if len(url) == 1 and not validators.url(url[0]):
                print(bad_line_message)
                continue

            try:
                download_from_youtube(str(url), ffmpeg_path, audio_only)
            except Exception as e:
                print(e)


@timing_decorator
def download_from_youtube(url: str, ffmpeg_path: str, audio_only: bool = False) -> None:
    """
    Downloads a video from YouTube, optionally converting it to audio-only format.

    This function downloads a YouTube video from a given URL. If 'audio_only' is set to True, it converts the
    video into an MP3 file. Otherwise, it downloads the video as an MKV file. The function uses ffmpeg for
    conversion and requires ffmpeg executable path to be set correctly.

    Args:
    url (str): The URL of the YouTube video to download.
    audio_only (bool, optional): If True, download and convert to audio-only format (MP3). Defaults to False.
    ffmpeg_path (str): The full path to the "ffmpeg.exe" file.
    """
    print(url)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    yt = YouTube(url)

    video_title = yt.title.replace(' ', '_').replace('/', '_')
    output_filename = f"{video_title}_{timestamp}.mkv" if not audio_only else f"{video_title}_{timestamp}.mp3"

    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
    audio_bitrate = ''.join(filter(str.isdigit, audio_stream.abr)) + 'k'
    audio_filename = f"audio_{timestamp}.mp4"
    print("Download audio start...")
    audio_stream.download(filename=audio_filename)
    print("Done")

    if not audio_only:
        video_stream = yt.streams.filter(only_video=True).order_by('resolution').desc().first()
        video_filename = f"video_{timestamp}.mp4"
        print("Download video start...")
        video_stream.download(filename=video_filename)
        print("Done")

        command = [
            ffmpeg_path, '-y', '-i', video_filename, '-i', audio_filename,
            '-c:v', 'hevc_nvenc', '-preset', 'fast', '-profile:v', 'main', '-c:a', 'aac', '-b:a', audio_bitrate,
            output_filename
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            print(line, end='')

        os.remove(video_filename)
    else:
        command = [
            ffmpeg_path, '-y', '-i', audio_filename, '-b:a', audio_bitrate, output_filename
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            print(line, end='')

    os.remove(audio_filename)
