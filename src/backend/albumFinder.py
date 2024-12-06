from pathlib import Path
import numpy as np
from PIL import Image


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
datasetPath = Path("src/backend/dataset/dataGambar")
# menyimpan hasil gambar yang telah diproses
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
        
meanValue = np.mean(processedImg, axis=0)
U = svdDecompotition(processedImg)
#hasil dari dataset
datasetProjection = projectionPCADataset(processedImg, U, 10)

#hasil dari query
queryPath = Path('src/backend/dataset/dataGambar/query.jpg')
queryProjection = projectionPCAQuery(queryPath, U, 10, meanValue)

#menghitung jarak euclidiean
sorted_distances = euclidieanDistance(queryProjection, datasetProjection)

########################################################################
# cetak hasil (masih debugging)
print("Hasil jarak dan urutan berdasarkan jarak terkecil:")
for index, distance in sorted_distances:
    print(f"Gambar ke-{index} memiliki jarak {distance:.4f}")




