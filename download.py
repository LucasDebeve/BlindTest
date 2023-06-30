import yt_dlp
from pathlib import Path


path = str(Path(__file__).parent)

def download_video(link: str, title: str, output: str = 'temp') -> str:
    """
    Download a video from a link
    :param title: title of the video
    :param link: link of the video
    :param format: format of export
    :return: str (error message)
    """
    ydl_opts = {'format': f'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': f'{path}/{output}/' + title + '.%(ext)s',
                'merge_output_format': 'mp4',
                'restrictfilenames': True,
                'overwrites': True,
                'postprocessors': [
                    {
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4'
                    },
                    {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True
                    }
                ]}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            title = get_title(link, ydl)
            ydl.download([link])
    except Exception as e:
        if isinstance(e, yt_dlp.utils.DownloadError):
            pass
        elif hasattr(e, 'message'):
            return e.message
        else:
            return "The video cannot be downloaded"

    return "Video downloaded : " + title


def download_audio(link: str, title: str, format: str = 'mp3', output: str = 'temp') -> str:
    """
    Download a audio from a link
    :param title: title of the video
    :param link: link of the video
    :param format: format of export
    :return: str (error message)
    """
    ydl_opts = {'format': 'bestaudio/best',
                'outtmpl': f'{path}/{output}/' + title + '.%(ext)s',
                'merge_output_format': format,
                'restrictfilenames': True,
                'overwrites': True,
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': format,
                        'preferredquality': '192',
                    },
                    {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True
                    }
                ]
                }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            title = get_title(link, ydl)
            ydl.download([link])
    except Exception as e:
        if isinstance(e, yt_dlp.utils.DownloadError):
            pass
        elif hasattr(e, 'message'):
            return e.message
        else:
            return "The audio cannot be downloaded"

    return "Audio downloaded : " + title

def get_title(link: str, ydl = yt_dlp.YoutubeDL()) -> str:
    """
    Get the title of a video from a link
    :param ydl:
    :param link:
    :return: str
    """
    info_dict = ydl.extract_info(link, download=False)
    return info_dict.get('title', None)
