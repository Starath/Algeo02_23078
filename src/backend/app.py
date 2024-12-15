from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
from albumFinder import process_uploaded_image
from MusicFinder import compare_query_to_database
from pathlib import Path
import mimetypes
import shutil
from zipfile import ZipFile

app = Flask(__name__)
CORS(app)

# Path Konfigurasi
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
DATASET_FOLDER = BASE_DIR / "dataset" / "dataGambar"
AUDIO_FOLDER = BASE_DIR / "dataset" / "dataAudio"
MIDI_DATABASE_FILE = "midi_feature_database.json"
THRESHOLD = 0.55  # Threshold similarity untuk file MIDI

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask API!', 'routes': ['/upload-picture', '/upload-midi', '/upload-zip/<category>']})

# Endpoint untuk upload file gambar
@app.route('/upload-picture', methods=['POST'])
def upload_picture():
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'failed', 'message': 'No selected file'}), 400

    file_path = UPLOAD_FOLDER / secure_filename(file.filename)
    file.save(file_path)

    try:
        # Proses file menggunakan albumFinder.py
        result, valid_files = process_uploaded_image(str(file_path), str(DATASET_FOLDER))
        sorted_result = [
            {
                'filename': valid_files[idx].name,
                'distance': distance,
                'imagePath': f"/dataset-image/{valid_files[idx].name}"
            }
            for idx, distance in result
        ]
        return jsonify({'status': 'success', 'data': sorted_result})

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

# Endpoint untuk upload file MIDI
@app.route('/upload-midi', methods=['POST'])
def upload_midi():
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': 'No file part'}), 400

    file = request.files['file']
    if not file.filename.endswith('.mid'):
        return jsonify({'status': 'failed', 'message': 'Invalid MIDI file'}), 400

    file_path = UPLOAD_FOLDER / secure_filename(file.filename)
    file.save(file_path)

    try:
        # Proses file MIDI menggunakan MusicFinder.py
        results = compare_query_to_database(str(file_path), MIDI_DATABASE_FILE, threshold=THRESHOLD)
        return jsonify({'status': 'success', 'results': results})

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

# Endpoint untuk upload ZIP file
@app.route('/upload-zip/<category>', methods=['POST'])
def upload_zip(category):
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.zip'):
        return jsonify({'status': 'failed', 'message': 'Invalid ZIP file'}), 400

    if category not in ['pictures', 'audio', 'mapper']:
        return jsonify({'status': 'failed', 'message': 'Invalid category'}), 400

    target_folder = BASE_DIR / "dataset" / f"data{category.capitalize()}"
    zip_path = UPLOAD_FOLDER / secure_filename(file.filename)
    file.save(zip_path)

    try:
        # Hapus isi folder lama dan ekstrak ZIP
        if target_folder.exists():
            shutil.rmtree(target_folder)
        target_folder.mkdir(parents=True, exist_ok=True)

        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_folder)

        zip_path.unlink()  # Hapus file ZIP

        extracted_files = [f.name for f in target_folder.iterdir()]
        return jsonify({
            'status': 'success',
            'message': f'{category.capitalize()} ZIP extracted successfully',
            'data': extracted_files
        })

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

@app.route('/dataset-image/<filename>')
def dataset_image(filename):
    file_path = DATASET_FOLDER / filename
    if file_path.exists():
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return send_file(file_path, mimetype=mime_type or "image/jpeg")
    return jsonify({"error": f"File {filename} not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
