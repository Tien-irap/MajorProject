import React, { useEffect, useState } from "react";
import { Swords, TrendingUp, AlertTriangle } from "lucide-react";

interface ComparisonData {
  comparison: {
    metric: string;
    user: number;
    master: number;
    difference: number;
    percentage_diff: number;
  }[];
  summary: string;
}

interface MasterComparisonProps {
  analysisId: string;
  onBack?: () => void; // Optional onBack prop
}

const MasterComparison: React.FC<MasterComparisonProps> = ({ analysisId, onBack }) => {
  console.log("⚔️ MasterComparison Rendered. ID:", analysisId);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/analysis/${analysisId}/comparison`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch comparison data.");
        }
        const data = await response.json();
        setComparisonData(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, [analysisId]);

  if (loading) {
    return <div className="text-center text-zinc-400">Loading comparison...</div>;
  }

  if (error) {
    return <div className="text-center text-red-500">Error: {error}</div>;
  }

  if (!comparisonData) {
    return <div className="text-center text-zinc-400">No data available.</div>;
  }

  return (
    <div className="p-6 bg-zinc-950 text-zinc-200 min-h-screen">
      {/* Navigation */}
      {onBack && (
        <button
          onClick={onBack}
          className="mb-4 px-4 py-2 bg-zinc-800 text-zinc-200 rounded hover:bg-zinc-700"
        >
          Back to Dashboard
        </button>
      )}

      {/* Header */}
      <h1 className="text-3xl font-bold text-center mb-6 flex items-center justify-center gap-2">
        <Swords className="w-6 h-6 text-green-500" /> You vs. Grandmaster
      </h1>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {comparisonData.comparison.map((metric) => (
          <div
            key={metric.metric}
            className="p-4 bg-zinc-900 rounded shadow-md border border-zinc-800"
          >
            <h2 className="text-xl font-semibold mb-2 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-400" /> {metric.metric}
            </h2>
            <div className="mb-2">
              <div className="flex justify-between text-sm text-zinc-400">
                <span>Master: {metric.master}</span>
                <span>{metric.master}</span>
              </div>
              <div className="w-full bg-zinc-800 rounded h-4">
                <div
                  className="bg-green-500 h-4 rounded"
                  style={{ width: `${metric.master}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm text-zinc-400">
                <span>You: {metric.user}</span>
                <span>{metric.user}</span>
              </div>
              <div className="w-full bg-zinc-800 rounded h-4">
                <div
                  className={`h-4 rounded ${
                    metric.user > metric.master ? "bg-red-500" : "bg-blue-500"
                  }`}
                  style={{ width: `${metric.user}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Verdict Section */}
      <div className="mt-8 p-4 bg-zinc-900 rounded shadow-md border border-zinc-800">
        <h2 className="text-xl font-semibold mb-2 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-yellow-400" /> Verdict
        </h2>
        <blockquote className="text-zinc-400 italic">{comparisonData.summary}</blockquote>
      </div>
    </div>
  );
};

export default MasterComparison;