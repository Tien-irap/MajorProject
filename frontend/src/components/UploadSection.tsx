import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface UploadSectionProps {
  onUpload: (file: File) => void;
}

export const UploadSection = ({ onUpload }: UploadSectionProps) => {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
    }
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
        <label htmlFor="file-upload">
          <Button className="bg-gradient-gold text-primary-foreground hover:opacity-90 transition-opacity cursor-pointer">
            Choose File
          </Button>
          <input
            id="file-upload"
            type="file"
            accept=".pgn"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>
      </div>
    </Card>
  );
};
