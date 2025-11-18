import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import type { MoveInfo } from "src/types"; // Import the shared type

const CP_CLAMP = 1500; // Max centipawn value to consider for probability
const CP_DIVISOR = 400; // Standard divisor for Elo/CP to probability conversion

interface WinProbabilityChartProps {
  analysisData: MoveInfo[];
}

export const WinProbabilityChart: React.FC<WinProbabilityChartProps> = ({ analysisData }) => {

  // Converts centipawn eval (from White's perspective) to a win probability percentage.
  const centipawnToWinProb = (cp: number) => {
    const clampedCp = Math.max(-CP_CLAMP, Math.min(CP_CLAMP, cp));
    const probability = 1 / (1 + Math.pow(10, -clampedCp / CP_DIVISOR));
    return probability * 100;
  };

  // Memoize chart data generation to prevent re-computation on every render.
  const chartData = React.useMemo(() => {
    // Determine the starting probability. Default to 50/50.
    const startProb = (analysisData.length > 0 && analysisData[0].eval_before !== undefined)
      ? centipawnToWinProb(analysisData[0].eval_before)
      : 50;
    
    const startPoint = { ply: 0, name: "Start", probability: startProb };
    
    const movePoints = analysisData.map((move, index) => ({
      ply: index + 1, // Ply is the half-move number
      name: `Move ${move.move_num} (${move.move})`,
      // Use eval_after for the state *after* the move was made
      probability: centipawnToWinProb(move.eval_after),
    }));
    
    return [startPoint, ...movePoints];
  }, [analysisData]);

  return (
    <div className="h-80 w-full" data-testid="win-probability-chart">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: -20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
          <XAxis 
            dataKey="ply"
            stroke="#a1a1aa" 
            fontSize={12} 
            tick={false} // Hide x-axis labels to keep it clean
            label={{ value: "Moves (Start to End)", position: "insideBottom", dy: 10, fill: "#a1a1aa" }}
          />
          <YAxis 
            stroke="#a1a1aa" 
            fontSize={12} 
            domain={[0, 100]} 
            tickFormatter={(value) => `${value}%`}
            label={{ value: "White's Win %", angle: -90, position: "insideLeft", dx: -10, fill: "#a1a1aa" }}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#18181b", border: "1px solid #3f3f46", borderRadius: "0.5rem" }}
            labelStyle={{ color: "#ffffff", fontWeight: "bold" }}
            itemStyle={{ color: "#06b6d4" }}
            formatter={(value: number) => [`${value.toFixed(1)}%`, "Win Rate"]}
          />
          <Line
            type="monotone"
            dataKey="probability"
            stroke="#06b6d4" // cyan-500
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 6, stroke: "#06b6d4", fill: "#06b6d4" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};