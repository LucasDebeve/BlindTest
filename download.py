import yt_dlp


def download_video(link: str):
    """
    Download a video from a link
    :param link:
    :return: str
    """
    ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': 'downloaded/%(title)s.%(ext)s',
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
            title = get_title(ydl, link)
            ydl.download([link])
    except Exception as e:
        if isinstance(e, yt_dlp.utils.DownloadError):
            pass
        elif hasattr(e, 'message'):
            return e.message
        else:
            return "Error while downloading video"

    return "Video downloaded : " + title


def get_title(ydl, link: str) -> str:
    """
    Get the title of a video from a link
    :param ydl:
    :param link:
    :return: str
    """
    info_dict = ydl.extract_info(link, download=False)
    return info_dict.get('title', None)
