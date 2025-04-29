import React, { useEffect, useState } from "react";
import axios from "axios";
import { ArrowLeft } from "lucide-react";
import { Button } from "../components/ui/button";

const API_BASE = import.meta.env.VITE_API_URL;

function ReviewPage({ filename, notes, fromFlashcards, onReviewed, onBack }) {
  const [localNotes, setLocalNotes] = useState(notes || "");
  const [loading, setLoading] = useState(!notes); // Only loading if no notes passed

  // Fetch notes if needed
  useEffect(() => {
    if (!notes) {
      axios
        .get(`${API_BASE}/review/${filename}`)
        .then((res) => {
          setLocalNotes(res.data.notes || "");
          setLoading(false);
        })
        .catch((err) => {
          console.error("Error loading notes:", err);
          setLoading(false);
        });
    }
  }, [filename, notes]);

  // 🛠 Add beforeunload warning
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      e.preventDefault();
      e.returnValue = "Are you sure? \n This will delete your progress.";
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);

  const handleNext = () => {
    onReviewed(localNotes);
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-screen space-y-6">
      <h2 className="text-xl font-semibold">
        {fromFlashcards ? "Loading your reviewed notes..." : "Extracting notes from image..."}
      </h2>
      <div className="w-1/2 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className="h-full bg-blue-500 animate-pulse w-full"></div>
      </div>
    </div>
  );

  return (
    <div className="w-full px-4 py-8 space-y-8">
      {/* Header + Title */}
      <div className="w-full space-y-4 relative">
        <h1 className="text-[40px] font-bold text-center">Flashcards AI</h1>
        <div className="px-10">
          <div className="relative">
            <ArrowLeft
              className="w-5 h-5 absolute left-0 top-1/2 -translate-y-1/2 cursor-pointer"
              onClick={() => {
                const confirmLeave = window.confirm(
                  "Are you sure? \n This will delete your progress."
                );
                if (confirmLeave) {
                  onBack();
                }
              }}
            />
            <h2 className="text-xl font-semibold text-center">Review extracted notes</h2>
          </div>
        </div>
      </div>

      {/* Textarea Section */}
      <div className="bg-white rounded-xl w-full px-10 py-6">
        <textarea
          value={localNotes}
          onChange={(e) => setLocalNotes(e.target.value)}
          placeholder="Review and edit the extracted notes..."
          className="w-full border border-gray-300 rounded-md p-4 text-base leading-6 h-[500px] resize-y"
        />
      </div>

      {/* Action Button */}
      <div className="w-full flex justify-center">
        <Button
          onClick={handleNext}
          className="!bg-[#3B48DE] hover:!bg-[#2f39b4] text-white w-[300px] py-3 text-sm font-semibold"
        >
          Generate Flashcards
        </Button>
      </div>
    </div>
  );
}

export default ReviewPage;
