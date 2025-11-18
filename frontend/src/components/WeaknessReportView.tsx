import React from "react";
import { Target, ArrowLeft, BrainCircuit, Info, Zap, AlertTriangle } from "lucide-react";
import { Card, Button, Chessboard } from "./ui/stubs"; 
import type { AnalysisResult, MoveAnalysis } from "../types"; 

interface WeaknessReportProps {
  analysis: AnalysisResult;
  onBack: () => void;
}

/**
 * Helper to find the board FEN for a specific move UCI.
 * We want the board state *before* the mistake was made to show the context.
 */
const getBoardFenForMove = (
  analysisData: MoveAnalysis[], 
  moveUci: string
): string | undefined => {
  // Find the move object that matches the UCI string (e.g., "e2e4")
  const moveData = analysisData.find(m => m.move === moveUci);
  
  // Return the FEN string representing the board before this move was played
  return moveData ? moveData.board_before_fen : undefined;
};

export const WeaknessReport = ({ analysis, onBack }: WeaknessReportProps) => {
  const report = analysis.weakness_report;
  const analysisData = analysis.move_by_move_analysis;
  
  // Convert dictionary to array for mapping
  const weaknessItems = report ? Object.entries(report) : [];

  // --- Styles ---
  const textForeground = "text-white";
  const textMuted = "text-zinc-400";
  // A subtle red gradient to indicate "danger/weakness" zones
  const gradientRed = "bg-gradient-to-br from-red-950/40 via-zinc-900 to-zinc-900";
  const borderRed = "border-red-500/20";

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      
      {/* --- Header Section --- */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button 
            onClick={onBack} 
            className="bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Back
          </Button>
          <h2 className={`text-2xl font-bold ${textForeground} flex items-center gap-2`}>
            <Target className="w-6 h-6 text-red-500" />
            Strategic Weakness Report
          </h2>
        </div>
      </div>

      {/* --- Intro Card --- */}
      <Card className="p-6 bg-zinc-900/80 border border-zinc-800 shadow-lg backdrop-blur-sm">
        <div className="flex gap-4 items-start">
          <div className="p-3 bg-blue-500/10 rounded-full h-fit flex-shrink-0">
            <BrainCircuit className="w-8 h-8 text-blue-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">How the AI Coach analyzed this</h3>
            <p className={`${textMuted} leading-relaxed max-w-3xl`}>
              Instead of just looking at individual blunders, we used <strong>K-Means Clustering</strong> to group your mistakes by game phase, complexity, and evaluation loss. 
              The AI then identified recurring <strong>strategic patterns</strong> in your play. Fixing these patterns is the fastest way to improve your rating.
            </p>
          </div>
        </div>
      </Card>

      {/* --- Weakness Cards Loop --- */}
      <div className="grid grid-cols-1 gap-8">
        {weaknessItems.length > 0 ? (
          weaknessItems.map(([key, content], index) => {
            // 1. Extract the first example move UCI
            const exampleMoveUci = content.example_moves?.[0];
            // 2. Find the corresponding FEN from the full game analysis
            const exampleFen = exampleMoveUci ? getBoardFenForMove(analysisData, exampleMoveUci) : undefined;
            
            return (
              <Card key={key} className={`overflow-hidden border ${borderRed} ${gradientRed} shadow-xl`}>
                <div className="p-6 md:p-8 flex flex-col lg:flex-row gap-8">
                  
                  {/* Left Column: Text & Diagnosis */}
                  <div className="flex-1 space-y-5">
                    <div className="flex items-center gap-3">
                      <span className="px-3 py-1 bg-red-500/10 text-red-400 text-xs font-mono font-bold rounded-full border border-red-500/20 uppercase tracking-wider">
                        Pattern #{index + 1}
                      </span>
                      <h3 className="text-2xl font-bold text-white leading-tight">
                        {content.global_pattern_name}
                      </h3>
                    </div>
                    
                    {/* Coach's Diagnosis Box */}
                    <div className="bg-black/40 p-5 rounded-xl border border-zinc-800/50 relative">
                      <div className="absolute top-4 left-4">
                         <Zap className="w-5 h-5 text-yellow-500" />
                      </div>
                      <div className="pl-8">
                        <h4 className="text-sm font-bold text-yellow-500 uppercase tracking-wide mb-2">Coach's Diagnosis</h4>
                        <p className="text-zinc-200 text-base leading-relaxed italic">
                          "{content.llm_explanation}"
                        </p>
                      </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 gap-4 pt-2">
                      <div className="bg-zinc-900/50 p-3 rounded-lg border border-zinc-800">
                        <p className="text-xs text-zinc-500 uppercase">Mistake Frequency</p>
                        <p className="text-xl font-mono font-bold text-white mt-1">
                          {content.num_mistakes} <span className="text-sm text-zinc-600 font-normal">times</span>
                        </p>
                      </div>
                      <div className="bg-zinc-900/50 p-3 rounded-lg border border-zinc-800">
                         <p className="text-xs text-zinc-500 uppercase">Avg. Severity</p>
                         <p className="text-xl font-mono font-bold text-red-400 mt-1">
                           -{Math.round(content.avg_centipawn_loss)} <span className="text-sm text-zinc-600 font-normal">cp</span>
                         </p>
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Visual Example */}
                  <div className="flex-shrink-0 w-full lg:w-80 flex flex-col items-center">
                     <div className="w-full flex items-center justify-between mb-2 text-xs text-zinc-500 uppercase tracking-wider font-semibold">
                        <span>Example Scenario</span>
                        <span>Move {exampleMoveUci || "?"}</span>
                     </div>
                     
                     {exampleFen ? (
                       <div className="rounded-lg overflow-hidden shadow-2xl border-4 border-zinc-800 bg-zinc-800 w-full max-w-[320px]">
                          <Chessboard 
                            boardWidth={320} 
                            position={exampleFen} 
                            // Optional: Add arrows or highlights if your library supports it
                          />
                       </div>
                     ) : (
                       <div className="w-full h-64 bg-zinc-800/50 rounded-lg flex flex-col items-center justify-center text-zinc-500 border border-zinc-700/50">
                            <AlertTriangle className="w-8 h-8 mb-2 opacity-50" />
                            <span className="text-sm">Board state unavailable</span>
                       </div>
                     )}
                     
                     <p className="mt-3 text-xs text-zinc-500 text-center max-w-[280px]">
                       This position led to a significant drop in your evaluation.
                     </p>
                  </div>

                </div>
              </Card>
            );
          })
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-zinc-500 bg-zinc-900/30 rounded-xl border border-zinc-800 border-dashed">
            <Info className="w-12 h-12 mb-4 opacity-40" />
            <h3 className="text-lg font-semibold text-zinc-300">No Patterns Detected</h3>
            <p className="max-w-md text-center mt-2">
              Your game didn't show enough clustered mistakes to form a specific strategic weakness profile. That's actually good news!
            </p>
          </div>
        )}
      </div>
    </div>
  );
};