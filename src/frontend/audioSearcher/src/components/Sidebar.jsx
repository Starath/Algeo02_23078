import React, { useRef } from 'react';

const Sidebar = () => {
  const fileInputRef = useRef(null);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) {
      alert("Pilih file terlebih dahulu!");
      return;
    }

    // Kirim file ke backend
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.status === "success") {
        console.log("Hasil:", data.data);
        alert(JSON.stringify(data.data, null, 2)); // Tampilkan hasil
      } else {
        alert(`Error: ${data.message}`);
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Terjadi kesalahan saat mengunggah file.");
    }
  };

  const handleFileUpload = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="w-[25%] h-[100%] p-2 flex-col gap-2 text-white lg-flex">
      <div className="bg-[#092D3A] h-[100%] rounded flex flex-col justify-around">
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <div className="flex justify-center items-center p-8">
          <button
            className="px-4 py-2 bg-[#BABEB8] text-[#092D3A] rounded"
            onClick={handleFileUpload}
          >
            Upload Pictures
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
