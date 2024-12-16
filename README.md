# **Algeo02-23078**
By Kelompok 18 Ada Ada Aja
Website untuk mencari album/lagu
<br>

## Contributors
<div align="center">

| **NIM**  | **Nama** |
| ------------- |:-------------:|
| 13523078   | Anella Utari Gunadi |
| 13523080   | Diyah Susan Nugrahani |
| 13523106   | Athian Nugraha Muarajuang |

</div>

## Apa itu Audio Searcher?

Proyek Audio Searcher ini adalah sebuah web application yang dibangun 
untuk mencari dan memproses file audio MIDI serta gambar, 
dengan tujuan untuk melakukan pencocokan data 
berdasarkan fitur yang diekstrak dari file-file tersebut. 

## Teknologi yang Digunakan
- React
- Flask     

## Bagaimana Cara Menjalankan Web-nya?
1. Pastikan npm dan python sudah terinstall. Install node dari https://nodejs.org/en. Install python dari https://www.python.org/downloads/
2. Install dependencies dengan menggunakan terminal. Jalankan command-command berikut
```sh
git clone https://github.com/Starath/Algeo02_23078.git
cd src\frontend\audioSearcher\src
npm install
cd ..\..\..\..
pip install virtualenv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
3. Jalankan backend web menggunakan terminal dengan command
``` sh
cd src\backend
python app.py
cd ..\..
```

4. jalankan frontend web menggunakan terminal yang berbeda saat jalankan backend dengan command
``` sh
cd src\frontend\audioSearcher\src
npm run dev
```

5. Buka link localnya

## Bagaimana cara menggunakannya

1. Berikut laman saat pertama kali user masuki web
![Imgur](https://imgur.com/XT6Nllr.jpg)
2. Tekan tombol 'Audios' dan masukkan dataset audio berupa zip berisi file midi 
![Imgur](https://imgur.com/SsHmIFd.jpg)
![Imgur](https://imgur.com/v5pk3Rv.jpg)
3. Tekan tombol 'Pictures' dan masukkan dataset gambar berupa zip berisi file jpg, jpeg, bmp, png
![Imgur](https://imgur.com/NAub8He.jpg)
4. Tekan tombol 'Mapper' dan masukkan mapper berupa json yang sudah mengelompokkan file file audio dengan gambarnya
![Imgur](https://imgur.com/cQ3cKih.jpg)
![Imgur](https://imgur.com/b1mYpyr.jpg)
5. Pilih mode album (untuk query gambar) atau music (untuk query musik)

6. Tekan tombol 'Upload' dan masukkan file yang mau dicari kemiripannya dengan dataset yang sudah dimasuki
![Imgur](https://imgur.com/VQCZDBC.jpg)
![Imgur](https://imgur.com/l8dI3uv.jpg)
7. Tekan tombol search untuk mulai melakukan perbandingan query dengan dataset
![Imgur](https://imgur.com/Qajljup.jpg)

