import React, { useRef, useState, useEffect } from 'react';

const Sidebar = ({ setResults, setUploadedImage, uploadedImage }) => {
  const fileInputRef = useRef(null);
  const [fileName, setFileName] = useState(""); // Untuk file biasa (gambar)
  //const [datasetFileNames, setDatasetFileNames] = useState([]); // Untuk zip dataset

  const [uploadedZipFiles, setUploadedZipFiles] = useState({
    audio: "",
    pictures: "",
    mapper: "",
  })

  const handleFileUpload = (type, category = "") => {
    // Set accept file sesuai jenis file (image atau ZIP/MIDI)
    fileInputRef.current.accept =
      type === "zip" ? ".zip" : "image/*, .mid"; // Mendukung gambar & MIDI
    fileInputRef.current.dataset.type = type; // Tandai tipe file (image/zip)
    fileInputRef.current.dataset.category = category; // Tandai kategori untuk ZIP
    fileInputRef.current.click();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    const uploadType = fileInputRef.current.dataset.type; // 'image', 'zip'
    const category = fileInputRef.current.dataset.category; // 'pictures', 'audio', 'mapper'

    if (file) {
      const formData = new FormData();
      formData.append("file", file);

      // Tentukan endpoint berdasarkan jenis file
      const fileExtension = file.name.split('.').pop().toLowerCase();
      let url = "";

      if (fileExtension === "mid") {
        url = "http://127.0.0.1:5000/upload-midi"; // Endpoint MIDI
      } else if (["jpg", "jpeg", "png", "bmp"].includes(fileExtension)) {
        url = "http://127.0.0.1:5000/upload-picture"; // Endpoint gambar
      } else if (uploadType === "zip") {
        url = `http://127.0.0.1:5000/upload-zip/${category}`; // Endpoint ZIP
      } else {
        alert("Unsupported file type. Please upload an image, MIDI, or ZIP file.");
        return;
      }

      try {
        const response = await fetch(url, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        if (response.ok) {
          alert("File uploaded successfully!");

          // Update hasil berdasarkan jenis file
          if (fileExtension === "mid") {
            setResults(data.results); // Hasil dari MusicFinder (MIDI)
            setFileName(file.name); // Set nama file MIDI
          } else if (["jpg", "jpeg", "png", "bmp"].includes(fileExtension)) {
            setUploadedImage(URL.createObjectURL(file)); // Preview gambar
            setResults(data.data); // Hasil dari albumFinder (PCA)
            setFileName(file.name); // Set nama file gambar
          } else if (uploadType === "zip") {
            //setResults(data.data); 
            setUploadedZipFiles((prev) => ({
              ...prev,
              [category]: file.name, // Tambahkan file ZIP ke kategori
            }));
            //setResults(data.data); // Hasil ZIP
          }
        } else {
          alert(`Failed to upload file: ${data.message}`);
        }
      } catch (error) {
        console.error("Error uploading file:", error);
        alert(`Failed to upload file: ${error.message}`);
      }
    }
  };

  const fetchMappedDataset = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get-dataset-mapped');
      const data = await response.json();
      if (response.ok) {
        setResults(data.data); // Perbarui SongGrid dengan hasil mapper
      } else {
        alert(`Failed to load dataset: ${data.message}`);
      }
    } catch (error) {
      console.error("Error fetching mapped dataset:", error);
      alert("Failed to fetch dataset.");
    }
  };
  
  useEffect(() => {
    // Jika ketiga ZIP sudah diunggah, panggil fetchMappedDataset sekali
    if (uploadedZipFiles.audio && uploadedZipFiles.pictures && uploadedZipFiles.mapper) {
      fetchMappedDataset();
    }
  }, [uploadedZipFiles]); // Jalankan ketika uploadedZipFiles berubah  
  
  return (
    <div className="w-[25%] h-[100%] p-2 flex-col gap-2 text-white lg-flex">
      <div className="bg-[#092D3A] h-[100%] rounded flex flex-col justify-around">
        
        {/* Kotak Preview Gambar*/}
        <div className="bg-white h-[25%] flex justify-center items-center rounded m-3">
          {uploadedImage ? (
            <img
              src={uploadedImage}
              alt="Uploaded Preview"
              className="max-h-full max-w-full object-contain"
            />
          ) : (
            <span className="text-gray-500">No Image</span>
          )}
        </div>
          
        {/* Tampilkan Nama File (Gambar/MIDI) */}
        {fileName && (
          <div className="text-center text-white font-bold text-sm -mt-8">{fileName}</div>
        )}

        {/* Input file (disembunyikan) */}
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />

        {/* Tombol Upload */}
        <div className="flex justify-center items-center p-8 -mt-10">
          <button
            className="px-10 py-1.5 bg-[#BABEB8] text-[#092D3A] rounded font-bold"
            onClick={() => handleFileUpload("image")}
          >
            Upload
          </button>
        </div>

        {/* Tombol untuk Dataset */}
        <div className="flex flex-col justify-center items-center space-y-2">
        {/* Tombol Audios */}
          <button
            className="px-10 py-1.5 bg-[#BABEB8] text-[#092D3A] rounded font-bold"
            onClick={() => handleFileUpload("zip", "audio")}
          >
            Audios
          </button>
          {/* Tombol Pictures */}
          <button
            className="px-9 py-1.5 bg-[#BABEB8] text-[#092D3A] rounded font-bold"
            onClick={() => handleFileUpload("zip", "pictures")}
          >
            Pictures
          </button>
          {/* Tombol Mapper */}
          <button
            className="px-9 py-1.5 bg-[#BABEB8] text-[#092D3A] rounded font-bold"
            onClick={() => handleFileUpload("zip", "mapper")}
            >
            Mapper
          </button>
        </div>

        {/* Tulisan dataset yang diunggah */}
        <div className="flex flex-col justify-center items-center p-2 space-y-1 -mt-5">
          {uploadedZipFiles.audio && (
            <p className="text-center text-sm text-white font-bold mt-1">
              Audios: {uploadedZipFiles.audio}
            </p>
          )}
          {uploadedZipFiles.pictures && (
            <p className="text-center text-sm text-white font-bold mt-1">
              Pictures: {uploadedZipFiles.pictures}
            </p>
          )}
          {uploadedZipFiles.mapper && (
            <p className="text-center text-sm text-white font-bold mt-1">
              Mapper: {uploadedZipFiles.mapper}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
