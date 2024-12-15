from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from albumFinder import process_uploaded_image
from pathlib import Path
import mimetypes

app = Flask(__name__)
CORS(app)  # Tambahkan ini untuk mengizinkan semua origin

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

    if file:
        filename = secure_filename(file.filename)
        file_path = UPLOAD_FOLDER / filename
        file.save(file_path)  # Simpan file sementara

        try:
            # Proses file menggunakan albumFinder
            result = process_uploaded_image(str(file_path), str(DATASET_FOLDER))
            files_in_dataset = list(DATASET_FOLDER.glob("*.jpg"))
            sorted_result = [
                {
                    'filename': files_in_dataset[idx].name,
                    'distance': distance,
                    'imagePath': f"http://127.0.0.1:5000/dataset-image/{files_in_dataset[idx].name}"
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


if __name__ == '__main__':
    app.run(debug=True)
