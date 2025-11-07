import { useState } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Lightbulb, RotateCcw, ArrowRight } from "lucide-react";
import { toast } from "sonner";

interface TrainingRoomProps {
  puzzleData: {
    fen: string;
    solution: string[];
    description: string;
  };
  onNextPuzzle: () => void;
}

export const TrainingRoom = ({ puzzleData, onNextPuzzle }: TrainingRoomProps) => {
  const [game, setGame] = useState(new Chess(puzzleData.fen));
  const [moveHistory, setMoveHistory] = useState<string[]>([]);

  const makeMove = (sourceSquare: string, targetSquare: string) => {
    try {
      const move = game.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: 'q',
      });

      if (move) {
        setMoveHistory([...moveHistory, move.san]);
        setGame(new Chess(game.fen()));
        toast.success("Good move! Keep going!");
        return true;
      }
    } catch (error) {
      toast.error("Illegal move. Try again!");
    }
    return false;
  };

  const resetPuzzle = () => {
    setGame(new Chess(puzzleData.fen));
    setMoveHistory([]);
    toast.info("Puzzle reset!");
  };

  const showHint = () => {
    if (puzzleData.solution.length > 0) {
      toast.info(`Hint: Try moving ${puzzleData.solution[0]}`);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">Training Room</h2>
        <div className="flex gap-2">
          <Button 
            onClick={showHint}
            variant="outline"
            className="border-accent/50 hover:bg-accent/10"
          >
            <Lightbulb className="w-4 h-4 mr-2" />
            Hint
          </Button>
          <Button 
            onClick={resetPuzzle}
            variant="outline"
            className="border-border hover:bg-muted"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="p-6 bg-gradient-board border-border shadow-card">
            <div className="max-w-[600px] mx-auto">
              <Chessboard />
            </div>
          </Card>
        </div>

        <div className="space-y-4">
          <Card className="p-6 bg-gradient-board border-border shadow-card">
            <h3 className="text-lg font-semibold text-foreground mb-3">Puzzle Goal</h3>
            <p className="text-muted-foreground">{puzzleData.description}</p>
          </Card>

          <Card className="p-6 bg-gradient-board border-border shadow-card">
            <h3 className="text-lg font-semibold text-foreground mb-3">Engine Analysis</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Evaluation:</span>
                <span className="text-accent font-bold">+1.2</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Best Move:</span>
                <span className="text-foreground font-mono">{puzzleData.solution[0]}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Depth:</span>
                <span className="text-foreground">20</span>
              </div>
            </div>
          </Card>

          <Card className="p-6 bg-gradient-board border-border shadow-card">
            <h3 className="text-lg font-semibold text-foreground mb-3">Your Moves</h3>
            <div className="space-y-1 max-h-[150px] overflow-y-auto">
              {moveHistory.length === 0 ? (
                <p className="text-muted-foreground text-sm">No moves yet</p>
              ) : (
                moveHistory.map((move, idx) => (
                  <div key={idx} className="text-sm">
                    <span className="text-muted-foreground">{idx + 1}.</span>{" "}
                    <span className="text-foreground font-mono">{move}</span>
                  </div>
                ))
              )}
            </div>
          </Card>

          <Button 
            onClick={onNextPuzzle}
            className="w-full bg-gradient-gold text-primary-foreground hover:opacity-90 transition-opacity"
          >
            Next Puzzle
            <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};
