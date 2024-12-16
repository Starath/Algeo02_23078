import React, { useRef, useState, useEffect } from 'react';

const Sidebar = ({ setResults, setUploadedImage, uploadedImage, uploadMode }) => {
  const fileInputRef = useRef(null);
  const [fileName, setFileName] = useState(""); // Untuk file biasa (gambar)
  //const [datasetFileNames, setDatasetFileNames] = useState([]); // Untuk zip dataset

  const [uploadedZipFiles, setUploadedZipFiles] = useState({
    audio: "",
    pictures: "",
    mapper: "",
  })

  const [executionTime, setExecutionTime] = useState(null);


  const handleFileUpload = (type, category = "") => {
    if (type === "upload") {
      if (uploadMode === "pictures") {
        fileInputRef.current.accept = ".jpg,.jpeg,.png,.bmp";
        fileInputRef.current.dataset.category = "pictures"; 
      } else if (uploadMode === "audio") {
        fileInputRef.current.accept = ".mp3,.wav,.ogg,.flac,.midi,.mid";
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

  const handleFileChange = async (event) => {
    const files = Array.from(event.target.files);
    if (!files.length) return;

    const uploadType = fileInputRef.current.dataset.type; // upload/zip
    const category = fileInputRef.current.dataset.category || ""; // pictures/audio/mapper

    if (!category) {
      alert("Category is not defined. Please select a valid category.");
      return;
    }

    const formData = new FormData();

    if (uploadType === "upload") {
      // Jika "upload" gambar/audio
      const file = files[0]; // Ambil satu file saja
      const fileExtension = file.name.split('.').pop().toLowerCase();

      let url = "";
      if (uploadMode === "pictures" && ["jpg", "jpeg", "png", "bmp"].includes(fileExtension)) {
        url = "http://127.0.0.1:5000/upload-picture";
      } else if (uploadMode === "audio" && ["mp3", "wav", "ogg", "flac", "midi", "mid"].includes(fileExtension)) {
        url = "http://127.0.0.1:5000/upload-midi";
      } else {
        alert(`Unsupported file type for mode: ${uploadMode}`);
        return;
      }

      formData.append("file", file);

      try {
        const response = await fetch(url, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        if (response.ok) {
          alert("File uploaded successfully!");
          setFileName(file.name); // Tampilkan nama file
          if (url.includes("upload-picture")) {
            setUploadedImage(URL.createObjectURL(file)); // Preview gambar
            setResults(data.data); // Hasil untuk gambar
          } else {
            if (data.imagePath) {
              console.log("Results received:", data.results); // Log untuk memastikan data
              setUploadedImage(data.imagePath);
            } else {
              setUploadedImage(null); // No image jika tidak ada di mapper
            }
            setResults(data.results || []);
          }

          if (data.execution_time){
            setExecutionTime(data.execution_time);
          }
        } else {
          alert(`Failed to upload file: ${data.message}`);
        }
      } catch (error) {
        console.error("Error uploading file:", error);
        alert("Error uploading file.");
      }
    } else if (uploadType === "zip"){
      // Jika "zip" file
      files.forEach((file) => formData.append("file", file));

      try {
        const response = await fetch(`http://127.0.0.1:5000/upload-zip/${category}`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        if (response.ok) {
          alert(`${category.charAt(0).toUpperCase() + category.slice(1)} uploaded successfully!`);
          setUploadedZipFiles((prev) => ({
            ...prev,
            [category]: files.map((f) => f.name).join(", "),
          }));
        } else {
          alert(`Failed to upload file: ${data.message}`);
        }
      } catch (error) {
        console.error("Error uploading files:", error);
        alert("Error uploading files.");
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

        {/* Execution Time */}
        {executionTime && (
                <div className="text-center text-white font-bold text-sm mt-2">
                    Execution Time: {executionTime.toFixed(2)*1000} ms
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
            onClick={() => handleFileUpload("upload")}
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

Sidebar.defaultProps = {
  uploadMode: "pictures", // Default mode ke "pictures"
};


export default Sidebar;
