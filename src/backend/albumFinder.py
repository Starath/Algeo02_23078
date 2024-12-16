from pathlib import Path
import numpy as np
from PIL import Image, UnidentifiedImageError
import time
import json
import os



BASE_DIR = Path(__file__).resolve().parent  # path root 'backend'
datasetPath = BASE_DIR / "dataSet" / "dataGambar"


def preProcessing(input_path):
    img = Image.open(input_path)
    imgArray = np.array(img)

    #ekstrak channel RGB
    R, G, B = imgArray[:, :, 0], imgArray[:, :, 1], imgArray[:, :, 2]

    gray_array = 0.2989 * R + 0.5870 * G + 0.1140 * B

    gray_array = gray_array.astype(np.uint8)

    # simpan gambar grayscale
    gray_img = Image.fromarray(gray_array)

    #resize
    resized_img = gray_img.resize((10, 10), Image.Resampling.LANCZOS)
    
    return np.array(resized_img)

def flattenImg1D(imgArray):
    img1D = np.array([value for row in imgArray for value in row])
        
    return img1D

def standardizeImg(imgArray):
    imgArray = np.array(imgArray)
    
    # hitung rata-rata untuk setiap piksel 
    meanValue = np.mean(imgArray, axis=0)  
    
    # standarisasi gambar
    standardizedImg = imgArray - meanValue  

    return standardizedImg


def transpose(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    transposed = [[matrix[j][i] for j in range(rows)] for i in range(cols)]
    return transposed

def covarianceMatrix(matrix):
    N = len(matrix)  # jumlah gambar
    features = len(matrix[0])  # jumlah fitur
    
    # matriks kovarians kosong dengan dimensi (jumlah fitur x jumlah fitur)
    C = [[0 for i in range(features)] for j in range(features)]
    
    # menghitung matriks kovarians
    tMatrix = transpose(matrix)
    for i in range(N):
        for j in range(features):
            for k in range(features):
                C[j][k] += matrix[i][j] * tMatrix[j][i]
    
    # membagi dengan N untuk mendapatkan rata-rata
    for j in range(features):
        for k in range(features):
            C[j][k] /= N
    return C

def svdDecompotition(matrix):
    C = covarianceMatrix(matrix)

    U, S, UT = np.linalg.svd(C)

    # matriks U adalah eigenvektor

    return U


def projectionPCADataset(matrix, U, k):
    # ambil k-komponen utama
    U_k = [U[i][:k] for i in range(len(U))]

    # inisialisasi hasil proyeksi 
    N = len(matrix)
    Z = [[0 for _ in range(k)] for _ in range(N)]

    # proyeksikan data
    for i in range(N):  
        for j in range(k):  
            for m in range(len(U_k)):  
                Z[i][j] += matrix[i][m] * U_k[m][j]

    return Z


def projectionPCAQuery(queryPath, U, k, meanValue):
    # pre-processing gambar query
    grayscaleImg = preProcessing(queryPath)

    # flatten gambar menjadi vektor 1D
    flattenImg = flattenImg1D(grayscaleImg)

    # standarisasi gambar query menggunakan rata-rata dataset
    standardizedImg = standardizeImg(flattenImg)

    U_k = U[:, :k]  # ambil k komponen utama
    q = np.dot(standardizedImg, U_k)  # proyeksi ke ruang PCA
    
    return q

def euclidieanDistance(queryProjection, datasetProjection):
    
    distances = []
    
    for i, zi in enumerate(datasetProjection):
        # Hitung jarak Euclidean antara q dan zi
        distance = np.sqrt(np.sum((queryProjection - zi) ** 2))
        distances.append((i, distance))
    
    # Urutkan berdasarkan jarak terkecil
    distances.sort(key=lambda x: x[1])
    
    return distances


#########################################################################################
file_list = sorted(datasetPath.glob("*"))
processedImg = []

# membaca semua file gambar dalam folder
for imgPath in datasetPath.glob("*"):
    if imgPath.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
        # konversi gambar ke grayscale dan resize
        grayscaleImg = preProcessing(imgPath)
        
        # flatten gambar menjadi vektor 1D
        flattenImg = flattenImg1D(grayscaleImg)

        standardImg = standardizeImg(flattenImg)
        
        # tambahkan gambar yang telah diproses ke list
        processedImg.append(standardImg)
        


def process_uploaded_image(file_path, dataset_path, cache_file="dataset_cache.json"):
    startTime = time.time()
    
    datasetPath = Path(dataset_path)
    processedImg = []
    valid_files = []

    if Path(cache_file).exists():
        with open(cache_file, "r") as f:
            cache = json.load(f)
        
        cached_files = set(cache.get("validFiles", []))
        current_files = {str(p) for p in datasetPath.glob("*") if p.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']}

        if current_files != cached_files:
            print("Dataset has changed. Invalidating cache...")
            os.remove(cache_file)

    # jika belum ada, maka buat baru
    if not Path(cache_file).exists():
        print("Processing new dataset and updating cache...")
        for imgPath in datasetPath.glob("*"):
            try:
                if imgPath.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                    img = Image.open(imgPath)
                    img.verify()  
                    grayscaleImg = preProcessing(imgPath)
                    flattenImg = flattenImg1D(grayscaleImg)
                    standardImg = standardizeImg(flattenImg)
                    processedImg.append(standardImg)
                    valid_files.append(str(imgPath))  
            except UnidentifiedImageError:
                print(f"Skipping invalid image: {imgPath}")
            except Exception as e:
                print(f"Error processing file {imgPath}: {e}")

        if not processedImg:
            raise ValueError("No valid images found in the dataset!")

        # hitung PCA component
        meanValue = np.mean(processedImg, axis=0)
        U = svdDecompotition(processedImg)
        datasetProjection = projectionPCADataset(processedImg, U, 10)

        cache = {
            "meanValue": meanValue.tolist(),
            "U": U.tolist(),
            "datasetProjection": datasetProjection,
            "validFiles": valid_files,  
        }
        with open(cache_file, "w") as f:
            json.dump(cache, f)
    else:
        # load from cache
        print("Loading dataset from cache...")
        with open(cache_file, "r") as f:
            cache = json.load(f)
        meanValue = np.array(cache["meanValue"])
        U = np.array(cache["U"])
        datasetProjection = np.array(cache["datasetProjection"])
        valid_files = cache["validFiles"]

    # proses query
    queryProjection = projectionPCAQuery(file_path, U, 10, meanValue)

    # distance
    sorted_distances = euclidieanDistance(queryProjection, datasetProjection)

    # sorting 
    filtered_distances = [(i, distance) for i, distance in sorted_distances if distance < 250 and i < len(valid_files)]

    endTime = time.time()
    executionTime = endTime - startTime

    return filtered_distances, valid_files, executionTime

