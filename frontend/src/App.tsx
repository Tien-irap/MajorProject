import React, { useState, useEffect, useRef } from "react";
import { UploadSection } from "./components/UploadSection";
import { AnalysisView } from "./components/AnalysisView";
import { ToastProvider, useToast } from "./hooks/UseToast";
import { Loader2 } from "lucide-react";
import type { AnalysisResult, StatusResponse } from "src/types";

const API_BASE_URL = "http://localhost:8000"; // Your FastAPI backend URL
const MAX_POLL_RETRIES = 5; // How many times to retry on a 404 before failing
const POLL_INTERVAL_MS = 3000; // Poll every 3 seconds

// Define the states of our application for cleaner state management
type AppState =
  | { status: 'idle' }
  | { status: 'uploading' }
  | { status: 'polling'; analysisId: string }
  | { status: 'success'; result: AnalysisResult }
  | { status: 'error'; message: string };

/**
 * Custom hook to manage the entire analysis polling lifecycle.
 * This encapsulates the complex asynchronous logic, keeping the component clean.
 */
const useAnalysisPoller = (
  appState: AppState,
  setAppState: React.Dispatch<React.SetStateAction<AppState>>
) => {
  const { toast } = useToast();
  const pollErrorCount = useRef(0);

  useEffect(() => {
    if (appState.status !== 'polling') {
      return;
    }

    const analysisId = appState.analysisId;
    let isCancelled = false;
    let timeoutId: number;

    const poll = async () => {
      if (isCancelled) return;

      try {
        const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/status`);

        if (!response.ok) {
          if (response.status === 404 && pollErrorCount.current < MAX_POLL_RETRIES) {
            pollErrorCount.current++;
            console.warn(`Job not found, retrying... (${pollErrorCount.current}/${MAX_POLL_RETRIES})`);
            timeoutId = setTimeout(poll, POLL_INTERVAL_MS) as unknown as number;
            return;
          }
          throw new Error(`Analysis failed or could not be found.`);
        }

        pollErrorCount.current = 0; // Reset error count on a successful status check
        const data: StatusResponse = await response.json();

        if (data.status === 'COMPLETED') {
          toast("Analysis complete! Fetching results...", 'success');
          const resultResponse = await fetch(`${API_BASE_URL}/analysis/${analysisId}`);
          if (!resultResponse.ok) throw new Error("Failed to fetch final results.");
          const resultData: AnalysisResult = await resultResponse.json();
          setAppState({ status: 'success', result: resultData });
        } else if (data.status === 'FAILED') {
          throw new Error(data.error || "Analysis failed on the server.");
        } else {
          // Status is PENDING or IN_PROGRESS, so poll again
          timeoutId = setTimeout(poll, POLL_INTERVAL_MS) as unknown as number;
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : "An unknown error occurred.";
        toast(message, 'error');
        setAppState({ status: 'error', message });
      }
    };

    poll(); // Start the polling loop

    return () => {
      isCancelled = true;
      clearTimeout(timeoutId);
    };
  }, [appState, setAppState, toast]);
};

function AppContent() {
  const [appState, setAppState] = useState<AppState>({ status: 'idle' });
  const { toast } = useToast();

  // Use the custom hook to handle all polling logic
  useAnalysisPoller(appState, setAppState);

  const handleUpload = async (file: File) => {    
    setAppState({ status: 'uploading' });
    toast("Uploading PGN file...", 'info');

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/analysis/`, { method: "POST", body: formData });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(errorData.detail || "Upload failed");
      }

      const data: { analysis_id: string } = await response.json();
      toast("Upload successful! Starting analysis...", 'success');
      setAppState({ status: 'polling', analysisId: data.analysis_id });
    } catch (error) {
      const message = error instanceof Error ? error.message : "An unknown upload error occurred.";
      console.error("Upload failed:", error);
      toast(message, 'error');
      setAppState({ status: 'error', message });
    }
  };

  const renderContent = () => {
    switch (appState.status) {
      case 'success':
        return <AnalysisView analysis={appState.result} onStartTraining={() => toast("Training Room Coming Soon!", 'info')} />;
      
      case 'uploading':
      case 'polling':
        return (
          <div className="flex flex-col items-center justify-center text-center p-8">
            <Loader2 className="w-12 h-12 text-cyan-400 animate-spin mb-4" />
            <h3 className="text-xl font-semibold text-white">Analysis in Progress</h3>
            <p className="text-zinc-400">
              {appState.status === 'uploading' ? 'Uploading file...' : 'Analyzing game...'}
            </p>
          </div>
        );

      case 'idle':
      case 'error': // On error, we allow the user to try again.
        return <UploadSection onUpload={handleUpload} isLoading={false} />;
    }
  };
  
  // Define custom styles
  const bgBackground = "bg-zinc-950";
  const textForeground = "text-white";
  const borderBorder = "border-zinc-800";

  return (
    <div className={`min-h-screen ${bgBackground} ${textForeground} font-sans`}>
      <header className={`p-4 border-b ${borderBorder}`}>
        <h1 className={`text-2xl font-bold text-center ${textForeground}`}>♟️ AI Chess Tutor</h1>
      </header>
      <main className="container mx-auto p-4 md:p-8">
        {renderContent()}
      </main>
    </div>
  );
}

// --- Default Export (Wraps App in Providers) ---
export default function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}