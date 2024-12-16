import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import SongGrid from './components/SongGrid';

const App = () => {
  const [results, setResults] = useState([]); 
  const [uploadedImage, setUploadedImage] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadMode, setUploadMode] = useState("pictures"); 
  const [executionTime, setExecutionTime] = useState(null);

  const handleSearch = async () => {
    if (!uploadedFile) {
      alert("Please upload a file first!");
      return;
    }
  
    const formData = new FormData();
    formData.append("file", uploadedFile);

    let url = "";
    if (uploadMode === "pictures") {
      url = "http://127.0.0.1:5000/upload-picture";
    } else if (uploadMode === "audio") {
      url = "http://127.0.0.1:5000/upload-midi";
    }

    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        alert("File processed successfully!");
        setResults(data.data || data.results || []);
        if (data.execution_time) {
          setExecutionTime(data.execution_time);
        }
      } else {
        alert(`Failed to process search: ${data.message}`);
      }
    } catch (error) {
      console.error("Error processing file:", error);
      alert("Error occurred during file processing.");
    }
  };

  return (
    <div className="h-screen bg-black">
      <Navbar />
      <div className="h-[90%] flex">
        {/* Sidebar menerima fungsi setResults dan setUploadedImage sebagai props */}
        <Sidebar 
          setResults={setResults} 
          setUploadedImage={setUploadedImage}
          uploadedImage={uploadedImage}
          setUploadedFile={setUploadedFile}
          uploadMode={uploadMode}
          executionTime={executionTime}
          setExecutionTime={setExecutionTime} 
        />
        {/* SongGrid menerima data results sebagai props */}
        <SongGrid 
          songs={results}
          uploadMode={uploadMode} 
          setUploadMode={setUploadMode}
          onSearch={handleSearch}
        />
      </div>
    </div>
  );
};

export default App;
