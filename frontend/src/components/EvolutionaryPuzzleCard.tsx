import { useState, useEffect } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import { Card } from "./ui/stubs";
import { Check, X, Clock, Zap, Target, Dna } from "lucide-react";
import type { PuzzleDB } from "../types";

interface EvolutionaryPuzzleCardProps {
  puzzle: PuzzleDB;
  onComplete: (timeSeconds: number, isCorrect: boolean) => void;
  cardNumber: number;
}

export const EvolutionaryPuzzleCard = ({ 
  puzzle, 
  onComplete, 
  cardNumber 
}: EvolutionaryPuzzleCardProps) => {
  const [game, setGame] = useState<Chess>(new Chess(puzzle.fen));
  const [moveHistory, setMoveHistory] = useState<string[]>([]);
  const [startTime] = useState<number>(Date.now());
  const [isSolved, setIsSolved] = useState(false);
  const [isWrong, setIsWrong] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Timer
  useEffect(() => {
    if (isSolved || isWrong) return;
    
    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime, isSolved, isWrong]);

  const onDrop = (sourceSquare: string, targetSquare: string): boolean => {
    if (isSolved || isWrong) return false;

    try {
      const gameCopy = new Chess(game.fen());
      const move = gameCopy.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: "q",
      });

      if (!move) return false;

      // Build UCI string from the move
      const moveUci = `${sourceSquare}${targetSquare}${move.promotion ? move.promotion : ""}`;
      setMoveHistory([...moveHistory, move.san]);
      setGame(gameCopy);

      // Check if it's the correct first move (solution is in UCI format from backend)
      const expectedMove = puzzle.solution[0];
      
      // Normalize comparison - remove any promotion symbols for matching
      const normalizedUserMove = moveUci.toLowerCase();
      const normalizedExpected = expectedMove.toLowerCase();
      
      console.log("User move:", normalizedUserMove, "Expected:", normalizedExpected);
      
      if (normalizedUserMove === normalizedExpected) {
        // Correct!
        setIsSolved(true);
        const timeTaken = (Date.now() - startTime) / 1000;
        setTimeout(() => onComplete(timeTaken, true), 800);
      } else {
        // Wrong move - show feedback but don't complete yet
        setIsWrong(true);
        setTimeout(() => {
          setIsWrong(false);
          // Reset the board after a delay
          setGame(new Chess(puzzle.fen));
          setMoveHistory([]);
        }, 1500);
      }

      return true;
    } catch (error) {
      return false;
    }
  };

  // Styling
  const textForeground = "text-white";
  const textMuted = "text-zinc-400";
  const gradientBoard = "bg-zinc-900";
  const borderBorder = "border-zinc-800";
  const textAccent = "text-cyan-400";
  const textSuccess = "text-green-500";
  const textDestructive = "text-red-500";
  const bgSuccess = "bg-green-500/10";
  const bgDestructive = "bg-red-500/10";
  const borderSuccess = "border-green-500/20";
  const borderDestructive = "border-red-500/20";

  // Theme-based icons
  const getThemeIcon = () => {
    if (puzzle.theme.includes("Original") || puzzle.generator_type === "seed") {
      return <Target className="w-5 h-5 text-red-400" />;
    }
    return <Dna className="w-5 h-5 text-purple-400" />;
  };

  const getThemeColor = () => {
    if (puzzle.theme.includes("Original") || puzzle.generator_type === "seed") {
      return "from-red-500/10 via-zinc-900 to-zinc-900";
    }
    return "from-purple-500/10 via-zinc-900 to-zinc-900";
  };

  return (
    <Card 
      className={`p-6 bg-gradient-to-br ${getThemeColor()} ${borderBorder} border-2 shadow-xl transition-all duration-300 ${
        isSolved ? `${borderSuccess} scale-105` : isWrong ? `${borderDestructive} scale-95` : ""
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 ${puzzle.generator_type === "seed" ? "bg-red-500/20 text-red-400" : "bg-purple-500/20 text-purple-400"} text-xs font-bold rounded-full uppercase tracking-wider flex items-center gap-1.5`}>
            {getThemeIcon()}
            Card {cardNumber}
          </span>
          <h3 className={`text-lg font-bold ${textForeground}`}>{puzzle.theme}</h3>
        </div>
        
        <div className="flex items-center gap-2 text-sm">
          {isSolved ? (
            <div className={`flex items-center gap-1.5 px-3 py-1.5 ${bgSuccess} rounded-full ${borderSuccess} border`}>
              <Check className={`w-4 h-4 ${textSuccess}`} />
              <span className={textSuccess}>Solved!</span>
            </div>
          ) : isWrong ? (
            <div className={`flex items-center gap-1.5 px-3 py-1.5 ${bgDestructive} rounded-full ${borderDestructive} border`}>
              <X className={`w-4 h-4 ${textDestructive}`} />
              <span className={textDestructive}>Try Again</span>
            </div>
          ) : (
            <div className={`flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800/50 rounded-full ${textMuted}`}>
              <Clock className="w-4 h-4" />
              <span className="font-mono">{elapsedTime}s</span>
            </div>
          )}
        </div>
      </div>

      {/* Chessboard */}
      <div className="mb-4 rounded-lg overflow-hidden border-4 border-zinc-800 shadow-2xl">
        <Chessboard
          position={game.fen()}
          onPieceDrop={onDrop}
          boardWidth={380}
          arePiecesDraggable={!isSolved && !isWrong}
          customBoardStyle={{
            borderRadius: "4px",
          }}
        />
      </div>

      {/* Info Section */}
      <div className="space-y-3">
        <div className={`p-3 bg-black/40 rounded-lg border ${borderBorder}`}>
          <div className="flex items-start gap-2">
            <Zap className={`w-4 h-4 mt-0.5 ${textAccent}`} />
            <div className="flex-1">
              <p className="text-xs text-zinc-500 uppercase font-semibold mb-1">Your Task</p>
              <p className={`text-sm ${textForeground}`}>
                {puzzle.generator_type === "seed" 
                  ? "This is the exact position where you made a mistake. Find the winning move!"
                  : "Recognize the tactical pattern in this evolved variation. The geometry has changed, but the core tactic remains."}
              </p>
            </div>
          </div>
        </div>

        {/* Show hint after wrong move */}
        {isWrong && (
          <div className={`p-3 ${bgDestructive} rounded-lg border ${borderDestructive} animate-in fade-in duration-300`}>
            <p className="text-xs text-red-400 uppercase font-semibold mb-1">Hint</p>
            <p className={`text-sm ${textDestructive}`}>
              Not quite! The best move starts from {puzzle.solution[0].substring(0, 2)}...
            </p>
          </div>
        )}

        {moveHistory.length > 0 && !isWrong && (
          <div className={`p-3 bg-zinc-800/50 rounded-lg border ${borderBorder}`}>
            <p className="text-xs text-zinc-500 uppercase font-semibold mb-1">Your Moves</p>
            <div className="flex flex-wrap gap-2">
              {moveHistory.map((move, idx) => (
                <span key={idx} className={`px-2 py-1 bg-zinc-900 rounded text-xs font-mono ${textForeground}`}>
                  {idx + 1}. {move}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Debug info - remove this later */}
        {process.env.NODE_ENV === 'development' && (
          <div className="p-2 bg-yellow-900/20 rounded text-xs text-yellow-500 border border-yellow-500/20">
            <strong>Debug:</strong> Expected move (UCI): {puzzle.solution[0]}
          </div>
        )}
      </div>
    </Card>
  );
};
