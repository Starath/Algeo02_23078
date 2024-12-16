import json
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from albumFinder import process_uploaded_image
from MusicFinder import compare_query_to_database
from DatabaseProcess import build_feature_database  # Import fungsi untuk membangun database fitur
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
MAPPER_FOLDER = BASE_DIR / "dataset" / "dataMapper"
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
                'imagePath': f"http://127.0.0.1:5000/dataset-image/{valid_files[idx].name}"
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
        # Step 1: Proses file MIDI menggunakan MusicFinder.py
        results = compare_query_to_database(str(file_path), MIDI_DATABASE_FILE, threshold=THRESHOLD)
        
        # Step 2: Load the mapper JSON
        mapper_path = MAPPER_FOLDER / "mapper.json"
        if not mapper_path.exists():
            return jsonify({'status': 'failed', 'message': 'Mapper file not found'}), 404
        
        with open(mapper_path, 'r') as f:
            mapper = json.load(f)

        # Step 3: Map the query results to pictures
        matched_results = []
        for result in results:  # Assuming results contain 'filename' of matched audio
            matched_audio = result.get('filename')
            for entry in mapper:
                if entry['audio_file'] == matched_audio:
                    matched_results.append({
                        'filename': entry["pic_name"],
                        'distance': result.get('similarity'),
                        'imagePath': f"http://127.0.0.1:5000/dataset-image/{entry["pic_name"]}"
                    })

        # Step 4: Return the matched results
        return jsonify({
            'status': 'success',
            'results': matched_results if matched_results else 'No picture matches found'
        })

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500
    finally:
        # Clean up the uploaded file
        file_path.unlink(missing_ok=True)

@app.route('/upload-zip/<category>', methods=['POST'])
def upload_zip(category):
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.zip'):
        return jsonify({'status': 'failed', 'message': 'Invalid ZIP file'}), 400

    # Tentukan folder tujuan berdasarkan kategori
    if category == "pictures":
        target_folder = DATASET_FOLDER
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    elif category == "audio":
        target_folder = AUDIO_FOLDER
        allowed_extensions = {'.midi', '.mid'}
    elif category == "mapper":
        target_folder = MAPPER_FOLDER
        allowed_extensions = {'.json', '.txt'}  # Allow all for mapper
    else:
        return jsonify({'status': 'failed', 'message': 'Invalid category'}), 400

    # Simpan file ZIP sementara
    zip_path = UPLOAD_FOLDER / secure_filename(file.filename)
    file.save(zip_path)

    try:
        # Hapus semua file lama di target folder
        if target_folder.exists():
            shutil.rmtree(target_folder)
        target_folder.mkdir(parents=True, exist_ok=True)

        # Ekstrak ZIP ke target folder
        with ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if allowed_extensions:
                    if not any(member.lower().endswith(ext) for ext in allowed_extensions):
                        continue  # Skip file yang tidak sesuai
                zip_ref.extract(member, target_folder)

        # Hapus file ZIP setelah selesai
        zip_path.unlink()

        # Buat daftar file valid setelah ekstraksi
        valid_files = [file for file in target_folder.glob("*") if file.suffix.lower() in allowed_extensions]
        
        # Proses khusus untuk kategori audio: build feature database
        if category == "audio":
            from DatabaseProcess import build_feature_database  # Import fungsi di sini agar modular
            build_feature_database(str(target_folder), str(MIDI_DATABASE_FILE))
            message = "Audio ZIP extracted and feature database updated successfully"
        else:
            message = f"{category.capitalize()} ZIP extracted successfully"

        # Respons untuk ZIP yang diproses
        dataset_result = [
            {
                'filename': file.name,
                'imagePath': f"http://127.0.0.1:5000/dataset-image/{file.name}" if category == "pictures" else None,
                'distance': None  # Hanya untuk gambar
            }
            for file in valid_files
        ]

        return jsonify({
            'status': 'success',
            'message': message,
            'data': dataset_result
        })

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

@app.route('/dataset-image/<filename>')
@cross_origin() 
def dataset_image(filename):
    file_path = DATASET_FOLDER / filename
    print(f"Looking for file at: {file_path}")  # Tambahkan ini untuk debugging
    if file_path.exists():
        # Tentukan jenis MIME file (e.g., image/jpeg, image/png)
        mime_type, _ = mimetypes.guess_type(str(file_path))
        print(f"Detected MIME type: {mime_type}")  # Debugging MIME type

        if mime_type:
            # Kirim file dengan MIME type
            return send_file(file_path, mimetype=mime_type)
        else:
            # Jika tidak bisa mendeteksi MIME type, kembalikan sebagai gambar default
            return send_file(file_path)
    else:
        # Jika file tidak ditemukan
        error_message = f"File {filename} not found at {file_path}"
        print(error_message)  # Debugging
        return jsonify({"error": error_message}), 404

if __name__ == '__main__':
    app.run(debug=True)
