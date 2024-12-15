import React, { useState } from "react";

const SongCard = ({ fileName, distance , imagePath}) => {
  // Tambahkan validasi default value
  const safeDistance = typeof distance === "number" ? distance.toFixed(2) : "%";

  return (
    <div className="bg-gray-300 w-full h-[150px] flex flex-col justify-between p-2 rounded-md shadow-md">
      <div className="bg-gray-400 w-full h-[70%] rounded-sm flex justify-center items-center">
        <img
          src={imagePath}
          alt={fileName}
          className="w-full h-full object-cover rounded-sm"
        />
      </div>
      <div className="flex justify-between items-center text-sm mt-2 text-black">
        <span className="truncate">{fileName}</span>
        <span className="truncate">{safeDistance}</span>
      </div>
    </div>
  );
};


const SongGrid = ({ songs }) => {
  console.log("Data songs diterima di SongGrid:", songs);
  
  const itemsPerPage = 12; // menentukan jumlah lagu yang ditampilkan per halaman
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(songs.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const currentSongs = songs.slice(startIndex, startIndex + itemsPerPage);

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
    <div className="bg-[#092D3A] w-[100%] flex items-center justify-center">
      <div className="w-full max-w-6xl p-4">
        <div className="flex flex-col justify-start items-center">
          <div className="w-full bg-[#092D3A] p-4 flex justify-center items-center">
            <button className="px-4 py-2 m-2 bg-[#BABEB8] text-[#092D3A] rounded">
              Album
            </button>
            <button className="px-4 py-2 m-2 bg-[#BABEB8] text-[#092D3A] rounded">
              Music
            </button>
          </div>
        </div>

        {/*song grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {currentSongs.map((song, index) => {
            console.log(song.imagePath); // Tambahkan log di sini
            return (
              <SongCard 
                key={index}
                fileName={song.filename} 
                distance={song.distance} 
                imagePath={song.imagePath}
              />
            );
          })};
        </div>

        {/* Pagination */}
        <div className="flex justify-between items-center mt-6">
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