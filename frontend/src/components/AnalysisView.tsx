import { TrendingUp, AlertTriangle, Award, ArrowRight, BrainCircuit } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { WinProbabilityChart } from "./WinProbabilityChart";
import { Chessboard } from "react-chessboard";

// --- Updated Interfaces to match Backend API Response ---

interface MoveInfo {
  move_num: number;
  move: string;
  eval_diff: number;
  classification: string;
}

interface KeyMove {
  move_info: MoveInfo;
  board_before_fen: string;
  explanation: string;
}

interface MoveByMoveAnalysis {
  move_num: number;
  win_prob_after: number;
}

interface AnalysisResult {
  game_headers: { [key: string]: string };
  key_move_summary: {
    mistakes: KeyMove[];
    best_moves: KeyMove[];
  };
  move_by_move_analysis: MoveByMoveAnalysis[];
}

interface AnalysisViewProps {
  analysis: AnalysisResult;
  onStartTraining: () => void;
}

export const AnalysisView = ({ analysis, onStartTraining }: AnalysisViewProps) => {
  const gameName = analysis.game_headers.Site || `${analysis.game_headers.White} vs ${analysis.game_headers.Black}`;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">Game Analysis: {gameName}</h2>
        <Button 
          onClick={onStartTraining}
          className="bg-gradient-gold text-primary-foreground hover:opacity-90 transition-opacity"
        >
          Enter Training Room
          <ArrowRight className="ml-2 w-4 h-4" />
        </Button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card className="p-6 bg-gradient-board border-border shadow-card">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-destructive" />
            Key Mistakes
          </h3>
          <div className="space-y-3">
            {(analysis.key_move_summary.mistakes ?? []).slice(0, 3).map((mistake, idx) => (
              <div key={idx} className="p-4 bg-primary/50 rounded-lg border border-destructive/20">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="text-muted-foreground text-sm">Move {mistake.move_info.move_num}</span>
                    <p className="text-foreground font-mono font-semibold">{mistake.move_info.move}</p>
                  </div>
                  <div className="text-destructive font-bold">-{mistake.move_info.eval_diff} cp</div>
                </div>
                <div className="grid grid-cols-3 gap-4 items-center">
                  <div className="col-span-1">
                    <Chessboard boardWidth={120} arePiecesDraggable={false} position={mistake.board_before_fen} />
                  </div>
                  <p className="col-span-2 text-sm text-muted-foreground italic flex items-start gap-2"><BrainCircuit className="w-4 h-4 mt-1 text-accent flex-shrink-0" /> {mistake.explanation}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6 bg-gradient-board border-border shadow-card">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-success" />
            Brilliant Moves
          </h3>
          <div className="space-y-3">
            {(analysis.key_move_summary.best_moves ?? []).slice(0, 3).map((bestMove, idx) => (
              <div key={idx} className="p-4 bg-primary/50 rounded-lg border border-success/20">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="text-muted-foreground text-sm">Move {bestMove.move_info.move_num}</span>
                    <p className="text-foreground font-mono font-semibold">{bestMove.move_info.move}</p>
                  </div>
                  <div className="text-success font-bold">Best Move</div>
                </div>
                <div className="grid grid-cols-3 gap-4 items-center">
                  <div className="col-span-1">
                    <Chessboard boardWidth={120} arePiecesDraggable={false} position={bestMove.board_before_fen} />
                  </div>
                  <p className="col-span-2 text-sm text-muted-foreground italic flex items-start gap-2"><BrainCircuit className="w-4 h-4 mt-1 text-accent flex-shrink-0" /> {bestMove.explanation}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card className="p-6 bg-gradient-board border-border shadow-card">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-accent" />
          Win Probability Over Time
        </h3>
        <WinProbabilityChart analysisData={analysis.move_by_move_analysis} />
      </Card>
    </div>
  );
};
