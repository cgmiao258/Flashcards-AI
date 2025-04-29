import React, { useState } from "react"
import { Button } from "../components/ui/button"

function UploadPage({ onUploaded }) {
  const [file, setFile] = useState(null)
  const [fileName, setFileName] = useState("")

  const handleUpload = async () => {
    if (!file) return;
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/upload`, {
        method: "POST",
        body: formData,
      });
  
      const data = await res.json();
  
      console.log("Upload success:", data);
      setFileName(file.name); // show selected filename
      onUploaded(data.filename);
    } catch (err) {
      console.error("Upload failed:", err);
    }
  };
  
  return (
    <div className="h-full w-full flex items-center justify-center bg-gray-100 px-4">
      <div className="bg-white rounded-2xl p-8 w-full max-w-md h-175 flex flex-col justify-center items-center text-center space-y-4">

        {/* Title */}
        <h1 className="text-[40px] font-bold">Flashcards AI</h1>

        {/* Description or file name */}
        <p className="text-sm text-gray-500">{fileName || "Upload handwritten notes as an image"}</p>

        {/* Upload zone */}
        <label htmlFor="file-input" className="cursor-pointer bg-gray-100 border border-gray-300 rounded-md px-6 py-3 w-full text-center text-sm text-gray-500 hover:bg-gray-200">
          Upload File
        </label>
        <input
          id="file-input"
          type="file"
          onChange={(e) => {
            setFile(e.target.files[0]);
            setFileName(e.target.files[0]?.name || "");
          }}
          className="hidden"
        />

        {/* Continue button */}
        <Button
          className={`w-full text-white transition-opacity ${
            file ? '!bg-[#3B48DE] hover:!bg-[#2f39b4] opacity-100' : '!bg-[#3B48DE] opacity-50 cursor-not-allowed'
          }`}
          onClick={handleUpload}
          disabled={!file}
        >
          Continue
        </Button>

        {/* Subtext */}
        <p className="text-xs text-gray-400 mt-2">
          Supported file formats: JPEG, PNG
        </p>
      </div>
    </div>
  )
}

export default UploadPage
