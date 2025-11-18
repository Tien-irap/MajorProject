import React, { useMemo } from "react";
import { TrendingUp, AlertTriangle, Award, ArrowRight, BrainCircuit, Info } from "lucide-react";
import { Card, Button, Chessboard } from "./ui/stubs"; // Fixed path
import { WinProbabilityChart } from "./WinProbabilityChart"; // Adjusted path
import type { AnalysisResult } from "src/types"; // Adjusted path

interface AnalysisViewProps {
  analysis: AnalysisResult;
  onStartTraining: () => void;
}

export const AnalysisView = ({ analysis, onStartTraining }: AnalysisViewProps) => {
  const gameName = useMemo(() => 
    analysis.game_headers.Site || `${analysis.game_headers.White} vs ${analysis.game_headers.Black}`,
    [analysis.game_headers]
  );

  // Define custom styles
  const textForeground = "text-white";
  const gradientGold = "bg-gradient-to-r from-yellow-400 via-yellow-500 to-orange-500";
  const textPrimaryForeground = "text-black";
  const gradientBoard = "bg-zinc-900";
  const borderBorder = "border-zinc-800";
  const shadowCard = "shadow-xl";
  const textDestructive = "text-red-500";
  const bgPrimary50 = "bg-zinc-950";
  const borderDestructive20 = "border-red-500/20";
  const textMutedForeground = "text-zinc-500";
  const textAccent = "text-cyan-400";
  const textSuccess = "text-green-500";
  const borderSuccess20 = "border-green-500/20";

  const { mistakes, bestMoves } = useMemo(() => ({
    mistakes: analysis.key_move_summary.mistakes ?? [],
    bestMoves: analysis.key_move_summary.best_moves ?? [],
  }), [analysis.key_move_summary]);

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <h2 className={`text-2xl font-bold ${textForeground} truncate`}>Game Analysis: {gameName}</h2>
        <Button 
          onClick={onStartTraining}
          className={`${gradientGold} ${textPrimaryForeground} font-semibold hover:opacity-90 transition-opacity w-full sm:w-auto flex-shrink-0`}
        >
          Enter Training Room
          <ArrowRight className="ml-2 w-4 h-4" />
        </Button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card className={`p-4 sm:p-6 ${gradientBoard} ${borderBorder} ${shadowCard}`}>
          <h3 className={`text-lg font-semibold ${textForeground} mb-4 flex items-center gap-2`}>
            <AlertTriangle className={`w-5 h-5 ${textDestructive}`} />
            Key Mistakes
          </h3>
          <div className="space-y-3">
            {mistakes.length > 0 ? (
              mistakes.slice(0, 3).map((mistake) => (
                <div key={`mistake-${mistake.move_info.move_num}`} className={`p-4 ${bgPrimary50} rounded-lg ${borderDestructive20} border`}>
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className={`${textMutedForeground} text-sm`}>Move {mistake.move_info.move_num}</span>
                      <p className={`${textForeground} font-mono font-semibold`}>{mistake.move_info.move}</p>
                    </div>
                    <div className={`${textDestructive} font-bold`}>-{mistake.move_info.eval_diff} cp</div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 items-center">
                    <div className="col-span-1">
                      <Chessboard boardWidth={120} position={mistake.move_info.board_before_fen} />
                    </div>
                    <p className={`col-span-2 text-sm ${textMutedForeground} italic flex items-start gap-2`}><BrainCircuit className={`w-4 h-4 mt-1 ${textAccent} flex-shrink-0`} /> {mistake.explanation}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className={`flex flex-col items-center justify-center text-center p-4 ${textMutedForeground}`}>
                <Info className="w-8 h-8 mb-2" />
                <p className="font-semibold">No significant mistakes found.</p>
                <p className="text-sm">Well played!</p>
              </div>
            )}
          </div>
        </Card>

        <Card className={`p-4 sm:p-6 ${gradientBoard} ${borderBorder} ${shadowCard}`}>
          <h3 className={`text-lg font-semibold ${textForeground} mb-4 flex items-center gap-2`}>
            <Award className={`w-5 h-5 ${textSuccess}`} />
            Brilliant Moves
          </h3>
          <div className="space-y-3">
            {bestMoves.length > 0 ? (
              bestMoves.slice(0, 3).map((bestMove) => (
                <div key={`best-${bestMove.move_info.move_num}`} className={`p-4 ${bgPrimary50} rounded-lg ${borderSuccess20} border`}>
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className={`${textMutedForeground} text-sm`}>Move {bestMove.move_info.move_num}</span>
                      <p className={`${textForeground} font-mono font-semibold`}>{bestMove.move_info.move}</p>
                    </div>
                    <div className={`${textSuccess} font-bold`}>Best Move</div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 items-center">
                    <div className="col-span-1">
                      <Chessboard boardWidth={120} position={bestMove.move_info.board_before_fen} />
                    </div>
                    <p className={`col-span-2 text-sm ${textMutedForeground} italic flex items-start gap-2`}><BrainCircuit className={`w-4 h-4 mt-1 ${textAccent} flex-shrink-0`} /> {bestMove.explanation}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className={`flex flex-col items-center justify-center text-center p-4 ${textMutedForeground}`}>
                <Info className="w-8 h-8 mb-2" />
                <p className="font-semibold">No brilliant moves found.</p>
                <p className="text-sm">Keep looking for those winning ideas!</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      <Card className={`p-4 sm:p-6 ${gradientBoard} ${borderBorder} ${shadowCard}`}>
        <h3 className={`text-lg font-semibold ${textForeground} mb-4 flex items-center gap-2`}>
          <TrendingUp className={`w-5 h-5 ${textAccent}`} />
          Win Probability Over Time
        </h3>
        {analysis.move_by_move_analysis && analysis.move_by_move_analysis.length > 0 ? (
          <WinProbabilityChart analysisData={analysis.move_by_move_analysis} />
        ) : (
          <p className={textMutedForeground}>Win probability data is not available for this game.</p>
        )}
      </Card>
    </div>
  );
};