import React, { useRef } from 'react';

const Sidebar = ({ setResults, setUploadedImage, uploadedImage }) => {
  const fileInputRef = useRef(null);

  const flaskURL = "http://127.0.0.1:5000/upload-picture";

  const handleFileUpload = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      // Set image preview di kotak putih
      const fileURL = URL.createObjectURL(file);
      setUploadedImage(fileURL); // Perbarui state uploadedImage

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch(flaskURL, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        if (response.ok) {
          console.log("Response from Flask:", data);
          alert("File uploaded successfully!");

          // Kirim hasil ke SongGrid
          if (data.status === "success") {
            console.log("Data sent to SongGrid:", data.data); // Debug
            setResults(data.data); // Perbarui state results di App.jsx
          }
        } else {
          console.error("Error:", data.message);
          alert(`Failed to upload file: ${data.message}`);
        }
      } catch (error) {
        console.error("Error connecting to Flask:", error);
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
            onClick={handleFileUpload}
          >
            Upload
          </button>
        </div>

        {/* Tombol Audios */}
        <div className="flex justify-center items-center p-2">
          <button
            className="px-4 py-2 bg-[#BABEB8] text-[#092D3A] rounded"
            onClick={handleFileUpload}
          >
            Audios
          </button>
        </div>

        {/* Tombol Pictures */}
        <div className="flex justify-center items-center p-2">
          <button
            className="px-4 py-2 bg-[#BABEB8] text-[#092D3A] rounded"
            onClick={handleFileUpload}
          >
            Pictures
          </button>
        </div>

        {/* Tombol Mapper */}
        <div className="flex justify-center items-center p-2">
          <button
            className="px-4 py-2 bg-[#BABEB8] text-[#092D3A] rounded"
            onClick={handleFileUpload}
          >
            Mapper
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
