import React, { useRef, useState, useEffect } from 'react';

const Sidebar = ({ setResults, setUploadedImage, setUploadedFile, uploadedImage, executionTime, setExecutionTime, uploadMode = "pictures" }) => {
  const fileInputRef = useRef(null);
  const [fileName, setFileName] = useState(""); // Untuk file biasa (gambar)
  //const [datasetFileNames, setDatasetFileNames] = useState([]); // Untuk zip dataset

  const [uploadedZipFiles, setUploadedZipFiles] = useState({
    audio: "",
    pictures: "",
    mapper: "",
  })

  // const [executionTime, setExecutionTime] = useState(null);

  const handleDatasetUpload = (type, category = "") => {
    if (type === "upload") {
      if (uploadMode === "pictures") {
        fileInputRef.current.accept = ".jpg,.jpeg,.png,.bmp";
        fileInputRef.current.dataset.category = "pictures"; 
      } else if (uploadMode === "audio") {
        fileInputRef.current.accept = ".midi,.mid";
        fileInputRef.current.dataset.category = "audio"; 
      }
      fileInputRef.current.dataset.type = "upload";
    } else if (type === "zip") {
      fileInputRef.current.accept =
        category === "pictures"
          ? ".jpg,.jpeg,.png,.bmp,.zip,.rar,.7z" // Pictures
          : category === "audio"
          ? ".midi,.mid,.zip,.rar,.7z" // Audio
          : ".json,.txt,.zip,.rar,.7z"; // Mapper
      fileInputRef.current.dataset.category = category; // Tandai kategori
      fileInputRef.current.dataset.type = "zip"; // Tandai untuk ZIP
    }

    fileInputRef.current.click();
  };

  const handleFileUpload = () => {
    // Pastikan input file memiliki atribut accept sesuai dengan uploadMode
    if (uploadMode === "pictures") {
      fileInputRef.current.accept = ".jpg,.jpeg,.png,.bmp";
      fileInputRef.current.dataset.category = "pictures"; 
    } else if (uploadMode === "audio") {
      fileInputRef.current.accept = ".mp3,.wav,.ogg,.flac,.midi,.mid";
      fileInputRef.current.dataset.category = "audio"; 
    }
  
    fileInputRef.current.dataset.type = "upload"; // Reset type menjadi "upload"
    fileInputRef.current.click(); // Membuka file picker
  };   

  const handleFileChange = async (event) => {
    const files = Array.from(event.target.files);
    if (!files.length) return;

    const uploadType = fileInputRef.current.dataset.type; // upload/zip
    const category = fileInputRef.current.dataset.category || ""; // pictures/audio/mapper

    // const file = files[0];
    // const fileExtension = file.name.split('.').pop().toLowerCase();

    // Logika untuk tombol Upload (preview file saja)
    if (uploadType === "upload") {
      // Ambil satu file saja
      const file = files[0];
      const fileExtension = file.name.split('.').pop().toLowerCase();
    
      if (
        (uploadMode === "pictures" && ["jpg", "jpeg", "png", "bmp"].includes(fileExtension)) ||
        (uploadMode === "audio" && ["mp3", "wav", "ogg", "flac", "midi", "mid"].includes(fileExtension))
      ) {
        setUploadedFile(file); // Simpan file untuk diproses nanti oleh tombol "Search"

        if (uploadMode === "pictures") {
          // Mode Pictures: hanya preview gambar
          setUploadedImage(URL.createObjectURL(file));
          setFileName(file.name);
        } else if (uploadMode === "audio") {
          // Mode Audio: kirim ke backend untuk mendapatkan imagePath (preview gambar dari mapper)
          const formData = new FormData();
          formData.append("file", file);

          try {
            const response = await fetch("http://127.0.0.1:5000/upload-midi", {
              method: "POST",
              body: formData,
            });

            const data = await response.json();
            if (response.ok) {
              setFileName(file.name); // Tampilkan nama file
              if (data.imagePath) {
                setUploadedImage(data.imagePath); // Preview gambar dari mapper
              } else {
                setUploadedImage(null); // Tidak ada gambar dari mapper
              }
            } else {
              alert(`Failed to upload audio: ${data.message}`);
            }
          } catch (error) {
            console.error("Error uploading audio file:", error);
            alert("Error occurred during audio upload.");
          }
        }
      } else {
          alert(`Unsupported file type for mode: ${uploadMode}`);
      }
    }
    // Logika untuk tombol Audios, Pictures, Mapper (zip upload)
    else if (uploadType === "zip") {
      // Upload ZIP dataset
      const formData = new FormData();
      files.forEach((file) => formData.append("file", file));

      fetch(`http://127.0.0.1:5000/upload-zip/${category}`, {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            alert(`${category.charAt(0).toUpperCase() + category.slice(1)} uploaded successfully!`);
            setUploadedZipFiles((prev) => ({
              ...prev,
              [category]: files.map((f) => f.name).join(", "),
            }));
            if (data.execution_time) {
              setExecutionTime(data.execution_time); // Simpan execution time
            }
          } else {
            alert(`Failed to upload file: ${data.message}`);
          }
        })
        .catch((error) => {
          console.error("Error uploading files:", error);
          alert("Error uploading files.");
        });
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

        {/* Execution Time */}
        {executionTime && (
          <div className="text-center text-white font-bold text-sm mt-2">
              Execution Time: {(executionTime * 1000).toFixed(2)} ms
          </div>
        )}

        {/* Input file (disembunyikan) */}
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileChange}
          multiple // Mendukung multiple files
        />

        {/* Tombol Upload */}
        <div className="flex justify-center items-center p-8 -mt-10">
          <button
            className="px-10 py-1.5 bg-[#BABEB8] text-[#092D3A] rounded font-bold"
            onClick={handleFileUpload}
          >
            Upload
          </button>
        </div>

        {/* Tombol untuk Dataset */}
        <div className="flex flex-col justify-center items-center space-y-2">
        {/* Tombol Audios */}
          <button
            className="px-10 py-1.5 bg-[#BABEB8] text-[#092D3A] rounded font-bold"
            onClick={() => handleDatasetUpload("zip", "audio")}
          >
            Audios
          </button>
          {/* Tombol Pictures */}
          <button
            className="px-9 py-1.5 bg-[#BABEB8] text-[#092D3A] rounded font-bold"
            onClick={() => handleDatasetUpload("zip", "pictures")}
          >
            Pictures
          </button>
          {/* Tombol Mapper */}
          <button
            className="px-9 py-1.5 bg-[#BABEB8] text-[#092D3A] rounded font-bold"
            onClick={() => handleDatasetUpload("zip", "mapper")}
            >
            Mapper
          </button>
        </div>

        {/* Daftar Files Upload */}
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
