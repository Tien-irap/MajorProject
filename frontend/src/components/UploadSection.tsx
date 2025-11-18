import React, { useRef, useState } from "react"; // Added useState
import { Upload } from "lucide-react";
import { Button, Card } from "./ui/stubs"; // Fixed path

interface UploadSectionProps {
  onUpload: (file: File) => void;
  isLoading: boolean;
}

export const UploadSection = ({ onUpload, isLoading }: UploadSectionProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false); // For drag/drop UI

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  // --- Added Drag and Drop handlers for better UX ---
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file && (file.type === "application/x-chess-pgn" || file.name.endsWith(".pgn"))) {
      onUpload(file);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  };
  // ---

  // Define custom styles to match your theme
  const gradientGold = "bg-gradient-to-r from-yellow-400 via-yellow-500 to-orange-500";
  const gradientBoard = "bg-zinc-900"; // Simplified gradient
  const shadowCard = "shadow-xl";
  const shadowGlow = "hover:shadow-cyan-500/10";
  const textAccent = "text-cyan-400";
  const borderAccent = "border-cyan-400";
  const bgAccent = "bg-cyan-500/10";
  const borderBorder = "border-zinc-800";
  const textForeground = "text-white";
  const textMutedForeground = "text-zinc-400";
  const textPrimaryForeground = "text-black";

  return (
    <Card 
      className={`p-8 text-center ${gradientBoard} ${shadowCard} ${shadowGlow} transition-all duration-300 ${dragOver ? borderAccent : borderBorder} border-2 border-dashed`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <div className="flex flex-col items-center gap-4">
        <div className={`p-4 rounded-full ${bgAccent}`}>
          <Upload className={`w-8 h-8 ${textAccent}`} />
        </div>
        <div>
          <h3 className={`text-xl font-semibold ${textForeground} mb-2`}>Upload Your Game</h3>
          <p className={`${textMutedForeground} text-sm`}>
            Drag & drop a PGN file here, or click to browse
          </p>
        </div>
        <Button
          onClick={handleButtonClick}
          disabled={isLoading}
          className={`${gradientGold} ${textPrimaryForeground} font-semibold hover:opacity-90 transition-opacity cursor-pointer`}
        >
          {isLoading ? "Uploading..." : "Choose File"}
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pgn, application/x-chess-pgn"
          onChange={handleFileChange}
          className="hidden"
          disabled={isLoading}
        />
      </div>
    </Card>
  );
};