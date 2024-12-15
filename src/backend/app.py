from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from albumFinder import process_uploaded_image
from pathlib import Path
import mimetypes
import shutil  # Untuk menghapus folder
from zipfile import ZipFile  # Untuk ekstraksi zip

app = Flask(__name__)
CORS(app)  # Tambahkan ini untuk mengizinkan semua origin
BASE_DIR = Path(__file__).resolve().parent

# Folder untuk menyimpan file upload sementara
DATASET_FOLDER = Path(__file__).resolve().parent / "dataset" / "dataGambar"
UPLOAD_FOLDER = Path(__file__).resolve().parent / "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask API!', 'routes': ['/upload-picture']})

@app.route('/upload-picture', methods=['POST'])
def upload_picture():
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'failed', 'message': 'No selected file'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'failed', 'message': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = UPLOAD_FOLDER / filename
        file.save(file_path)  # Simpan file sementara

        try:
            # Proses file menggunakan albumFinder
            result, valid_files = process_uploaded_image(str(file_path), str(DATASET_FOLDER))
            sorted_result = [
                {
                    'filename': valid_files[idx].name,  # Pastikan index sesuai valid_files
                    'distance': distance,
                    'imagePath': f"http://127.0.0.1:5000/dataset-image/{valid_files[idx].name}"
                }
                for idx, distance in result
            ]


            return jsonify({'status': 'success', 'data': sorted_result})

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

# Route untuk upload ZIP (pictures, audio, mapper)
@app.route('/upload-zip/<category>', methods=['POST'])
def upload_zip(category):
    if 'file' not in request.files:
        return jsonify({'status': 'failed', 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.zip'):
        return jsonify({'status': 'failed', 'message': 'Invalid file or not a zip file'}), 400

    # Tentukan folder tujuan berdasarkan kategori
    if category == "pictures":
        target_folder = DATASET_FOLDER
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    elif category == "audio":
        target_folder = BASE_DIR / "dataset" / "dataAudio"
        allowed_extensions = {'.midi', '.mid'}
    elif category == "mapper":
        target_folder = BASE_DIR / "dataset" / "dataMapper"
        allowed_extensions = None  # Allow all for mapper
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

        return jsonify({'status': 'success', 'message': f'{category.capitalize()} zip uploaded and extracted successfully'})

    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
