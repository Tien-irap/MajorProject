import { useState, useEffect } from "react";
import { UploadSection } from "./components/UploadSection";
import { AnalysisView } from "./components/AnalysisView";
import { Toaster, toast } from "sonner";
import { Loader2 } from "lucide-react";

// Define the structure of the final analysis result
interface AnalysisResult {
  game_headers: { [key: string]: string };
  key_move_summary: {
    mistakes: any[]; // Using 'any' for simplicity, can be typed further
    best_moves: any[];
  };
  move_by_move_analysis: any[];
}

// Define the structure of the status response
interface StatusResponse {
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  error?: string;
}

const API_BASE_URL = "http://localhost:8000"; // Your FastAPI backend URL

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [pollingStatus, setPollingStatus] = useState("");

  // This effect handles the polling logic
  useEffect(() => {
    if (!analysisId) return;

    const poll = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/status`);
        if (!response.ok) {
          throw new Error("Failed to get status. Please try again.");
        }
        const data: StatusResponse = await response.json();

        setPollingStatus(`Status: ${data.status}...`);

        if (data.status === "COMPLETED") {
          // Analysis is done, fetch the full result
          toast.success("Analysis complete! Fetching results...");
          const resultResponse = await fetch(`${API_BASE_URL}/analysis/${analysisId}`);
          const resultData: AnalysisResult = await resultResponse.json();
          setAnalysisResult(resultData);
          setAnalysisId(null); // Stop polling
          setIsLoading(false);
        } else if (data.status === "FAILED") {
          toast.error(`Analysis failed: ${data.error || "Unknown error"}`);
          setAnalysisId(null); // Stop polling
          setIsLoading(false);
        }
      } catch (error) {
        console.error("Polling error:", error);
        toast.error("An error occurred while checking status.");
        setAnalysisId(null);
        setIsLoading(false);
      }
    };

    const intervalId = setInterval(poll, 3000); // Poll every 3 seconds

    return () => clearInterval(intervalId); // Cleanup on component unmount
  }, [analysisId]);

  const handleUpload = async (file: File) => {
    setIsLoading(true);
    setAnalysisResult(null); // Reset previous results
    toast.info("Uploading PGN file...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/analysis/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Upload failed");
      }

      const data = await response.json();
      toast.success("Upload successful! Starting analysis...");
      setAnalysisId(data.analysis_id); // Start polling by setting the ID
    } catch (error) {
      console.error("Upload failed:", error);
      toast.error(`Upload failed: ${error instanceof Error ? error.message : "Unknown error"}`);
      setIsLoading(false);
    }
  };

  const renderContent = () => {
    if (analysisResult) {
      return <AnalysisView analysis={analysisResult} onStartTraining={() => alert("Navigate to training room!")} />;
    }
    if (isLoading || analysisId) {
      return (
        <div className="flex flex-col items-center justify-center text-center p-8">
          <Loader2 className="w-12 h-12 text-accent animate-spin mb-4" />
          <h3 className="text-xl font-semibold">Analysis in Progress</h3>
          <p className="text-muted-foreground">{pollingStatus || "Please wait..."}</p>
        </div>
      );
    }
    return <UploadSection onUpload={handleUpload} isLoading={isLoading} />;
  };

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      <Toaster position="top-center" richColors />
      <header className="p-4 border-b border-border">
        <h1 className="text-2xl font-bold text-center">♟️ AI Chess Tutor</h1>
      </header>
      <main className="container mx-auto p-4 md:p-8">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;