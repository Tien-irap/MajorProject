import { useState, useEffect, useRef } from "react";
import { UploadSection } from "./components/UploadSection";
import { AnalysisView } from "./components/AnalysisView";
import { ProfileCard } from "./components/ProfileCard";
import { RuleBook } from "./components/RuleBook";
import { WeaknessReport } from "./components/WeaknessReportView"; 
import { ToastProvider, useToast } from "./hooks/UseToast";
import { Loader2, LayoutDashboard, GraduationCap, ArrowLeft, Target, Swords } from "lucide-react"; // Added Swords
import { Button } from "./components/ui/stubs";
import type { AnalysisResult, StatusResponse } from "./types";
import MasterComparison from "./components/MasterComparison"; 

// --- CONFIG ---
const API_BASE_URL = "http://127.0.0.1:8000"; 
const POLL_INTERVAL_MS = 2000; 

const userStats = {
  gamesWon: 124,
  gamesLost: 89,
  rank: "Intermediate",
  rating: 1450
};

const AppContent = () => {
  // View State
  const [currentView, setCurrentView] = useState<'dashboard' | 'analysis' | 'weakness' | 'training' | 'comparison'>('dashboard');
  
  // Data State
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [completedId, setCompletedId] = useState<string | null>(null); // NEW: Stores ID for comparison
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  
  // UI State
  const [isLoading, setIsLoading] = useState(false);
  const [pollingStatus, setPollingStatus] = useState("");
  
  const { toast } = useToast();
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // --- POLLING LOGIC ---
  useEffect(() => {
    if (!analysisId || analysisResult) return;

    const fetchStatus = async () => {
      try {
        console.log(`Polling status for: ${analysisId}...`);
        const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/status`);

        if (!response.ok) {
          console.warn(`Poll failed: ${response.status}`);
          return; 
        }

        const data: StatusResponse = await response.json();
        console.log("Poll Response:", data);

        setPollingStatus(`Status: ${data.status}`);

        if (data.status === "COMPLETED") {
          console.log("Status is COMPLETED. Stopping polling...");
          clearInterval(pollingRef.current!);
          pollingRef.current = null;

          toast("Analysis complete! Fetching report...", "success");

          setTimeout(async () => {
            try {
              const resultResp = await fetch(`${API_BASE_URL}/analysis/${analysisId}`);
              if (!resultResp.ok) throw new Error("Failed to fetch final report");

              const resultData = await resultResp.json();
              setAnalysisResult(resultData);
              
              // --- FIX: Save the ID for later use before clearing ---
              setCompletedId(analysisId); 
              setAnalysisId(null); 
              
              setIsLoading(false);
              toast("Analysis Ready!", "success");
            } catch (error) {
              console.error("Error fetching final result:", error);
              toast("Failed to fetch analysis result. Please try again.", "error");
            }
          }, 500); 
        } else if (data.status === "FAILED") {
          clearInterval(pollingRef.current!);
          pollingRef.current = null;
          setAnalysisId(null);
          setIsLoading(false);
          toast(`Analysis Failed: ${data.error}`, "error");
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    };

    pollingRef.current = setInterval(fetchStatus, POLL_INTERVAL_MS);

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [analysisId, analysisResult, toast]);

  const handleUpload = async (file: File) => {
    setIsLoading(true);
    setAnalysisResult(null); 
    setAnalysisId(null); 
    setCompletedId(null); // Reset completed ID on new upload
    setPollingStatus("Uploading...");
    toast("Uploading PGN file...", 'info');

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/analysis`, { 
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Upload failed: ${errText}`);
      }

      const data = await response.json();
      toast("Upload success! Starting analysis...", 'success');
      
      setAnalysisId(data.analysis_id); 

    } catch (error: any) {
        console.error("Upload Error:", error);
        toast(error.message, 'error');
        setIsLoading(false); 
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
            <p className="text-zinc-400">{pollingStatus}</p>
            <p className="text-zinc-500 text-sm mt-4">
               Job ID: {analysisId ? analysisId.slice(0,8) : "..."}
            </p>
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
                 View Analysis
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
               onClick={() => { setAnalysisResult(null); setAnalysisId(null); setCompletedId(null); }}
               className="mt-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-400 text-sm"
             >
               Analyze Another Game
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
          onStartTraining={() => setCurrentView('training')} 
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
      <div className="flex items-center gap-4 mb-4">
        <Button 
          onClick={() => setCurrentView('analysis')} 
          className="bg-zinc-800 hover:bg-zinc-700 text-zinc-300"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Analysis
        </Button>
      </div>
      
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6 p-8 bg-zinc-900 rounded-lg border border-zinc-800">
         <div className="p-6 bg-yellow-500/10 rounded-full">
           <GraduationCap className="w-24 h-24 text-yellow-500" />
         </div>
         <h2 className="text-3xl font-bold text-white">Training Room</h2>
         <p className="text-xl text-zinc-400 max-w-2xl">
           Based on your analysis, we are generating custom puzzles to target your specific weaknesses.
         </p>
         <div className="px-4 py-2 bg-zinc-800 rounded-full text-cyan-400 font-mono text-sm">
           Coming Soon
         </div>
      </div>
    </div>
  );

  const renderComparison = () => {
    // --- FIX: Use completedId, fallback to analysisId ---
    const idToUse = completedId || analysisId;
    
    if (!idToUse) {
         // Fallback if somehow both are null (prevents crash)
         return <div className="text-white">Error: No Analysis ID found. Please re-upload.</div>
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
