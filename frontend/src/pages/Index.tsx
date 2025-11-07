import { useState } from "react";
import { Crown } from "lucide-react";
import { UploadSection } from "@/components/UploadSection";
import { ProfileCard } from "@/components/ProfileCard";
import { RuleBook } from "@/components/RuleBook";
import { AnalysisView } from "@/components/AnalysisView";
import { TrainingRoom } from "@/components/TrainingRoom";
import { toast } from "sonner";

type ViewMode = 'dashboard' | 'analysis' | 'training';

const Index = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('dashboard');
  const [uploadedFileName, setUploadedFileName] = useState<string>('');

  const profileStats = {
    gamesWon: 142,
    gamesLost: 89,
    rank: "Expert",
    rating: 1847
  };

  const mockTopMoves = [
    { moveNumber: 12, move: "Nf6", evaluation: 2.3, isTopMove: true },
    { moveNumber: 18, move: "Qd7", evaluation: 1.8, isTopMove: true },
    { moveNumber: 24, move: "Rxe8+", evaluation: 3.1, isTopMove: true },
  ];

  const mockMistakes = [
    { moveNumber: 15, move: "Bc4?", evaluation: -1.2, isMistake: true },
    { moveNumber: 22, move: "f3?", evaluation: -2.1, isMistake: true },
    { moveNumber: 28, move: "Kh1??", evaluation: -4.5, isMistake: true },
  ];

  const mockPuzzle = {
    fen: "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
    solution: ["Nxe5", "Nxe5", "d4"],
    description: "Find the best move sequence to win material advantage. White to move and gain the upper hand."
  };

  const handleFileUpload = (file: File) => {
    setUploadedFileName(file.name);
    toast.success(`${file.name} uploaded successfully!`);
    setTimeout(() => {
      setViewMode('analysis');
      toast.success("Analysis complete!");
    }, 1500);
  };

  const handleStartTraining = () => {
    setViewMode('training');
    toast.info("Welcome to the training room! Solve puzzles to improve your skills.");
  };

  const handleNextPuzzle = () => {
    toast.success("Great job! Loading next puzzle...");
    // In a real app, this would load a new puzzle
  };

  const handleBackToDashboard = () => {
    setViewMode('dashboard');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-primary/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div 
              className="flex items-center gap-3 cursor-pointer" 
              onClick={handleBackToDashboard}
            >
              <div className="p-2 rounded-lg bg-gradient-gold">
                <Crown className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">ChessMaster Pro</h1>
                <p className="text-sm text-muted-foreground">Analyze. Learn. Improve.</p>
              </div>
            </div>
            <nav className="hidden md:flex gap-6">
              <button 
                onClick={handleBackToDashboard}
                className={`text-sm font-medium transition-colors ${viewMode === 'dashboard' ? 'text-accent' : 'text-muted-foreground hover:text-foreground'}`}
              >
                Dashboard
              </button>
              <button 
                onClick={() => setViewMode('analysis')}
                className={`text-sm font-medium transition-colors ${viewMode === 'analysis' ? 'text-accent' : 'text-muted-foreground hover:text-foreground'}`}
                disabled={!uploadedFileName}
              >
                Analysis
              </button>
              <button 
                onClick={handleStartTraining}
                className={`text-sm font-medium transition-colors ${viewMode === 'training' ? 'text-accent' : 'text-muted-foreground hover:text-foreground'}`}
              >
                Training
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {viewMode === 'dashboard' && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <UploadSection onUpload={handleFileUpload} />
              <RuleBook />
            </div>
            <div>
              <ProfileCard stats={profileStats} />
            </div>
          </div>
        )}

        {viewMode === 'analysis' && (
          <AnalysisView
            gameName={uploadedFileName || "Sample Game"}
            topMoves={mockTopMoves}
            mistakes={mockMistakes}
            onStartTraining={handleStartTraining}
          />
        )}

        {viewMode === 'training' && (
          <TrainingRoom
            puzzleData={mockPuzzle}
            onNextPuzzle={handleNextPuzzle}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border mt-12 py-6">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2025 ChessMaster Pro. Improve your chess skills with AI-powered analysis.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
