import React, { useRef } from 'react';

const Sidebar = ({ setResults, setUploadedImage, uploadedImage }) => {
  const fileInputRef = useRef(null);

  const handleFileUpload = (type, category = "") => {
    fileInputRef.current.accept = type === "zip" ? ".zip" : "image/*";
    fileInputRef.current.dataset.type = type; // Tandai tipe file (image/zip)
    fileInputRef.current.dataset.category = category; // Tandai kategori untuk ZIP
    fileInputRef.current.click();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    const uploadType = fileInputRef.current.dataset.type; // 'image' atau 'zip'
    const category = fileInputRef.current.dataset.category; // 'pictures', 'audio', 'mapper'

    if (file) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const url =
          uploadType === "zip"
            ? `http://127.0.0.1:5000/upload-zip/${category}` // Endpoint untuk ZIP
            : `http://127.0.0.1:5000/upload-picture`; // Endpoint untuk gambar biasa

        const response = await fetch(url, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        if (response.ok) {
          alert("File uploaded successfully!");
          console.log("Upload result:", data);

          // Hanya jika gambar biasa
          if (uploadType !== "zip") {
            setUploadedImage(URL.createObjectURL(file)); // Preview gambar
            setResults(data.data); // Update hasil ke SongGrid
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

  return (
    <div className='w-[25%] h-[100%] p-2 flex-col gap-2 text-white lg-flex'>
      <div className='bg-[#092D3A] h-[100%] rounded flex flex-col justify-around'>
        
        {/* Kotak Putih untuk Image Preview */}
        <div className='bg-white h-[45%] flex justify-center items-center rounded m-5'>
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

        {/* Input file (disembunyikan) */}
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />

        {/* Tombol Upload */}
        <div className="flex justify-center items-center p-8">
          <button
            className="px-4 py-2 bg-[#BABEB8] text-[#092D3A] rounded"
            onClick={() => handleFileUpload("image")}
          >
            Upload
          </button>
        </div>

        {/* Tombol Audios */}
        <div className="flex justify-center items-center p-2">
          <button
            className="px-4 py-2 bg-[#BABEB8] text-[#092D3A] rounded"
            onClick={() => handleFileUpload("zip", "audio")}
          >
            Audios
          </button>
        </div>

        {/* Tombol Pictures */}
        <div className="flex justify-center items-center p-2">
          <button
            className="px-4 py-2 bg-[#BABEB8] text-[#092D3A] rounded"
            onClick={() => handleFileUpload("zip", "pictures")}
          >
            Pictures
          </button>
        </div>

        {/* Tombol Mapper */}
        <div className="flex justify-center items-center p-2">
          <button
            className="px-4 py-2 bg-[#BABEB8] text-[#092D3A] rounded"
            onClick={() => handleFileUpload("zip", "mapper")}
          >
            Mapper
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
