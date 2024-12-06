import React, { useState } from "react";

const SongCard = ({ fileName, time }) => {
  return (
    <div className="bg-gray-300 w-full h-[150px] flex flex-col justify-between p-2 rounded-md shadow-md">
      {/* cover */}
      <div className="bg-gray-400 w-full h-[70%] rounded-sm"></div>

      {/* judul lagu */}
      <div className="flex justify-between items-center text-sm mt-2 text-black">
        <span className="truncate">{fileName}</span>
        <span className="truncate">%</span>
      </div>
    </div>
  );
};

const SongGrid = () => {
  const audioFiles = [
    "audio1.wav", "audio2.wav", "audio3.wav", "audio4.wav", "audio5.wav",
    "audio6.wav", "audio7.wav", "audio8.wav", "audio9.wav", "audio10.wav",
    "audio11.wav", "audio12.wav", "audio13.wav", "audio14.wav", "audio15.wav",
    "audio16.wav", "audio17.wav", "audio18.wav", "audio19.wav", "audio20.wav",
    "audio21.wav", "audio22.wav", "audio23.wav", "audio24.wav", "audio25.wav"
  ];
  
  const itemsPerPage = 12; // menentukan jumlah lagu yang ditampilkan per halaman
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(audioFiles.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const currentSongs = audioFiles.slice(startIndex, startIndex + itemsPerPage);

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  return (
    <div className="bg-[#092D3A] w-[100%]  flex items-center justify-center">
      <div className="w-full max-w-6xl p-4">
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {currentSongs.map((file, index) => (
            <SongCard key={index} fileName={file} />
          ))}
        </div>

        {/* pagination */}
        <div className=" flex justify-between items-center mt-6">
          <button
            onClick={handlePreviousPage}
            disabled={currentPage === 1}
            className="px-4 py-2 bg-[#BABEB8] text-[#092D3A] rounded disabled:bg-gray-400"
          >
            Previous
          </button>
          <span className="text-white">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            className="px-4 py-2 bg-[#BABEB8] text-[#092D3A] rounded disabled:bg-gray-400"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default SongGrid;
