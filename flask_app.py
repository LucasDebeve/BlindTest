import os
from multiprocessing import Process, Queue
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from main import BlindTest

app = Flask(__name__)
app.secret_key = 'secret_key'


@app.route('/', methods=['GET', 'POST'])
def create_blind_test():
    if request.method == 'POST':
        if 'guess_duration' not in request.form or 'reveal_duration' not in request.form or 'number_of_videos' not in request.form or \
                request.form['guess_duration'] == '' or request.form['reveal_duration'] == '' or request.form['number_of_videos'] == '' \
                or int(request.form['guess_duration']) <= 0 or \
                int(request.form['reveal_duration']) <= 0 or int(request.form['number_of_videos']) <= 0:
            return render_template('index.html')

        folder = 'temp'  # Dossier temporaire pour stocker les fichiers envoyés
        guess_duration = int(request.form['guess_duration'])
        reveal_duration = int(request.form['reveal_duration'])
        number_of_videos = int(request.form['number_of_videos'])

        # Vérifier si des fichiers ont été envoyés, sinon lancer une alerte
        if 'file' not in request.files or request.files['file'].filename == '':
            return render_template('index.html', isAlert=True, error='No source file has been uploaded')

        files = request.files.getlist('file')

        # Vérifier si un fichier timer a été envoyé sinon utiliser le timer par défaut
        if 'timer' not in request.files or request.files['timer'].filename == '':
            timer = 'src\\Timer.mp4'
        else:
            folder_timer = 'temp\\timer'
            timer_file = request.files.get('timer')
            timer_filename = secure_filename(timer_file.filename)
            timer_file.save(os.path.join(folder_timer, timer_filename))
            timer = os.path.join(folder_timer, timer_filename)

        # Enregistrer les fichiers dans le dossier temporaire
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(folder, filename))

        blind_test_path = create_blindtest_wrapper(timer, folder, guess_duration, reveal_duration, number_of_videos)

        # Supprimer les fichiers du dossier temporaire après utilisation
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return send_file(blind_test_path, as_attachment=True)
    else:
        return render_template('index.html', isAlert=False, error='')


def create_blindtest(timer, folder, guess_duration, reveal_duration, number_of_videos, return_queue):
    blind_test = BlindTest(timer=timer, folder=folder, guess_duration=guess_duration,
                           reveal_duration=reveal_duration, number_of_videos=number_of_videos)
    return_queue.put(blind_test.path)


def create_blindtest_wrapper(timer, folder, guess_duration, reveal_duration, number_of_videos):
    return_queue = Queue()
    converter = Process(target=create_blindtest,
                        args=(timer, folder, guess_duration, reveal_duration, number_of_videos, return_queue))
    converter.start()
    converter.join()
    blind_test_path = return_queue.get()

    return blind_test_path


if __name__ == '__main__':
    app.run(debug=True)
