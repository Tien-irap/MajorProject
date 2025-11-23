import { useState, useEffect } from "react";
import { UploadSection } from "./components/UploadSection";
import { AnalysisView } from "./components/AnalysisView";
import { ProfileCard } from "./components/ProfileCard";
import { RuleBook } from "./components/RuleBook";
import { WeaknessReport } from "./components/WeaknessReportView"; 
import { EvolutionaryTrainingRoom } from "./components/EvolutionaryTrainingRoom";
import { ToastProvider, useToast } from "./hooks/UseToast";
import { Loader2, LayoutDashboard, GraduationCap, ArrowLeft, Target } from "lucide-react";
import { Button } from "./components/ui/stubs";
import type { AnalysisResult, StatusResponse, PuzzleDB, SubmitPuzzleResult } from "./types";

const API_BASE_URL = "http://localhost:8000"; 
const MAX_POLL_RETRIES = 5; 

// --- DUMMY PROFILE STATS (As requested) ---
const userStats = {
  gamesWon: 124,
  gamesLost: 89,
  rank: "Intermediate",
  rating: 1450
};

function AppContent() {
  // View State: 'dashboard', 'analysis', 'weakness', 'training'
  const [currentView, setCurrentView] = useState<'dashboard' | 'analysis' | 'weakness' | 'training'>('dashboard');
  
  const [isLoading, setIsLoading] = useState(false);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [pollingStatus, setPollingStatus] = useState("");
  const [pollErrorCount, setPollErrorCount] = useState(0);
  const [puzzles, setPuzzles] = useState<PuzzleDB[]>([]);
  const [isGeneratingPuzzles, setIsGeneratingPuzzles] = useState(false);
  const { toast } = useToast();

  // --- POLLING EFFECT ---
  useEffect(() => {
    if (!analysisId) return;
    setPollErrorCount(0);
    let intervalId: number | undefined;

    const poll = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/status`);
        
        if (!response.ok) {
           if (response.status === 404 && pollErrorCount < MAX_POLL_RETRIES) {
             setPollErrorCount(prev => prev + 1);
             setPollingStatus(`Status: Starting job... (attempt ${pollErrorCount + 1})`);
             return; 
           } else if (response.status === 404) {
             throw new Error(`Analysis job not found.`);
           } else {
             const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
             throw new Error(errorData.detail || "Failed to get status.");
           }
        }
        
        setPollErrorCount(0);
        const data: StatusResponse = await response.json();
        setPollingStatus(`Status: ${data.status}...`);

        if (data.status === "COMPLETED") {
          if (intervalId) clearInterval(intervalId);
          toast("Analysis complete! Finalizing...", 'success');
          
          const resultResponse = await fetch(`${API_BASE_URL}/analysis/${analysisId}`);
           if (!resultResponse.ok) throw new Error("Failed to fetch results.");
          
          const resultData: AnalysisResult = await resultResponse.json();
          setAnalysisResult(resultData);
          setAnalysisId(null); 
          setIsLoading(false);
          toast("Analysis Ready! Click 'View Analysis' to see results.", 'success');
        } else if (data.status === "FAILED") {
          if (intervalId) clearInterval(intervalId);
          toast(`Analysis failed: ${data.error}`, 'error');
          setAnalysisId(null); 
          setIsLoading(false);
        }
      } catch (error) {
        console.error("Polling error:", error);
        if (intervalId) clearInterval(intervalId);
        setAnalysisId(null);
        setIsLoading(false);
        toast("An error occurred during analysis.", 'error');
      }
    };

    poll();
    intervalId = setInterval(poll, 3000) as unknown as number;
    return () => { if (intervalId) clearInterval(intervalId); };
  }, [analysisId, toast, pollErrorCount]);

  const handleUpload = async (file: File) => {
    setIsLoading(true);
    setAnalysisResult(null); 
    setAnalysisId(null); 
    setPuzzles([]); // Clear previous puzzles
    toast("Uploading PGN file...", 'info');

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/analysis/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Upload failed");

      const data = await response.json();
      toast("Upload successful! Queuing analysis...", 'success');
      setAnalysisId(data.analysis_id); 
    } catch (error) {
        console.error("Upload failed:", error);
        toast("Upload failed. Please try again.", 'error');
        setIsLoading(false); 
    }
  };

  const handleGeneratePuzzles = async (fen: string, moveUci: string, difficultyLevel: number = 1) => {
    setIsGeneratingPuzzles(true);
    toast("Generating evolutionary puzzles...", 'info');
    
    console.log("=== Generating Puzzles ===");
    console.log("Request payload:", { fen, move_uci: moveUci, difficulty_level: difficultyLevel });
    
    try {
      const response = await fetch(`${API_BASE_URL}/genpuzzle/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          fen,
          move_uci: moveUci,
          difficulty_level: difficultyLevel,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(errorData.detail || "Failed to generate puzzles");
      }

      const puzzleData: PuzzleDB[] = await response.json();
      console.log("Generated puzzles:", puzzleData);
      
      setPuzzles(puzzleData);
      setCurrentView('training');
      toast(`Generated ${puzzleData.length} tactical puzzles!`, 'success');
    } catch (error) {
      console.error("Puzzle generation failed:", error);
      toast(`Failed to generate puzzles: ${error instanceof Error ? error.message : "Unknown error"}`, 'error');
    } finally {
      setIsGeneratingPuzzles(false);
    }
  };

  const handleSubmitPuzzleResult = async (result: SubmitPuzzleResult) => {
    try {
      const response = await fetch(`${API_BASE_URL}/genpuzzle/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(result),
      });

      if (!response.ok) {
        throw new Error("Failed to submit result");
      }

      const data = await response.json();
      console.log("Result submitted:", data);
    } catch (error) {
      console.error("Failed to submit puzzle result:", error);
      // Don't show error toast to user as this is background submission
    }
  };

  // --- RENDER HELPERS ---

  const renderDashboard = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-in fade-in duration-500">
      {/* Left Column: Profile & Rules */}
      <div className="space-y-8 lg:col-span-1">
        <ProfileCard stats={userStats} />
        <RuleBook />
      </div>

      {/* Right Column: Action Center */}
      <div className="lg:col-span-2 space-y-8">
        {/* If analysis is actively loading, show spinner card */}
        {(isLoading || analysisId) && (
          <div className="p-12 border border-zinc-800 bg-zinc-900 rounded-lg flex flex-col items-center justify-center text-center shadow-xl">
            <Loader2 className="w-16 h-16 text-cyan-400 animate-spin mb-6" />
            <h3 className="text-2xl font-semibold text-white mb-2">Analyzing Your Game</h3>
            <p className="text-zinc-400">{pollingStatus || "Initializing..."}</p>
            <p className="text-zinc-500 text-sm mt-4">This usually takes 15-30 seconds depending on game length.</p>
          </div>
        )}

        {/* If not loading, show Upload or "Analysis Ready" card */}
        {!isLoading && !analysisId && (
          <>
            {analysisResult ? (
              <div className="p-8 border border-green-500/20 bg-zinc-900/50 rounded-lg flex flex-col items-center justify-center text-center shadow-xl gap-4">
                <div className="p-4 bg-green-500/10 rounded-full mb-2">
                   <LayoutDashboard className="w-12 h-12 text-green-500" />
                </div>
                <h3 className="text-2xl font-bold text-white">Analysis Ready!</h3>
                <p className="text-zinc-400 max-w-md">
                  We have analyzed your game <strong>{analysisResult.game_headers.Site || "Uploaded Game"}</strong>. 
                </p>
                
                <div className="flex flex-wrap justify-center gap-4 mt-4 w-full">
                   <Button 
                     onClick={() => setCurrentView('analysis')}
                     className="bg-green-600 hover:bg-green-700 text-white px-6 py-6 text-lg flex-grow md:flex-grow-0"
                   >
                     View Move Analysis
                   </Button>

                   <Button 
                     onClick={() => setCurrentView('weakness')}
                     className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-6 text-lg flex-grow md:flex-grow-0"
                   >
                     <Target className="w-5 h-5 mr-2" />
                     Weakness Report
                   </Button>
                </div>
                
                <Button 
                   onClick={() => setAnalysisResult(null)}
                   className="mt-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-400 text-sm"
                 >
                   Analyze New Game
                 </Button>
              </div>
            ) : (
              <UploadSection onUpload={handleUpload} isLoading={isLoading} />
            )}
          </>
        )}
      </div>
    </div>
  );

  const renderAnalysis = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-4">
        <Button 
          onClick={() => setCurrentView('dashboard')} 
          className="bg-zinc-800 hover:bg-zinc-700 text-zinc-300"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
        </Button>
        
        <Button 
          onClick={() => setCurrentView('weakness')} 
          className="bg-zinc-800 hover:bg-zinc-700 text-orange-400 border border-orange-500/30"
        >
          <Target className="w-4 h-4 mr-2" /> See Weakness Report
        </Button>
      </div>
      {analysisResult && (
        <AnalysisView 
          analysis={analysisResult} 
          onStartTraining={(fen, moveUci) => handleGeneratePuzzles(fen, moveUci, 1)} 
        />
      )}
    </div>
  );

  const renderWeaknessReport = () => (
    <div className="space-y-6">
       {analysisResult && (
        <WeaknessReport 
          analysis={analysisResult}
          onBack={() => setCurrentView('dashboard')}
        />
       )}
    </div>
  );

  const renderTraining = () => (
    <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
      <EvolutionaryTrainingRoom
        puzzles={puzzles}
        onBack={() => setCurrentView('analysis')}
        onSubmitResult={handleSubmitPuzzleResult}
        isLoading={isGeneratingPuzzles}
      />
    </div>
  );

  // --- MAIN RENDER ---
  return (
    <div className="min-h-screen bg-zinc-950 text-white font-sans selection:bg-cyan-500/30">
      <header className="p-4 border-b border-zinc-800 sticky top-0 bg-zinc-950/90 backdrop-blur-sm z-10 mb-8">
        <div className="container mx-auto flex items-center justify-between">
          <h1 
            className="text-2xl font-bold flex items-center gap-2 cursor-pointer" 
            onClick={() => setCurrentView('dashboard')}
          >
            <span className="text-3xl">♟️</span> AI Chess Tutor
          </h1>
          {currentView !== 'dashboard' && (
             <Button 
               onClick={() => setCurrentView('dashboard')}
               className="text-xs bg-zinc-800/50 hover:bg-zinc-800"
             >
               Dashboard
             </Button>
          )}
        </div>
      </header>
      
      <main className="container mx-auto p-4 md:p-8 pb-20">
        {currentView === 'dashboard' && renderDashboard()}
        {currentView === 'analysis' && renderAnalysis()}
        {currentView === 'weakness' && renderWeaknessReport()}
        {currentView === 'training' && renderTraining()}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}