from youtube_downolader import download_youtube_videos_from_file

if __name__ == '__main__':
    ffmpeg_path = \
        r"C:\Users\marku\PycharmProjects\ffmpeg-6.1-essentials_build\bin\ffmpeg.exe"
    download_youtube_videos_from_file("videos_url.txt", ffmpeg_path)
