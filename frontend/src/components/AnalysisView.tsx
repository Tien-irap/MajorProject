import React, { useMemo } from "react";
import { TrendingUp, AlertTriangle, Award, ArrowRight, BrainCircuit, Info } from "lucide-react";
import { Card, Button, Chessboard } from "./ui/stubs";
import { WinProbabilityChart } from "./WinProbabilityChart";
import type { AnalysisResult } from "src/types";

interface AnalysisViewProps {
  analysis: AnalysisResult;
  onStartTraining: () => void;
}

export const AnalysisView = ({ analysis, onStartTraining }: AnalysisViewProps) => {
  console.log("DEBUG ANALYSIS:", analysis);

  const gameName = useMemo(() => 
    analysis.game_headers.Site || `${analysis.game_headers.White} vs ${analysis.game_headers.Black}`,
    [analysis.game_headers]
  );

  const { mistakes, bestMoves } = useMemo(() => {
    const keyMoveSummary = analysis.key_move_summary || {};
    let mistakes = keyMoveSummary.mistakes || [];
    let bestMoves = keyMoveSummary.best_moves || [];

    if (mistakes.length === 0) {
      console.log("Fallback: Generating mistakes list on client-side.");
      mistakes = (analysis.move_by_move_analysis || []).filter((m) => {
        const label = m.analysis.toLowerCase();
        return label === "mistake" || label === "blunder";
      }).map((m, i) => ({
        move_info: {
          move_num: Math.floor(i / 2) + 1,
          move: m.move_san,
          eval_diff: m.score_differential,
          board_before_fen: m.fen,
        },
        explanation: `Evaluation changed by ${m.score_differential} points.`
      }));
    }

    if (bestMoves.length === 0) {
      console.log("Fallback: Generating brilliant moves list on client-side.");
      bestMoves = (analysis.move_by_move_analysis || []).filter((m) => {
        const label = m.analysis.toLowerCase();
        return label === "brilliant" || label === "best" || label === "great";
      }).map((m, i) => ({
        move_info: {
          move_num: Math.floor(i / 2) + 1,
          move: m.move_san,
          eval_diff: m.score_differential,
          board_before_fen: m.fen,
        },
        explanation: `Evaluation changed by ${m.score_differential} points.`
      }));
    }

    return { mistakes, bestMoves };
  }, [analysis.key_move_summary, analysis.move_by_move_analysis]);

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <h2 className="text-2xl font-bold text-white truncate">Game Analysis: {gameName}</h2>
        <Button 
          onClick={onStartTraining}
          className="bg-gradient-to-r from-yellow-400 via-yellow-500 to-orange-500 text-black font-semibold hover:opacity-90 transition-opacity w-full sm:w-auto flex-shrink-0"
        >
          Enter Training Room
          <ArrowRight className="ml-2 w-4 h-4" />
        </Button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card className="p-4 sm:p-6 bg-zinc-900 border-zinc-800 shadow-xl">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            Key Mistakes
          </h3>
          <div className="space-y-3">
            {mistakes.length > 0 ? (
              mistakes.slice(0, 3).map((mistake) => (
                <div key={`mistake-${mistake.move_info.move_num}`} className="p-4 bg-zinc-950 rounded-lg border-red-500/20 border">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="text-zinc-500 text-sm">Move {mistake.move_info.move_num}</span>
                      <p className="text-white font-mono font-semibold">{mistake.move_info.move}</p>
                    </div>
                    <div className="text-red-500 font-bold">-{mistake.move_info.eval_diff} cp</div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 items-center">
                    <div className="col-span-1">
                      <Chessboard boardWidth={120} position={mistake.move_info.board_before_fen} />
                    </div>
                    <p className="col-span-2 text-sm text-zinc-500 italic flex items-start gap-2">
                      <BrainCircuit className="w-4 h-4 mt-1 text-cyan-400 flex-shrink-0" /> {mistake.explanation}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center text-center p-4 text-zinc-500">
                <Info className="w-8 h-8 mb-2" />
                <p className="font-semibold">No significant mistakes found.</p>
                <p className="text-sm">Well played!</p>
              </div>
            )}
          </div>
        </Card>

        <Card className="p-4 sm:p-6 bg-zinc-900 border-zinc-800 shadow-xl">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-green-500" />
            Brilliant Moves
          </h3>
          <div className="space-y-3">
            {bestMoves.length > 0 ? (
              bestMoves.slice(0, 3).map((bestMove) => (
                <div key={`best-${bestMove.move_info.move_num}`} className="p-4 bg-zinc-950 rounded-lg border-green-500/20 border">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="text-zinc-500 text-sm">Move {bestMove.move_info.move_num}</span>
                      <p className="text-white font-mono font-semibold">{bestMove.move_info.move}</p>
                    </div>
                    <div className="text-green-500 font-bold">Best Move</div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 items-center">
                    <div className="col-span-1">
                      <Chessboard boardWidth={120} position={bestMove.move_info.board_before_fen} />
                    </div>
                    <p className="col-span-2 text-sm text-zinc-500 italic flex items-start gap-2">
                      <BrainCircuit className="w-4 h-4 mt-1 text-cyan-400 flex-shrink-0" /> {bestMove.explanation}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center text-center p-4 text-zinc-500">
                <Info className="w-8 h-8 mb-2" />
                <p className="font-semibold">No brilliant moves found.</p>
                <p className="text-sm">Keep looking for those winning ideas!</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      <Card className="p-4 sm:p-6 bg-zinc-900 border-zinc-800 shadow-xl">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-cyan-400" />
          Win Probability Over Time
        </h3>
        {analysis.move_by_move_analysis && analysis.move_by_move_analysis.length > 0 ? (
          <WinProbabilityChart analysisData={analysis.move_by_move_analysis} />
        ) : (
          <p className="text-zinc-500">Win probability data is not available for this game.</p>
        )}
      </Card>
    </div>
  );
};