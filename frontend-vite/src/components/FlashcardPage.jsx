import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Button } from "../components/ui/button";
import { ArrowLeft } from "lucide-react";
import { DataTable } from "../components/ui/DataTable";

const API_BASE = import.meta.env.VITE_API_URL;

function FlashcardPage({ filename, notes, flashcards = [], setFlashcards, onBack }) {
  const [localFlashcards, setLocalFlashcards] = useState(() => flashcards || []);
  const [loading, setLoading] = useState(flashcards.length === 0);

  useEffect(() => {
    if (flashcards.length > 0 && localFlashcards.length === 0) {
      setLocalFlashcards(flashcards);
    }
  }, [flashcards, localFlashcards.length]);

  useEffect(() => {
    if (flashcards.length === 0) {
      axios
        .get(`${API_BASE}/generate/${filename}`, {
          params: { text: notes },
        })
        .then((res) => {
          setLocalFlashcards(res.data.flashcards || []);
          setFlashcards(res.data.flashcards || []);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Error generating flashcards:", err);
          setLoading(false);
        });
    }
  }, [filename, notes, flashcards.length, setFlashcards]);

  const handleUpdate = (index, field, value) => {
    const updated = localFlashcards.map((flashcard, i) => {
      if (i === index) {
        return { ...flashcard, [field]: value };
      }
      return flashcard;
    });
    setLocalFlashcards(updated);
    setFlashcards(updated);
  };

  const handleDelete = (index) => {
    const updated = localFlashcards.filter((_, i) => i !== index);
    setLocalFlashcards(updated);
    setFlashcards(updated);
  };

  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(localFlashcards, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    triggerDownload(url, "flashcards.json");
  };

  const downloadCSV = () => {
    const csv = localFlashcards
      .map((f) => `"${f.question.replace(/"/g, '""')}","${f.answer.replace(/"/g, '""')}"`)
      .join("\n");
    const blob = new Blob([`"Question","Answer"\n${csv}`], {
      type: "text/csv",
    });
    const url = URL.createObjectURL(blob);
    triggerDownload(url, "flashcards.csv");
  };

  const downloadPDF = () => {
    import("jspdf").then((jsPDF) => {
      const doc = new jsPDF.jsPDF();
      let y = 10;
      const lineHeight = 10;
      const maxWidth = 180;
      const qaSpacing = 4;
      const pairSpacing = 10;
      const marginBottom = 20;
      const pageHeight = doc.internal.pageSize.height;
  
      localFlashcards.forEach((f, i) => {
        const questionLines = doc
        .splitTextToSize(`Q${i + 1}: ${f.question}`.trim(), maxWidth)
        .filter((line) => line.trim() !== "");

      const answerLines = doc
        .splitTextToSize(`A${i + 1}: ${f.answer}`.trim(), maxWidth)
        .filter((line) => line.trim() !== "");

  
        const totalHeight =
          (questionLines.length + answerLines.length) * lineHeight +
          qaSpacing + pairSpacing;
  
        if (y + totalHeight > pageHeight - marginBottom) {
          doc.addPage();
          y = 10;
        }
  
        // Draw question line-by-line
        questionLines.forEach((line) => {
          doc.text(line, 10, y);
          y += lineHeight;
        });
  
        y += qaSpacing;
  
        // Draw answer line-by-line
        answerLines.forEach((line) => {
          doc.text(line, 10, y);
          y += lineHeight;
        });
  
        y += pairSpacing;
      });
  
      doc.save("flashcards.pdf");
    });
  };
  
  
  

  const triggerDownload = (url, filename) => {
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const columns = [
    {
      accessorKey: "question",
      header: "Question",
      cell: ({ row }) => {
        const [value, setValue] = useState(row.getValue("question"));
        const textareaRef = useRef(null);

        useEffect(() => {
          if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
          }
        }, [value]);

        return (
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onBlur={() => handleUpdate(row.index, "question", value)}
            rows={1}
            className="w-full bg-transparent text-sm border-none focus:outline-none focus:ring-0 resize-none whitespace-pre-wrap break-words"
            style={{
              minHeight: "2.5rem",
              overflow: "hidden",
              wordBreak: "break-word",
              whiteSpace: "pre-wrap",
            }}
          />
        );
      },
    },
    {
      accessorKey: "answer",
      header: "Answer",
      cell: ({ row }) => {
        const [value, setValue] = useState(row.getValue("answer"));
        const textareaRef = useRef(null);

        useEffect(() => {
          if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
          }
        }, [value]);

        return (
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onBlur={() => handleUpdate(row.index, "answer", value)}
            rows={1}
            className="w-full bg-transparent text-sm border-none focus:outline-none focus:ring-0 resize-none whitespace-pre-wrap break-words"
            style={{
              minHeight: "2.5rem",
              overflow: "hidden",
              wordBreak: "break-word",
              whiteSpace: "pre-wrap",
            }}
          />
        );
      },
    },
    {
      id: "actions",
      header: "",
      cell: ({ row }) => (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => handleDelete(row.index)}
          className="text-gray-400 hover:text-red-500"
        >
          ✖
        </Button>
      ),
    },
  ];

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-screen space-y-6">
      <h2 className="text-xl font-semibold">Generating flashcards...</h2>
      <div className="w-1/2 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className="h-full bg-green-500 animate-pulse w-full"></div>
      </div>
    </div>
  );

  return (
    <div className="w-full px-4 py-8 space-y-8">
      <div className="w-full space-y-4 relative">
        <h1 className="text-[40px] font-bold text-center">Flashcards AI</h1>
        <div className="px-10">
          <div className="relative">
            <ArrowLeft
              className="w-5 h-5 absolute left-0 top-1/2 -translate-y-1/2 cursor-pointer"
              onClick={onBack}
            />
            <h2 className="text-xl font-semibold text-center">Generated Flashcards</h2>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl w-full px-10 py-6 overflow-x-auto">
        <DataTable columns={columns} data={localFlashcards} />

        <div className="mt-6 flex justify-center items-center gap-4">
          <span className="text-gray-600 font-medium">Save as:</span>
          <Button
            variant="outline"
            className="!border-[#3B48DE] !text-[#3B48DE] !bg-white hover:!bg-[#3B48DE] hover:!text-white"
            onClick={downloadJSON}
          >
            JSON
          </Button>
          <Button
            variant="outline"
            className="!border-[#3B48DE] !text-[#3B48DE] !bg-white hover:!bg-[#3B48DE] hover:!text-white"
            onClick={downloadCSV}
          >
            CSV
          </Button>
          <Button
            variant="outline"
            className="!border-[#3B48DE] !text-[#3B48DE] !bg-white hover:!bg-[#3B48DE] hover:!text-white"
            onClick={downloadPDF}
          >
            PDF
          </Button>
        </div>
      </div>
    </div>
  );
}

export default FlashcardPage;
