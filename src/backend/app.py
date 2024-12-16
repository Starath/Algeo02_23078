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
        result, valid_files, time = process_uploaded_image(str(file_path), str(DATASET_FOLDER))
        
        # Step 2: Load all JSON and TXT files in the mapper folder
        mapper_files = list(MAPPER_FOLDER.glob("*.json")) + list(MAPPER_FOLDER.glob("*.txt"))

        if not mapper_files:
            return jsonify({'status': 'failed', 'message': 'No valid mapper files (JSON/TXT) found'}), 404

        # Load and combine all valid mapper files
        mapper = []
        for file in mapper_files:
            try:
                with open(file, 'r') as f:
                    if file.suffix == '.json':
                        data = json.load(f)  # Parse JSON file
                    else:
                        data = f.read()  # For TXT file (read as plain text)
                        # Optionally, convert TXT content to JSON if applicable
                        try:
                            data = json.loads(data)  # Attempt to parse TXT as JSON
                        except json.JSONDecodeError:
                            print(f"Skipping non-JSON TXT file: {file.name}")
                            continue  # Skip invalid TXT files that are not JSON-like

                    # Ensure the data is a list (or append if single dict)
                    if isinstance(data, list):
                        mapper.extend(data)
                    elif isinstance(data, dict):
                        mapper.append(data)
                    else:
                        print(f"Invalid data format in file: {file.name}")
            except Exception as e:
                print(f"Error loading file {file.name}: {e}")

        if not mapper:
            return jsonify({'status': 'failed', 'message': 'No valid mapper data found in files'}), 400


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

    # Save the uploaded MIDI file
    file_path = UPLOAD_FOLDER / secure_filename(file.filename)
    file.save(file_path)

    try:
        # Step 1: Proses file MIDI menggunakan MusicFinder.py
        results = compare_query_to_database(str(file_path), MIDI_DATABASE_FILE, threshold=THRESHOLD)

        # Step 2: Load all JSON and TXT files in the mapper folder
        mapper_files = list(MAPPER_FOLDER.glob("*.json")) + list(MAPPER_FOLDER.glob("*.txt"))

        if not mapper_files:
            return jsonify({'status': 'failed', 'message': 'No valid mapper files (JSON/TXT) found'}), 404

        # Combine data from all valid mapper files
        mapper = []
        for mapper_file in mapper_files:
            try:
                with open(mapper_file, 'r') as f:
                    if mapper_file.suffix == '.json':
                        data = json.load(f)  # Load JSON file
                    else:
                        # Attempt to parse TXT content as JSON
                        raw_content = f.read()
                        try:
                            data = json.loads(raw_content)  # Try parsing TXT as JSON
                        except json.JSONDecodeError:
                            print(f"Skipping invalid TXT file: {mapper_file.name}")
                            continue  # Skip files that are not valid JSON

                    # Ensure data is a list or a single dictionary
                    if isinstance(data, list):
                        mapper.extend(data)
                    elif isinstance(data, dict):
                        mapper.append(data)
                    else:
                        print(f"Invalid format in file: {mapper_file.name}")
            except Exception as e:
                print(f"Error reading file {mapper_file.name}: {e}")

        if not mapper:
            return jsonify({'status': 'failed', 'message': 'No valid mapper data found in files'}), 400

        # Step 3: Map Audio Results to Pictures
        matched_results = []
        matched_image_path = None

        # Iterate through the mapper data and match results
        for entry in mapper:
            # If the uploaded audio matches a mapper entry, set the image path
            if entry['audio_file'] == file.filename and not matched_image_path:
                matched_image_path = f"http://127.0.0.1:5000/dataset-image/{entry['pic_name']}"

            # Match query results (from MusicFinder) with mapper data
            for result in results:
                if entry['audio_file'] == result.get('filename'):
                    distance = float(result.get('similarity')) * 100
                    matched_results.append({
                        'filename': entry['audio_file'],
                        'distance': distance,
                        'imagePath': f"http://127.0.0.1:5000/dataset-image/{entry['pic_name']}"
                    })

        # Sort the matched results based on distance
        matched_results = sorted(matched_results, key=lambda x: x['distance'], reverse=True)

        # Prepare the response data
        response_data = {
            'status': 'success',
            'imagePath': matched_image_path,  # Path gambar jika ditemukan
            'results': matched_results,
            'message': 'MIDI file processed successfully'
        }

        return jsonify(response_data)

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

    # Define the target folder based on category
    if category == "pictures":
        target_folder = DATASET_FOLDER
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.zip'}
    elif category == "audio":
        target_folder = AUDIO_FOLDER
        allowed_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.midi', '.mid', '.zip'}
    elif category == "mapper":
        target_folder = MAPPER_FOLDER
        allowed_extensions = {'.json', '.txt', '.zip'}
    else:
        return jsonify({'status': 'failed', 'message': 'Invalid category'}), 400

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        return jsonify({'status': 'failed', 'message': f'Unsupported file type: {file_extension}'}), 400

    file_path = UPLOAD_FOLDER / secure_filename(file.filename)
    file.save(file_path)

    try:
        # **Step 1: Clean up the target folder**
        if target_folder.exists():
            shutil.rmtree(target_folder)  # Delete the target folder and its contents
        target_folder.mkdir(parents=True, exist_ok=True)  # Recreate an empty folder

        # **Step 2: Process the ZIP file**
        if file_extension == '.zip':
            # Extract files from ZIP archive
            with ZipFile(file_path, 'r') as zip_ref:
                valid_files = [
                    f for f in zip_ref.namelist()
                    if Path(f).suffix.lower() in allowed_extensions
                ]

                if not valid_files:
                    return jsonify({
                        'status': 'failed',
                        'message': f'No valid files for {category} found in the ZIP archive'
                    }), 400

                # Extract only valid files into the cleaned folder
                for valid_file in valid_files:
                    zip_ref.extract(valid_file, target_folder)

            return jsonify({
                'status': 'success',
                'message': f'{category.capitalize()} ZIP uploaded and extracted successfully, previous data replaced.'
            })
        else:
            # Save single files directly to the cleaned folder
            file.save(target_folder / secure_filename(file.filename))
            return jsonify({
                'status': 'success',
                'message': f'{category.capitalize()} file uploaded successfully, previous data replaced.'
            })

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

    finally:
        # Clean up the uploaded ZIP file
        file_path.unlink(missing_ok=True)


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
        # 1. Baca file mapper
        mapper_files = list(MAPPER_FOLDER.glob("*.json")) + list(MAPPER_FOLDER.glob("*.txt"))
        if not mapper_files:
            return jsonify({'status': 'failed', 'message': 'Mapper file not found'}), 404

        latest_mapper_file = mapper_files[0]
        
        # Baca konten file mapper
        with open(latest_mapper_file, 'r') as f:
            mapper = json.load(f) if latest_mapper_file.suffix == '.json' else f.read()

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
