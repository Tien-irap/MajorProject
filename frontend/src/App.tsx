import { useState, useEffect, useRef } from "react";
import { UploadSection } from "./components/UploadSection";
import { AnalysisView } from "./components/AnalysisView";
import { ProfileCard } from "./components/ProfileCard";
import { RuleBook } from "./components/RuleBook";
import { WeaknessReport } from "./components/WeaknessReportView"; 
import { EvolutionaryTrainingRoom } from "./components/EvolutionaryTrainingRoom";
import { ToastProvider, useToast } from "./hooks/UseToast";
import { Loader2, LayoutDashboard, GraduationCap, ArrowLeft, Target, Swords } from "lucide-react";
import { Button } from "./components/ui/stubs";
import type { AnalysisResult, StatusResponse, PuzzleDB, SubmitPuzzleResult } from "./types";
import MasterComparison from "./components/MasterComparison"; 

// --- CONFIG ---
const API_BASE_URL = "http://localhost:8000"; 
const POLL_INTERVAL_MS = 2000; 
const MAX_POLL_RETRIES = 5; 

// --- User Statistics ---
const userStats = {
  gamesWon: 124,
  gamesLost: 89,
  rank: "Intermediate",
  rating: 1450
};

const AppContent = () => {
  // View State: 'dashboard', 'analysis', 'weakness', 'training', 'comparison'
  const [currentView, setCurrentView] = useState<'dashboard' | 'analysis' | 'weakness' | 'training' | 'comparison'>('dashboard');
  
  // Data State
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [completedId, setCompletedId] = useState<string | null>(null); // Stores ID for comparison view
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [puzzles, setPuzzles] = useState<PuzzleDB[]>([]);
  
  // UI State
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingPuzzles, setIsGeneratingPuzzles] = useState(false);
  const [pollingStatus, setPollingStatus] = useState("");
  const [pollErrorCount, setPollErrorCount] = useState(0);
  
  const { toast } = useToast();
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // --- POLLING LOGIC ---
  useEffect(() => {
    if (!analysisId || analysisResult) return;

    const fetchStatus = async () => {
      try {
        console.log(`📊 Polling status for: ${analysisId}...`);
        const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/status`);

        if (!response.ok) {
          // Handle 404 with retry logic
          if (response.status === 404 && pollErrorCount < MAX_POLL_RETRIES) {
            setPollErrorCount(prev => prev + 1);
            setPollingStatus(`Status: Starting job... (attempt ${pollErrorCount + 1}/${MAX_POLL_RETRIES})`);
            console.warn(`⚠️ Job not found yet. Retry ${pollErrorCount + 1}/${MAX_POLL_RETRIES}`);
            return;
          } else if (response.status === 404) {
            throw new Error(`Analysis job not found after ${MAX_POLL_RETRIES} attempts.`);
          } else {
            const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
            throw new Error(errorData.detail || "Failed to get status.");
          }
        }

        // Reset error count on successful poll
        setPollErrorCount(0);
        const data: StatusResponse = await response.json();
        console.log("📡 Poll Response:", data);

        setPollingStatus(`Status: ${data.status}...`);

        if (data.status === "COMPLETED") {
          console.log("✅ Analysis COMPLETED. Fetching final report...");
          
          if (pollingRef.current) {
            clearInterval(pollingRef.current);
            pollingRef.current = null;
          }

          toast("Analysis complete! Fetching report...", "success");

          // Small delay to ensure backend has finalized the result
          setTimeout(async () => {
            try {
              const resultResp = await fetch(`${API_BASE_URL}/analysis/${analysisId}`);
              if (!resultResp.ok) throw new Error("Failed to fetch final report");

              const resultData: AnalysisResult = await resultResp.json();
              setAnalysisResult(resultData);
              
              // Save the completed ID for comparison view
              setCompletedId(analysisId); 
              setAnalysisId(null); 
              setIsLoading(false);
              
              toast("Analysis Ready! View your results.", "success");
            } catch (error) {
              console.error("❌ Error fetching final result:", error);
              toast("Failed to fetch analysis result. Please try again.", "error");
              setIsLoading(false);
            }
          }, 500); 
          
        } else if (data.status === "FAILED") {
          console.error("❌ Analysis FAILED:", data.error);
          
          if (pollingRef.current) {
            clearInterval(pollingRef.current);
            pollingRef.current = null;
          }
          
          setAnalysisId(null);
          setIsLoading(false);
          toast(`Analysis Failed: ${data.error || "Unknown error"}`, "error");
        }
      } catch (error) {
        console.error("❌ Polling error:", error);
        
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
        
        setAnalysisId(null);
        setIsLoading(false);
        toast(error instanceof Error ? error.message : "An error occurred during analysis.", "error");
      }
    };

    // Start polling
    fetchStatus(); // Initial fetch
    pollingRef.current = setInterval(fetchStatus, POLL_INTERVAL_MS);

    // Cleanup on unmount or when dependencies change
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [analysisId, analysisResult, pollErrorCount, toast]);

  const handleUpload = async (file: File) => {
    setIsLoading(true);
    setAnalysisResult(null); 
    setAnalysisId(null); 
    setCompletedId(null); // Reset completed ID on new upload
    setPuzzles([]); // Clear previous puzzles
    setPollErrorCount(0); // Reset error count
    setPollingStatus("Uploading PGN file...");
    toast("Uploading PGN file...", 'info');

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/analysis/`, { 
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Upload failed: ${errText}`);
      }

      const data = await response.json();
      console.log("✅ Upload successful! Analysis ID:", data.analysis_id);
      toast("Upload successful! Queuing analysis...", 'success');
      
      setAnalysisId(data.analysis_id); 

    } catch (error: any) {
        console.error("❌ Upload Error:", error);
        toast(error.message || "Upload failed. Please try again.", 'error');
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
      <div className="space-y-8 lg:col-span-1">
        <ProfileCard stats={userStats} />
        <RuleBook />
      </div>

      <div className="lg:col-span-2 space-y-8">
        
        {/* LOADING STATE */}
        {isLoading && (
          <div className="p-12 border border-zinc-800 bg-zinc-900 rounded-lg flex flex-col items-center justify-center text-center shadow-xl">
            <Loader2 className="w-16 h-16 text-cyan-400 animate-spin mb-6" />
            <h3 className="text-2xl font-semibold text-white mb-2">Analyzing Your Game</h3>
            <p className="text-zinc-400">{pollingStatus || "Initializing..."}</p>
            <p className="text-zinc-500 text-sm mt-4">
              Job ID: {analysisId ? analysisId.slice(0, 8) : "..."}
            </p>
            <p className="text-zinc-500 text-xs mt-2">This usually takes 15-30 seconds depending on game length.</p>
          </div>
        )}

        {/* READY STATE */}
        {!isLoading && analysisResult && (
          <div className="p-8 border border-green-500/20 bg-zinc-900/50 rounded-lg flex flex-col items-center justify-center text-center shadow-xl gap-4">
            <div className="p-4 bg-green-500/10 rounded-full mb-2">
               <LayoutDashboard className="w-12 h-12 text-green-500" />
            </div>
            <h3 className="text-2xl font-bold text-white">Analysis Ready!</h3>
            <p className="text-zinc-400 max-w-md">
              Game analyzed: <strong>{analysisResult.game_headers?.Site || "Uploaded Game"}</strong>
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

               <Button 
                 onClick={() => setCurrentView('comparison')}
                 className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-6 text-lg flex-grow md:flex-grow-0"
               >
                 <Swords className="w-5 h-5 mr-2" />
                 Compare with Masters
               </Button>
            </div>
            
            <Button 
               onClick={() => { setAnalysisResult(null); setAnalysisId(null); setCompletedId(null); setPuzzles([]); }}
               className="mt-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-400 text-sm"
             >
               Analyze New Game
             </Button>
          </div>
        )}

        {/* UPLOAD STATE */}
        {!isLoading && !analysisResult && (
          <UploadSection onUpload={handleUpload} isLoading={isLoading} />
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
        
        <div className="flex gap-2">
            <Button 
            onClick={() => setCurrentView('weakness')} 
            className="bg-zinc-800 hover:bg-zinc-700 text-orange-400 border border-orange-500/30"
            >
            <Target className="w-4 h-4 mr-2" /> Weakness Report
            </Button>
            <Button 
            onClick={() => setCurrentView('comparison')} 
            className="bg-zinc-800 hover:bg-zinc-700 text-indigo-400 border border-indigo-500/30"
            >
            <Swords className="w-4 h-4 mr-2" /> Vs Master
            </Button>
        </div>
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

  const renderComparison = () => {
    // Use completedId if available, fallback to analysisId
    const idToUse = completedId || analysisId;
    
    if (!idToUse) {
      // Fallback error state if no ID is available
      return (
        <div className="p-8 border border-red-500/20 bg-zinc-900 rounded-lg text-center">
          <h3 className="text-xl font-bold text-red-500 mb-2">Error: No Analysis ID</h3>
          <p className="text-zinc-400 mb-4">Cannot load comparison view without an analysis ID.</p>
          <Button 
            onClick={() => setCurrentView('dashboard')}
            className="bg-zinc-800 hover:bg-zinc-700"
          >
            Return to Dashboard
          </Button>
        </div>
      );
    }

    return (
      <MasterComparison
        analysisId={idToUse}
        onBack={() => setCurrentView('dashboard')}
      />
    );
  };

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
        {currentView === 'comparison' && renderComparison()}
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
