import { TrendingUp, AlertTriangle, Award, ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { WinProbabilityChart } from "./WinProbabilityChart";

interface Move {
  moveNumber: number;
  move: string;
  evaluation: number;
  isTopMove?: boolean;
  isMistake?: boolean;
}

interface AnalysisViewProps {
  gameName: string;
  topMoves: Move[];
  mistakes: Move[];
  onStartTraining: () => void;
}

export const AnalysisView = ({ gameName, topMoves, mistakes, onStartTraining }: AnalysisViewProps) => {
  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">Game Analysis: {gameName}</h2>
        <Button 
          onClick={onStartTraining}
          className="bg-gradient-gold text-primary-foreground hover:opacity-90 transition-opacity"
        >
          Start Training
          <ArrowRight className="ml-2 w-4 h-4" />
        </Button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card className="p-6 bg-gradient-board border-border shadow-card">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-success" />
            Top Best Moves
          </h3>
          <div className="space-y-3">
            {topMoves.map((move, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-primary/50 rounded-lg border border-success/20">
                <div>
                  <span className="text-muted-foreground text-sm">Move {move.moveNumber}</span>
                  <p className="text-foreground font-mono font-semibold">{move.move}</p>
                </div>
                <div className="text-success font-bold">+{move.evaluation.toFixed(1)}</div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6 bg-gradient-board border-border shadow-card">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-destructive" />
            Top Mistakes
          </h3>
          <div className="space-y-3">
            {mistakes.map((move, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-primary/50 rounded-lg border border-destructive/20">
                <div>
                  <span className="text-muted-foreground text-sm">Move {move.moveNumber}</span>
                  <p className="text-foreground font-mono font-semibold">{move.move}</p>
                </div>
                <div className="text-destructive font-bold">{move.evaluation.toFixed(1)}</div>
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
        <WinProbabilityChart />
      </Card>
    </div>
  );
};
