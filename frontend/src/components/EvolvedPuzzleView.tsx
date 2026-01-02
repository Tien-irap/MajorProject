"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowLeft, CheckCircle2, Trophy, ArrowRight } from "lucide-react";
import { EvolutionaryPuzzleCard } from "./EvolutionaryPuzzleCard";
import type { PuzzleDB } from "@/types";

interface EvolvedPuzzleViewProps {
  puzzles: PuzzleDB[];
  onBackToAnalysis: () => void;
}

export const EvolvedPuzzleView = ({ puzzles, onBackToAnalysis }: EvolvedPuzzleViewProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSessionComplete, setIsSessionComplete] = useState(false);
  const [results, setResults] = useState<{id: string, time: number, correct: boolean}[]>([]);

  // Safety Check
  if (!puzzles || puzzles.length === 0) {
    return <div className="text-center p-8 text-muted-foreground">No puzzles generated.</div>;
  }

  const currentPuzzle = puzzles[currentIndex];
  
  // Logic: Index 0 is ALWAYS Phase 1 (Seed), everything else is Phase 2
  const isPhase1 = currentIndex === 0;
  
  const phaseLabel = isPhase1 ? "Phase 1: Original Mistake" : "Phase 2: Evolved Variation";
  const phaseColor = isPhase1 ? "text-red-400" : "text-purple-400";
  const phaseBg = isPhase1 ? "bg-red-500/10 border-red-500/20" : "bg-purple-500/10 border-purple-500/20";

  // Handle Card Completion
  const handlePuzzleComplete = (timeTaken: number, isCorrect: boolean) => {
    setResults(prev => [...prev, {
      id: currentPuzzle._id,
      time: timeTaken,
      correct: isCorrect
    }]);

    // Delay transition slightly to allow user to see the "Success" animation
    setTimeout(() => {
      if (currentIndex < puzzles.length - 1) {
        setCurrentIndex(prev => prev + 1);
      } else {
        setIsSessionComplete(true);
      }
    }, 1500);
  };

  // Session Complete View
  if (isSessionComplete) {
    return (
      <div className="max-w-md mx-auto text-center space-y-6 animate-in zoom-in-95 duration-500 mt-10">
        <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto border border-green-500/30">
          <Trophy className="w-10 h-10 text-green-400" />
        </div>
        <h2 className="text-3xl font-bold text-foreground">Training Complete!</h2>
        <p className="text-muted-foreground">You've successfully analyzed your mistake and practiced the variations.</p>
        
        <div className="bg-zinc-900 rounded-lg p-4 space-y-2 border border-zinc-800 text-left">
          {results.map((res, idx) => (
            <div key={idx} className="flex justify-between text-sm items-center border-b border-zinc-800 last:border-0 pb-2 last:pb-0 mb-2 last:mb-0">
              <span className="text-zinc-500 flex items-center gap-2">
                 <span className="bg-zinc-800 w-6 h-6 rounded-full flex items-center justify-center text-xs">{idx + 1}</span>
                 {idx === 0 ? "Original" : "Mutation"}
              </span>
              <span className={res.correct ? "text-green-400 font-mono" : "text-red-400 font-mono"}>
                {res.correct ? "Solved" : "Missed"} ({res.time.toFixed(1)}s)
              </span>
            </div>
          ))}
        </div>

        <Button onClick={onBackToAnalysis} className="w-full" size="lg">
          Return to Game Analysis
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Top Navigation / Progress Bar */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Button 
            variant="ghost" 
            onClick={onBackToAnalysis} 
            className="text-muted-foreground hover:text-foreground pl-0"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Back
          </Button>
          
          <div className="flex gap-1.5">
            {puzzles.map((_, idx) => (
              <div 
                key={idx} 
                className={`h-2 w-12 rounded-full transition-all duration-500 ${
                  idx === currentIndex ? (isPhase1 ? 'bg-red-500 shadow-lg shadow-red-500/50' : 'bg-purple-500 shadow-lg shadow-purple-500/50') : 
                  idx < currentIndex ? 'bg-green-500' : 'bg-zinc-800'
                }`} 
              />
            ))}
          </div>
        </div>

        {/* Phase Indicator Pill */}
        <div className={`flex items-center justify-center gap-2 py-2 px-6 rounded-full border w-fit mx-auto transition-colors duration-500 ${phaseBg}`}>
           {isPhase1 ? <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" /> : <div className="w-2 h-2 rounded-full bg-purple-500" />}
           <span className={`text-sm font-bold tracking-wide uppercase ${phaseColor}`}>
             {phaseLabel}
           </span>
        </div>
      </div>

      {/* Single Active Card Container */}
      <div className="flex justify-center min-h-[600px] items-start">
        <div className="w-full max-w-[500px] animate-in slide-in-from-bottom-4 duration-500 fade-in">
          {/* Key is CRITICAL here: Changing the key forces React to destroy the old card 
              and create a brand new one, resetting the timer and board state completely. */}
          <EvolutionaryPuzzleCard 
            key={currentPuzzle._id || currentIndex}
            puzzle={currentPuzzle}
            cardNumber={currentIndex + 1}
            totalCards={puzzles.length}
            onComplete={handlePuzzleComplete}
          />
        </div>
      </div>
    </div>
  );
};