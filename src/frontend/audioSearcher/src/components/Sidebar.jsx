import React, { useRef } from 'react';

const Sidebar = () => {
  const fileInputRef = useRef(null); // Referensi untuk elemen input file

  const handleFileUpload = () => {
    // Membuka dialog unggah file
    fileInputRef.current.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      alert(`File diunggah: ${file.name}`); // Ganti dengan logika upload sesuai kebutuhan
    }
  };

  return (
    <div className='w-[25%] h-[100%] p-2 flex-col gap-2 text-white lg-flex'>
      <div className='bg-[#19191a] h-[100%] rounded flex flex-col justify-around'>
        <div className='bg-white h-screen flex justify-center items-center rounded m-5'></div>

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
            className="px-4 py-2 bg-[#3054d9] text-white rounded"
            onClick={handleFileUpload}
          >
            Upload
          </button>
        </div>

        {/* Tombol Audios */}
        <div className="flex justify-center items-center p-2">
          <button
            className="px-4 py-2 bg-[#3054d9] text-white rounded"
            onClick={handleFileUpload}
          >
            Audios
          </button>
        </div>

        {/* Tombol Pictures */}
        <div className="flex justify-center items-center p-2">
          <button
            className="px-4 py-2 bg-[#3054d9] text-white rounded"
            onClick={handleFileUpload}
          >
            Pictures
          </button>
        </div>

        {/* Tombol Mapper */}
        <div className="flex justify-center items-center p-2">
          <button
            className="px-4 py-2 bg-[#3054d9] text-white rounded"
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
