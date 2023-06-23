import os
from multiprocessing import Process, Queue
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from main import BlindTest

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def create_blind_test():
    if request.method == 'POST':
        folder = 'temp'  # Dossier temporaire pour stocker les fichiers envoyés
        timer = request.form['timer']
        guess_duration = int(request.form['guess_duration'])
        reveal_duration = int(request.form['reveal_duration'])
        number_of_videos = int(request.form['number_of_videos'])



        # Vérifier si des fichiers ont été envoyés
        files = request.files.getlist('file')

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
        return render_template('index.html')


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
