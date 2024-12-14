from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import os
from pathlib import Path
from albumFinder import process_uploaded_image

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "dataSet" / "dataGambar"  # Folder dataset

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        temp_file_path = default_storage.save(f"temp/{uploaded_file.name}", uploaded_file)

        # Path absolut ke file sementara
        temp_file_abs_path = os.path.join(BASE_DIR, "media", temp_file_path)

        try:
            # Proses gambar yang diunggah menggunakan albumFinder.py
            sorted_distances = process_uploaded_image(temp_file_abs_path, DATASET_PATH)
        except Exception as e:
            return JsonResponse({"status": "failed", "message": str(e)})

        # Hapus file sementara setelah diproses
        os.remove(temp_file_abs_path)

        # Kirim hasil ke frontend
        return JsonResponse({
            "status": "success",
            "data": [
                {"index": index, "distance": round(distance, 4)}
                for index, distance in sorted_distances
            ],
        })

    return JsonResponse({"status": "failed", "message": "Invalid request"})