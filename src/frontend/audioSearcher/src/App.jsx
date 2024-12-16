import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import SongGrid from './components/SongGrid';

const App = () => {
  const [results, setResults] = useState([]); // State untuk menyimpan hasil dari backend
  const [uploadedImage, setUploadedImage] = useState(null);
  const [uploadMode, setUploadMode] = useState("pictures"); // Tambahkan state untuk mode

  return (
    <div className="h-screen bg-black">
      <Navbar />
      <div className="h-[90%] flex">
        {/* Sidebar menerima fungsi setResults dan setUploadedImage sebagai props */}
        <Sidebar 
          setResults={setResults} 
          setUploadedImage={setUploadedImage}
          uploadedImage={uploadedImage}
          uploadMode={uploadMode}
        />
        {/* SongGrid menerima data results sebagai props */}
        <SongGrid 
          songs={results}
          setUploadMode={setUploadMode}
          uploadMode={uploadMode} />
      </div>
    </div>
  );
};

export default App;
