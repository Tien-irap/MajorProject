import { useRef } from "react";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface UploadSectionProps {
  onUpload: (file: File) => Promise<void>;
  isLoading: boolean;
}

export const UploadSection = ({ onUpload, isLoading }: UploadSectionProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <Card className="p-8 text-center bg-gradient-board border-border shadow-card hover:shadow-glow transition-shadow">
      <div className="flex flex-col items-center gap-4">
        <div className="p-4 rounded-full bg-accent/10">
          <Upload className="w-8 h-8 text-accent" />
        </div>
        <div>
          <h3 className="text-xl font-semibold text-foreground mb-2">Upload Your Game</h3>
          <p className="text-muted-foreground text-sm">
            Upload a PGN file to analyze your chess game
          </p>
        </div>
        <Button
          onClick={handleButtonClick}
          disabled={isLoading}
          className="bg-gradient-gold text-primary-foreground hover:opacity-90 transition-opacity cursor-pointer"
        >
          {isLoading ? "Uploading..." : "Choose File"}
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pgn"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>
    </Card>
  );
};
