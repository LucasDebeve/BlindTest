import math
import os
from random import choice, randint
from moviepy.editor import VideoFileClip, vfx, concatenate_videoclips, concatenate_audioclips, afx, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


class BlindTest:
    timer = ""
    folder = ""
    output = ""
    duration = (0, 0)
    path = ""
    width, height = 1280, 720

    def __init__(self, timer: str, folder: str, output: str = 'output', guess_duration: int = 5,
                 reveal_duration: int = 5,
                 number_of_videos: int = 3):
        """
        Constructeur de la classe BlindTest
        :param timer:
        :param folder:
        :param output:
        :param guess_duration:
        :param reveal_duration:
        :param number_of_videos:
        """
        self.timer = timer
        self.folder = folder
        self.output = output
        self.duration = (guess_duration, reveal_duration)
        self.path = os.path.join(self.output, "blind_test.mp4")
        # Count the number of videos in the folder
        self.export(number_of_videos)

    @staticmethod
    def get_video_duration(video_path: str):
        """
        Retourne la durée de la vidéo en secondes
        :param video_path:
        :return:
        """
        if not os.path.exists(video_path):
            raise ValueError("La vidéo n'existe pas : " + video_path)
        video = VideoFileClip(video_path)
        return math.floor(video.duration)

    def random_video(self, deja_vu: list):
        """
        Retourne une vidéo aléatoire dans le dossier self.folder, qui n'est pas dans la liste deja_vu
        :param deja_vu:
        :return:
        """
        videos = [video for video in os.listdir(self.folder) if video not in deja_vu]
        if not videos:
            return None
        return choice(videos)

    def export(self, number_of_videos: int):
        """
        Créer un blind test
        :param number_of_videos:
        :return:
        """
        clips = []
        audios = []
        deja_vu = []

        video = self.random_video(deja_vu)
        timer = VideoFileClip(self.timer).resize((self.width, self.height)).subclip(20 - self.duration[0],
                                                                                    20).fx(vfx.fadein,
                                                                                           0.5).fx(
            vfx.fadeout, 0.5)
        timer.audio = None

        # Si le nombre de vidéos demandé est supérieur ou égale au nombre de vidéos dans le dossier, on prend toutes les vidéos
        if number_of_videos >= len(os.listdir(self.folder)):
            number_of_videos = len(os.listdir(self.folder))
            # On enlève le coté aléatoire
            for i in range(number_of_videos):
                clips.append(timer)
                video = os.listdir(self.folder)[i]
                duration = self.get_video_duration(video_path=os.path.join(self.folder, video))

                begin = randint(5, duration - (self.duration[0] + self.duration[1]) - 10)

                clip = VideoFileClip(os.path.join(self.folder, video)).subclip(begin, begin + (
                        self.duration[0] + self.duration[1])).resize((self.width, self.height)).fx(
                    vfx.fadein, 1).fx(vfx.fadeout, 1)
                print(
                    f"Video: {video} - Begin: {begin} - End: {begin + (self.duration[0] + self.duration[1])} - Duration: {clip.duration}")
                # fadeout audio
                clip = clip.audio_fadeout(1).audio_fadein(1).fx(afx.audio_normalize)
                audios.append(clip.audio)

                clip = clip.subclip(self.duration[0], self.duration[0] + self.duration[1]).fx(vfx.mirror_x)
                clip.audio = None

                # Generate a text clip
                txt_clip = TextClip(video[:-4], fontsize=(75 if len(video) - 4 < 30 else 50), color='black',
                                    font='Arial-Black', stroke_color='white',
                                    stroke_width=2).set_position('center').set_duration(self.duration[1])
                clip = CompositeVideoClip([clip, txt_clip])

                clips.append(clip)
        else:
            i = 0
            while i < number_of_videos and video is not None:
                clips.append(timer)

                duration = self.get_video_duration(video_path=os.path.join(self.folder, video))

                begin = randint(5, duration - (self.duration[0] + self.duration[1]) - 10)

                clip = VideoFileClip(os.path.join(self.folder, video)).subclip(begin, begin + (
                        self.duration[0] + self.duration[1])).resize((self.width, self.height)).fx(
                    vfx.fadein, 1).fx(vfx.fadeout, 1)
                print(
                    f"Video: {video} - Begin: {begin} - End: {begin + (self.duration[0] + self.duration[1])} - Duration: {clip.duration}")
                # fadeout audio
                clip = clip.audio_fadeout(1).audio_fadein(1).fx(afx.audio_normalize)
                audios.append(clip.audio)

                clip = clip.subclip(self.duration[0], self.duration[0] + self.duration[1])
                clip.audio = None

                # Generate a text clip
                txt_clip = TextClip(video[:-4], fontsize=(75 if len(video) - 4 < 30 else 50), color='black',
                                    font='Arial-Black', stroke_color='white',
                                    stroke_width=2).set_position('center').set_duration(self.duration[1])
                clip = CompositeVideoClip([clip, txt_clip])

                clips.append(clip)

                deja_vu.append(video)
                video = self.random_video(deja_vu)

                i += 1

        combined_clip = concatenate_videoclips(clips).set_audio(concatenate_audioclips(audios))

        # Verify if output folder exists
        os.makedirs(self.output, exist_ok=True)

        i = 1
        path = os.path.join(self.output, f"blind_test[{i}].mp4")
        while os.path.exists(path):
            i += 1
            path = os.path.join(self.output, f"blind_test[{i}].mp4")
        self.path = path
        combined_clip.write_videofile(self.path, fps=24, codec='', audio_codec='aac')

        # Close all files
        combined_clip.close()
        for clip in clips:
            clip.close()


if __name__ == '__main__':
    bt = BlindTest('src\\Timer.mp4', 'X:\\Blind test\\Openings', number_of_videos=2)
