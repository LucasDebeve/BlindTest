import os
from multiprocessing import Process, Queue
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from main import BlindTest
import datetime
from download import download_video, get_title

app = Flask(__name__)
app.secret_key = 'secret_key'


@app.route('/')
def index():
    """
    Display the index page
    :return:
    """
    filenames = getOutputFiles()
    return render_template('index.html', isAlert=False, error='', files=filenames)


@app.route('/create', methods=['GET', 'POST'])
def create_blind_test():
    """
    Create a blind test from the files sent by the user
    :return:
    """
    if request.method == 'POST':
        if 'links' not in request.form or 'guess_duration' not in request.form or 'reveal_duration' not in request.form or 'number_of_videos' not in request.form or \
                request.form['guess_duration'] == '' or request.form['reveal_duration'] == '' \
                or request.form['number_of_videos'] == '' \
                or int(request.form['guess_duration']) <= 0 or \
                int(request.form['reveal_duration']) <= 0 or int(request.form['number_of_videos']) <= 0:
            return render_template('index.html', isAlert=True, error='Bad request', files=getOutputFiles())

        folder = 'temp'  # Dossier temporaire pour stocker les fichiers envoyés
        guess_duration = int(request.form['guess_duration'])
        reveal_duration = int(request.form['reveal_duration'])
        number_of_videos = int(request.form['number_of_videos'])

        # Vérifier si des fichiers ont été envoyés, sinon lancer une alerte
        if 'file' not in request.files or request.files['file'].filename == '':
            if request.form['links'] == '':
                return render_template('index.html', isAlert=True, error='No source file has been uploaded',
                                       files=getOutputFiles())
            else:
                download_from_yt(request.form['links'], number_of_videos)

        else:
            files = request.files.getlist('file')
            # Enregistrer les fichiers dans le dossier temporaire
            for file in files:
                filename = secure_filename(file.filename)
                file.save(os.path.join(folder, filename))

        # Vérifier si un fichier timer a été envoyé sinon utiliser le timer par défaut
        if 'timer' not in request.files or request.files['timer'].filename == '':
            timer = 'src\\Timer.mp4'
        else:
            folder_timer = 'temp\\timer'
            timer_file = request.files.get('timer')
            timer_filename = secure_filename(timer_file.filename)
            timer_file.save(os.path.join(folder_timer, timer_filename))
            timer = os.path.join(folder_timer, timer_filename)

        blind_test_path = create_blindtest_wrapper(timer, folder, guess_duration, reveal_duration, number_of_videos)

        # Supprimer les fichiers du dossier temporaire après utilisation
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        blind_test_id = os.path.basename(blind_test_path)[11:-5]
        return redirect(url_for('downloadPage', id=blind_test_id))
    else:
        return redirect(url_for('index'))


@app.route('/download/<int:id>', methods=['GET', 'POST'])
def downloadPage(id):
    """
    Interface to download the blind test
    :param id:
    :return:
    """
    if request.method == 'GET':
        path = 'output\\blind_test[' + str(id) + '].mp4'
        filename = os.path.join(path)
        if not os.path.exists(filename) or not os.path.isfile(filename) or os.path.getsize(
                filename) == 0 or not filename.endswith('.mp4'):
            return render_template('error.html', error='The blind test does not exist or is not available')
        created_date = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
        closure_date = created_date + datetime.timedelta(days=1)
        return render_template('download.html', file_id=id, title=os.path.basename(filename),
                               created_date=created_date.strftime("%d-%m-%Y  %H:%M:%S"),
                               closure_date=closure_date.strftime("%d-%m-%Y  %H:%M:%S"),
                               files=getOutputFiles())
    else:
        return redirect(url_for('index'))


@app.route('/download/<int:id>/download', methods=['GET', 'POST'])
def download(id):
    """
    Download the blind test
    :param id:
    :return:
    """
    if request.method == 'GET':
        path = 'output\\blind_test[' + str(id) + '].mp4'
        filename = os.path.join(path)
        if not os.path.exists(filename) or not os.path.isfile(filename) or os.path.getsize(
                filename) == 0 or not filename.endswith('.mp4'):
            return render_template('error.html', error='The blind test does not exist or is not available')
        return send_file(filename, as_attachment=True)
    else:
        return redirect(url_for('index'))


def create_blindtest(timer: str, folder: str, guess_duration: int, reveal_duration: int,
                     number_of_videos: int, return_queue: Queue) -> None:
    """
    Create a blind test and put the path to the blind test in the return queue. Call by the create_blindtest_wrapper
    :param timer: path to the timer video
    :param folder: path to the folder containing the videos
    :param guess_duration: duration of the guess
    :param reveal_duration: duration of the reveal
    :param number_of_videos: number of videos
    :param return_queue: queue to return the path to the blind test
    :return: None
    """
    blind_test = BlindTest(timer=timer, folder=folder, guess_duration=guess_duration,
                           reveal_duration=reveal_duration, number_of_videos=number_of_videos)
    return_queue.put(blind_test.path)


def create_blindtest_wrapper(timer: str, folder: str, guess_duration: int, reveal_duration: int,
                             number_of_videos: int) -> str:
    """
    Create a blind test wrapper
    :param timer: path to the timer video
    :param folder: path to the folder containing the videos
    :param guess_duration: duration of the guess
    :param reveal_duration: duration of the reveal
    :param number_of_videos: number of videos
    :return: blind_test_path: path to the blind test
    """
    return_queue = Queue()
    converter = Process(target=create_blindtest,
                        args=(timer, folder, guess_duration, reveal_duration, number_of_videos, return_queue))
    converter.start()
    converter.join()
    blind_test_path = return_queue.get()

    return blind_test_path


def getOutputFiles():
    """
    Get the list of the output files
    :return: list of the output files
    """
    files = os.listdir('output')
    filenames = []
    for file in files:
        if file.startswith('blind_test'):
            name = file[:-4]
            id_file = file[11:-5]
            date = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join('output', file))).strftime(
                '%d/%m/%Y %H:%M:%S')
            if (datetime.datetime.now() - datetime.datetime.fromtimestamp(
                    os.path.getmtime(os.path.join('output', file)))).days > 1:
                os.remove(os.path.join('output', file))
            else:
                filenames.append((id_file, name, date))
    return filenames


def download_from_yt(text: str, number_of_videos) -> str:
    res = ""
    list_of_videos = text.split('\r\n')
    if len(list_of_videos) < 1:
        return "No video found"
    if len(list_of_videos) > number_of_videos:
        list_of_videos = list_of_videos[:number_of_videos]
    for video in list_of_videos:
        if video.startswith('https://www.youtube.com/watch?v='):
            link, title = video.split(' : ')[0:2]
            res += download_video(link, title) + "<br>"
    return res


if __name__ == '__main__':
    app.run(debug=True)
