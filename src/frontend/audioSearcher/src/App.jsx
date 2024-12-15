import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import SongGrid from './components/SongGrid';

const App = () => {
  const [results, setResults] = useState([]); // State untuk menyimpan hasil dari backend
  const [uploadedImage, setUploadedImage] = useState(null);

  return (
    <div className="h-screen bg-black">
      <Navbar />
      <div className="h-[90%] flex">
        {/* Sidebar menerima fungsi setResults dan setUploadedImage sebagai props */}
        <Sidebar 
          setResults={setResults} 
          setUploadedImage={setUploadedImage}
          uploadedImage={uploadedImage}
        />
        {/* SongGrid menerima data results sebagai props */}
        <SongGrid songs={results} />
      </div>
    </div>
  );
};

export default App;
