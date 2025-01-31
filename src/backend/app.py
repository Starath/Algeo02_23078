import json
import os
import tempfile
from flask import Flask, request, jsonify, send_file
import patoolib
from flask_cors import CORS, cross_origin
import py7zr
from albumFinder import process_uploaded_image
from MusicFinder import compare_query_to_database
from DatabaseProcess import build_feature_database  
from pathlib import Path
import mimetypes
import shutil
from zipfile import ZipFile
import rarfile
import time
import uuid

app = Flask(__name__)
CORS(app)

# Path Konfigurasi
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
DATASET_FOLDER = BASE_DIR / "dataset" / "dataGambar"
AUDIO_FOLDER = BASE_DIR / "dataset" / "dataAudio"
MAPPER_FOLDER = BASE_DIR / "dataset" / "dataMapper"
MIDI_DATABASE_FILE = "midi_feature_database.json"
THRESHOLD = 0.55  # threshold similarity untuk file MIDI

ALLOWED_ARCHIVES = {".zip", ".rar", ".tar", ".7z"}  # format yang diperbolehkan
rarfile.UNRAR_TOOL = r"C:\Users\diyah\Downloads\unrar.exe"


UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask API!', 'routes': ['/upload-picture', '/upload-midi', '/upload-zip/<category>']})

# upload file gambar
@app.route('/upload-picture', methods=['POST'])
def upload_picture():    
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'failed', 'message': 'No selected file'}), 400

    file_path = UPLOAD_FOLDER / (file.filename)
    file.save(file_path)

    try:
        # proses file menggunakan albumFinder.py
        result, valid_files, time = process_uploaded_image(str(file_path), str(DATASET_FOLDER))
        
        # load JSON and TXT files in the mapper folder
        mapper_files = list(MAPPER_FOLDER.glob("*.json")) + list(MAPPER_FOLDER.glob("*.txt"))

        if not mapper_files:
            return jsonify({'status': 'failed', 'message': 'No valid mapper files (JSON/TXT) found'}), 404

        mapper = []
        for file in mapper_files:
            try:
                with open(file, 'r') as f:
                    if file.suffix == '.json':
                        data = json.load(f)  
                    else:
                        data = f.read()  
                        try:
                            data = json.loads(data)  
                        except json.JSONDecodeError:
                            print(f"Skipping non-JSON TXT file: {file.name}")
                            continue  

                    
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
            image_path = Path(valid_files[idx])  # pastikan path
            image_name = image_path.name  # ambil nama file
            audio_name = None
            
            for entry in mapper:
                if entry['pic_name'] == image_name:
                    audio_name = entry['audio_file']
                    break
            
            mapped_results.append({
                'filename': audio_name if audio_name else image_name,  
                'distance': distance,
                'imagePath': f"http://127.0.0.1:5000/dataset-image/{image_name}"
            })

        return jsonify({'status': 'success', 'data': mapped_results, 'execution_time': time})

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

