import json
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
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
        result, valid_files, time = process_uploaded_image(str(file_path), str(DATASET_FOLDER))
        
        # Baca file mapper.json
        mapper_path = MAPPER_FOLDER / "mapper.json"
        if not mapper_path.exists():
            return jsonify({'status': 'failed', 'message': 'Mapper file not found'}), 404
        
        with open(mapper_path, 'r') as f:
            mapper = json.load(f)

        # Cocokkan gambar dengan nama audio dari mapper.json
        mapped_results = []
        for idx, distance in result:
            image_path = Path(valid_files[idx])  # Ensure it's a Path object
            image_name = image_path.name  # Get the filename from the Path object
            audio_name = None
            
            # Search for corresponding audio file in mapper
            for entry in mapper:
                if entry['pic_name'] == image_name:
                    audio_name = entry['audio_file']
                    break
            
            mapped_results.append({
                'filename': audio_name if audio_name else image_name,  # Use audio name if available
                'distance': distance,
                'imagePath': f"http://127.0.0.1:5000/dataset-image/{image_name}"
            })

        return jsonify({'status': 'success', 'data': mapped_results, 'execution_time': time})

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
                    distance = float(result.get('similarity'))*100
                    matched_results.append({
                        'filename': entry["audio_file"],
                        'distance': distance,
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
    if not file:
        return jsonify({'status': 'failed', 'message': 'Invalid file or not a zip file'}), 400

    # Tentukan folder tujuan berdasarkan kategori
    if category == "pictures":
        target_folder = DATASET_FOLDER
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.zip'}
    elif category == "audio":
        target_folder = BASE_DIR / "dataset" / "dataAudio"
        allowed_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.midi', '.mid', '.zip'}
    elif category == "mapper":
        target_folder = MAPPER_FOLDER
        allowed_extensions = {'.json', '.txt', '.zip'}
    else:
        return jsonify({'status': 'failed', 'message': 'Invalid category'}), 400

    #target_folder.mkdir(parents=True, exist_ok=True)  # Buat folder jika belum ada

    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        return jsonify({'status': 'failed', 'message': f'Unsupported file type: {file_extension}'}), 400

    file_path = target_folder / secure_filename(file.filename)

    try:
        if file_extension == '.zip':
            # Ekstrak file ZIP
            with ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
        else:
            # Simpan file langsung jika bukan file ZIP
            file.save(file_path)

        return jsonify({'status': 'success', 'message': f'{category.capitalize()} file uploaded successfully'})

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

@app.route('/get-dataset-mapped', methods=['GET'])
def get_dataset_mapped():
    # Pastikan ketiga dataset sudah ada
    if not DATASET_FOLDER.exists() or not AUDIO_FOLDER.exists() or not MAPPER_FOLDER.exists():
        return jsonify({'status': 'failed', 'message': 'All datasets are not uploaded yet'}), 400

    try:
        # 1. Baca file mapper.json
        mapper_file = MAPPER_FOLDER / "mapper.json"
        if not mapper_file.exists():
            return jsonify({'status': 'failed', 'message': 'Mapper file not found'}), 404

        with open(mapper_file, 'r') as f:
            mapper = json.load(f)

        # 2. Buat daftar gambar sesuai mapper
        matched_data = []
        for entry in mapper:
            audio_file_name = entry['audio_file']
            picture_file = DATASET_FOLDER / entry['pic_name']
            if picture_file.exists():
                matched_data.append({
                    'filename': entry['audio_file'],
                    'imagePath': f"http://127.0.0.1:5000/dataset-image/{entry['pic_name']}",
                    'distance': None  # Belum ada perhitungan jarak, hanya menampilkan gambar
                })

        if not matched_data:
            return jsonify({'status': 'failed', 'message': 'No matching pictures found in the dataset'}), 404

        # 3. Return data yang sudah diproses
        return jsonify({'status': 'success', 'data': matched_data})

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
