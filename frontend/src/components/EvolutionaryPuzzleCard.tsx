"use client";

import { useState, useEffect } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import { Card } from "@/components/ui/card";
import { Check, X, Clock, Zap, Target, Dna, Eye, EyeOff, ChevronDown, ChevronUp } from "lucide-react";
import type { PuzzleDB } from "@/types";

interface EvolutionaryPuzzleCardProps {
  puzzle: PuzzleDB;
  onComplete: (timeSeconds: number, isCorrect: boolean) => void;
  cardNumber: number;
  totalCards: number;
}

export const EvolutionaryPuzzleCard = ({ 
  puzzle, 
  onComplete, 
  cardNumber,
  totalCards
}: EvolutionaryPuzzleCardProps) => {
  // Initialize game state safely
  const [game, setGame] = useState<Chess>(new Chess(puzzle.fen));
  const [moveHistory, setMoveHistory] = useState<string[]>([]);
  const [startTime] = useState<number>(Date.now());
  const [isSolved, setIsSolved] = useState(false);
  const [isWrong, setIsWrong] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  
  // State for answer reveal
  const [isAnswerVisible, setIsAnswerVisible] = useState(false);

  // Timer effect
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

      const moveUci = `${sourceSquare}${targetSquare}${move.promotion ? move.promotion : ""}`;
      setMoveHistory([...moveHistory, move.san]);
      setGame(gameCopy);

      const expectedMove = puzzle.solution && puzzle.solution.length > 0 ? puzzle.solution[0] : puzzle.best_move;
      const normalizedUserMove = moveUci.toLowerCase();
      const normalizedExpected = expectedMove?.toLowerCase() || "";
      
      if (normalizedUserMove === normalizedExpected) {
        setIsSolved(true);
        const timeTaken = (Date.now() - startTime) / 1000;
        setTimeout(() => onComplete(timeTaken, true), 800);
      } else {
        setIsWrong(true);
        setTimeout(() => {
          setIsWrong(false);
          setGame(new Chess(puzzle.fen)); 
          setMoveHistory([]);
        }, 1500);
      }
      return true;
    } catch (error) {
      return false;
    }
  };

  const isPhase1 = puzzle.is_parent;
  
  const getThemeIcon = () => {
    if (isPhase1) return <Target className="w-5 h-5 text-red-400" />;
    return <Dna className="w-5 h-5 text-purple-400" />;
  };

  const getThemeGradient = () => {
    if (isPhase1) return "from-red-500/10 via-zinc-900 to-zinc-900 border-red-500/20";
    return "from-purple-500/10 via-zinc-900 to-zinc-900 border-purple-500/20";
  };

  const borderColor = isSolved 
    ? "border-green-500" 
    : isWrong 
      ? "border-red-500" 
      : isPhase1 ? "border-red-500/30" : "border-purple-500/30";

  return (
    <Card 
      className={`p-6 bg-gradient-to-br ${getThemeGradient()} border-2 shadow-2xl transition-all duration-300 ${
        isSolved ? "scale-105 border-green-500/50" : isWrong ? "shake border-red-500/50" : ""
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 ${isPhase1 ? "bg-red-500/20 text-red-400" : "bg-purple-500/20 text-purple-400"} text-xs font-bold rounded-full uppercase tracking-wider flex items-center gap-2`}>
            {getThemeIcon()}
            <span>Card {cardNumber} <span className="opacity-50">/ {totalCards}</span></span>
          </span>
        </div>
        
        <div className="flex items-center gap-2 text-sm">
          {isSolved ? (
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 rounded-full border border-green-500/30 animate-in fade-in">
              <Check className="w-4 h-4 text-green-500" />
              <span className="text-green-500 font-bold">Solved!</span>
            </div>
          ) : isWrong ? (
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/20 rounded-full border border-red-500/30 animate-in fade-in">
              <X className="w-4 h-4 text-red-500" />
              <span className="text-red-500 font-bold">Try Again</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800 rounded-full text-zinc-400 border border-zinc-700">
              <Clock className="w-4 h-4" />
              <span className="font-mono font-medium w-8 text-center">{elapsedTime}s</span>
            </div>
          )}
        </div>
      </div>

      {/* Chessboard - Broadened display, removed overflow-hidden for promotion dialog */}
      <div className={`mb-6 rounded-lg border-4 shadow-black/50 shadow-lg transition-colors duration-300 ${borderColor}`}>
        <Chessboard
          position={game.fen()}
          onPieceDrop={onDrop}
          boardWidth={520}
          arePiecesDraggable={!isSolved && !isWrong}
          customDarkSquareStyle={{ backgroundColor: isPhase1 ? '#451a1a' : '#261a45' }}
          customLightSquareStyle={{ backgroundColor: isPhase1 ? '#f0d9b5' : '#e0c2f2' }}
          animationDuration={200}
        />
      </div>

      {/* Info Section */}
      <div className="space-y-4">
        {isWrong && (
          <div className="p-3 bg-red-500/10 rounded-lg border border-red-500/20 animate-in slide-in-from-top-2 fade-in">
            <p className="text-sm font-medium text-red-400 flex items-center gap-2">
              <X className="w-4 h-4" />
              Incorrect move. The tactic failed!
            </p>
          </div>
        )}

        {/* Task Description */}
        <div className="p-4 bg-zinc-950/50 rounded-lg border border-zinc-800">
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-md ${isPhase1 ? 'bg-red-500/10' : 'bg-purple-500/10'}`}>
               <Zap className={`w-5 h-5 ${isPhase1 ? 'text-red-400' : 'text-purple-400'}`} />
            </div>
            <div className="flex-1">
              <p className="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Mission</p>
              <p className="text-sm text-zinc-200 leading-relaxed">
                {isPhase1 
                  ? "This is the exact position where you made a mistake. Find the winning move!"
                  : "Recognize the tactical pattern in this evolved variation. The geometry has changed, but the core tactic remains."}
              </p>
            </div>
          </div>
        </div>

        {/* Answer Dropdown */}
        <div className="border border-zinc-800 rounded-lg overflow-hidden">
          <button 
            onClick={() => setIsAnswerVisible(!isAnswerVisible)}
            className="w-full flex items-center justify-between p-3 bg-zinc-900 hover:bg-zinc-800 transition-colors text-xs font-medium text-zinc-400 hover:text-zinc-200"
          >
            <span className="flex items-center gap-2">
              {isAnswerVisible ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
              {isAnswerVisible ? "Hide Answer" : "Stuck? Reveal Answer"}
            </span>
            {isAnswerVisible ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          
          {isAnswerVisible && (
             <div className="p-3 bg-black/40 border-t border-zinc-800 animate-in slide-in-from-top-1">
                <p className="text-sm text-center">
                  The best move is <span className="font-bold text-white bg-zinc-700 px-2 py-0.5 rounded ml-1">{puzzle.best_move}</span>
                </p>
             </div>
          )}
        </div>
      </div>
    </Card>
  );
};