# upload file MIDI
@app.route('/upload-midi', methods=['POST'])
def upload_midi():
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': 'No file part'}), 400

    file = request.files['file']
    if not file.filename.endswith('.mid'):
        return jsonify({'status': 'failed', 'message': 'Invalid MIDI file'}), 400

    # save the uploaded MIDI file
    file_path = UPLOAD_FOLDER / (file.filename)
    file.save(file_path)

    try:
        # proses file MIDI menggunakan MusicFinder.py
        results, time= compare_query_to_database(str(file_path), MIDI_DATABASE_FILE, threshold=THRESHOLD)

        mapper_files = list(MAPPER_FOLDER.glob("*.json")) + list(MAPPER_FOLDER.glob("*.txt"))

        if not mapper_files:
            return jsonify({'status': 'failed', 'message': 'No valid mapper files (JSON/TXT) found'}), 404

        mapper = []
        for mapper_file in mapper_files:
            try:
                with open(mapper_file, 'r') as f:
                    if mapper_file.suffix == '.json':
                        data = json.load(f)  # load JSON file
                    else:
                        raw_content = f.read()
                        try:
                            data = json.loads(raw_content)  
                        except json.JSONDecodeError:
                            print(f"Skipping invalid TXT file: {mapper_file.name}")
                            continue 
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

        # Map Audio Results to Pictures
        matched_results = []
        matched_image_path = None

        for entry in mapper:
            if entry['audio_file'] == file.filename and not matched_image_path:
                matched_image_path = f"http://127.0.0.1:5000/dataset-image/{entry['pic_name']}"

            for result in results:
                if entry['audio_file'] == result.get('filename'):
                    distance = float(result.get('similarity')) * 100
                    matched_results.append({
                        'filename': entry['audio_file'],
                        'distance': distance,
                        'imagePath': f"http://127.0.0.1:5000/dataset-image/{entry['pic_name']}"
                    })

        # sorting 
        matched_results = sorted(matched_results, key=lambda x: x['distance'], reverse=True)

        response_data = {
            'status': 'success',
            'imagePath': matched_image_path,  # path gambar jika ditemukan
            'results': matched_results,
            'execution_time': time,
            'message': 'MIDI file processed successfully'
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

    finally:
        file_path.unlink(missing_ok=True)

@app.route('/upload-zip/<category>', methods=['POST'])
def upload_zip(category):
    start_time = time.time()
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': 'No file part'}), 400

    files = request.files.getlist('file')  
    if not files:
        return jsonify({'status': 'failed', 'message': 'No files uploaded'}), 400

    if category == "pictures":
        target_folder = DATASET_FOLDER
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    elif category == "audio":
        target_folder = AUDIO_FOLDER
        allowed_extensions = {'.midi', '.mid'}
    elif category == "mapper":
        target_folder = MAPPER_FOLDER
        allowed_extensions = {'.json', '.txt'}
    else:
        return jsonify({'status': 'failed', 'message': 'Invalid category'}), 400

    try:
        if target_folder.exists():
            shutil.rmtree(target_folder)
        target_folder.mkdir(parents=True, exist_ok=True)

        for uploaded_file in files:
            file_extension = Path(uploaded_file.filename).suffix.lower()
            if file_extension not in allowed_extensions and file_extension not in {'.zip', '.rar'}:
                return jsonify({'status': 'failed', 'message': f'Unsupported file type: {file_extension}'}), 400

            file_path = UPLOAD_FOLDER / (uploaded_file.filename)
            uploaded_file.save(file_path)

            if file_extension == '.zip':
                with ZipFile(file_path, 'r') as zip_ref:
                    for file_name in zip_ref.namelist():
                        if Path(file_name).suffix.lower() in allowed_extensions:
                            zip_ref.extract(file_name, target_folder)

            elif file_extension == '.rar':
                with rarfile.RarFile(file_path) as rar_ref:
                    for file_name in rar_ref.namelist():
                        if Path(file_name).suffix.lower() in allowed_extensions and not file_name.endswith('/'):
                            with rar_ref.open(file_name) as source_file:
                                target_file_path = target_folder / Path(file_name).name  # Flatten to root
                                with open(target_file_path, 'wb') as dest_file:
                                    shutil.copyfileobj(source_file, dest_file)
                            print(f"Extracted: {file_name} to {target_file_path}")

            elif file_extension == '.7z':
                with py7zr.SevenZipFile(file_path, mode='r') as archive:
                    for file_name in archive.getnames():
                        if Path(file_name).suffix.lower() in allowed_extensions and not file_name.endswith('/'):
                            extracted_files = archive.read([file_name])  
                            target_file_path = target_folder / Path(file_name).name  
                            with open(target_file_path, 'wb') as dest_file:
                                dest_file.write(extracted_files[file_name].read())
                            print(f"Extracted: {file_name} to {target_file_path}")

            else:
                shutil.move(str(file_path), str(target_folder / (uploaded_file.filename)))

        if category == "audio":
            build_feature_database(str(target_folder), MIDI_DATABASE_FILE)
        
        execution_time = time.time() - start_time  # calculate execution time
        return jsonify({
            'status': 'success',
            'message': f'{category.capitalize()} files uploaded successfully, previous data replaced.',
            'execution_time': execution_time
        })

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

@app.route('/dataset-image/<filename>')
@cross_origin() 
def dataset_image(filename):
    file_path = DATASET_FOLDER / filename
    print(f"Looking for file at: {file_path}")  
    if file_path.exists():
        mime_type, _ = mimetypes.guess_type(str(file_path))
        print(f"Detected MIME type: {mime_type}") 

        if mime_type:
            return send_file(file_path, mimetype=mime_type)
        else:
            return send_file(file_path)
    else:
        # jika file tidak ditemukan
        error_message = f"File {filename} not found at {file_path}"
        print(error_message)  
        return jsonify({"error": error_message}), 404

@app.route('/get-dataset-mapped', methods=['GET'])
def get_dataset_mapped():
    # pastikan ketiga dataset sudah ada
    if not DATASET_FOLDER.exists() or not AUDIO_FOLDER.exists() or not MAPPER_FOLDER.exists():
        return jsonify({'status': 'failed', 'message': 'All datasets are not uploaded yet'}), 400

    try:
        # baca file mapper
        mapper_files = list(MAPPER_FOLDER.glob("*.json")) + list(MAPPER_FOLDER.glob("*.txt"))
        if not mapper_files:
            return jsonify({'status': 'failed', 'message': 'Mapper file not found'}), 404

        latest_mapper_file = mapper_files[0]
        
        with open(latest_mapper_file, 'r') as f:
            mapper = json.load(f) if latest_mapper_file.suffix == '.json' else f.read()

        # daftar gambar sesuai mapper
        matched_data = []
        for entry in mapper:
            audio_file_name = entry['audio_file']
            picture_file = DATASET_FOLDER / entry['pic_name']
            if picture_file.exists():
                matched_data.append({
                    'filename': entry['audio_file'],
                    'imagePath': f"http://127.0.0.1:5000/dataset-image/{entry['pic_name']}",
                    'distance': None  
                })

        if not matched_data:
            return jsonify({'status': 'failed', 'message': 'No matching pictures found in the dataset'}), 404

        return jsonify({'status': 'success', 'data': matched_data})

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
