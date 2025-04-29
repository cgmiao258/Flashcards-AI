import React, { useState } from "react";
import UploadPage from "./components/UploadPage";
import ReviewPage from "./components/ReviewPage";
import FlashcardPage from "./components/FlashcardPage";
import { Button } from "./components/ui/button";

export default function App() {
  const [step, setStep] = useState("upload"); // 'upload', 'review', 'flashcards'
  const [filename, setFilename] = useState(null);
  const [notes, setNotes] = useState("");
  const [flashcards, setFlashcards] = useState([]);
  const [fromFlashcards, setFromFlashcards] = useState(false); // 🆕

  const handleUploaded = (name) => {
    setFilename(name);
    setNotes("");
    setFlashcards([]);
    setFromFlashcards(false); // 🆕 Coming from upload, not flashcards
    setStep("review");
  };

  const handleReviewed = (text, cards) => {
    setNotes(text);
    setFlashcards(cards);
    setStep("flashcards");
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-8 py-8">
      {step === "upload" && (
        <UploadPage onUploaded={handleUploaded} />
      )}

      {step === "review" && (
        <ReviewPage
          filename={filename}
          notes={notes}
          fromFlashcards={fromFlashcards} // 🆕 pass direction
          onReviewed={handleReviewed}
          onBack={() => setStep("upload")}
        />
      )}

      {step === "flashcards" && (
        <div>
          <FlashcardPage
            filename={filename}
            notes={notes}
            flashcards={flashcards}
            setFlashcards={setFlashcards}
            onBack={() => setStep("review")}
          />
        </div>
      )}
    </div>
  );
}
