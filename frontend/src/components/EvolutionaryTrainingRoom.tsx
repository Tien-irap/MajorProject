"use client";

import { useState } from "react";
import { EvolutionaryPuzzleCard } from "./EvolutionaryPuzzleCard";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ArrowLeft, Loader2, Trophy, ArrowRight, Brain } from "lucide-react";
import type { PuzzleDB, SubmitPuzzleResult } from "@/types";

interface EvolutionaryTrainingRoomProps {
  puzzles: PuzzleDB[];
  onBack: () => void;
  onSubmitResult: (result: SubmitPuzzleResult) => Promise<void>;
  isLoading: boolean;
}

export const EvolutionaryTrainingRoom = ({
  puzzles,
  onBack,
  onSubmitResult,
  isLoading,
}: EvolutionaryTrainingRoomProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSessionComplete, setIsSessionComplete] = useState(false);
  const [results, setResults] = useState<{id: string, time: number, correct: boolean}[]>([]);

  // 1. Loading State
  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-6 animate-in fade-in duration-500">
        <div className="relative">
          <Loader2 className="w-16 h-16 text-cyan-500 animate-spin" />
          <div className="absolute inset-0 blur-xl bg-cyan-500/20 rounded-full" />
        </div>
        <div className="text-center space-y-2">
          <h3 className="text-2xl font-bold text-white">Evolving Puzzles...</h3>
          <p className="text-zinc-400">Applying genetic mutations to your position</p>
        </div>
      </div>
    );
  }

  // 2. Empty State
  if (!puzzles || puzzles.length === 0) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-6 text-center">
        <div className="p-6 bg-red-500/10 rounded-full border border-red-500/20">
          <Trophy className="w-12 h-12 text-red-400" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-white">No Puzzles Generated</h3>
          <p className="text-zinc-400 mt-2 max-w-md mx-auto">
            This position might be too simple or ambiguous for our evolutionary engine.
          </p>
        </div>
        <Button onClick={onBack} variant="secondary">
          <ArrowLeft className="w-4 h-4 mr-2" /> Return to Analysis
        </Button>
      </div>
    );
  }

  // 3. Completion State (Summary)
  if (isSessionComplete) {
    const accuracy = Math.round((results.filter(r => r.correct).length / results.length) * 100);
    
    return (
      <div className="max-w-md mx-auto text-center space-y-8 animate-in zoom-in-95 duration-500 mt-10">
        <div className="relative w-24 h-24 mx-auto">
          <div className="absolute inset-0 bg-green-500/20 blur-xl rounded-full" />
          <div className="relative bg-zinc-900 border-2 border-green-500/50 rounded-full w-full h-full flex items-center justify-center">
            <Trophy className="w-10 h-10 text-green-400" />
          </div>
        </div>
        
        <div className="space-y-2">
          <h2 className="text-3xl font-bold text-white">Training Complete!</h2>
          <p className="text-zinc-400">Evolutionary session finished with <span className="text-green-400 font-bold">{accuracy}%</span> accuracy.</p>
        </div>
        
        <div className="bg-zinc-900/50 rounded-xl border border-zinc-800 p-1 divide-y divide-zinc-800/50">
          {results.map((res, idx) => (
            <div key={idx} className="flex justify-between items-center p-3 text-sm">
              <span className="text-zinc-500 font-medium">Puzzle {idx + 1}</span>
              <span className={res.correct ? "text-green-400 font-mono" : "text-red-400 font-mono"}>
                {res.correct ? "Solved" : "Missed"} ({res.time.toFixed(1)}s)
              </span>
            </div>
          ))}
        </div>

        <Button onClick={onBack} className="w-full bg-white text-black hover:bg-zinc-200" size="lg">
          Return to Analysis
        </Button>
      </div>
    );
  }

  // 4. Active Puzzle Logic
  const currentPuzzle = puzzles[currentIndex];
  // Logic: First puzzle is ALWAYS Phase 1, rest are Phase 2
  const isPhase1 = currentIndex === 0;
  
  const phaseLabel = isPhase1 ? "Phase 1: Original Mistake" : "Phase 2: Evolved Variation";
  const phaseColor = isPhase1 ? "text-red-400" : "text-purple-400";
  const phaseBg = isPhase1 ? "bg-red-500/10 border-red-500/20" : "bg-purple-500/10 border-purple-500/20";

  const handlePuzzleComplete = async (timeTaken: number, isCorrect: boolean) => {
    // 1. Submit to Backend
    try {
      await onSubmitResult({
        puzzle_id: currentPuzzle._id,
        user_id: "demo_user", 
        is_correct: isCorrect,
        time_taken_seconds: timeTaken,
      });
    } catch (error) {
      console.error("Failed to submit result:", error);
    }

    // 2. Local State Update
    setResults(prev => [...prev, {
      id: currentPuzzle._id,
      time: timeTaken,
      correct: isCorrect
    }]);

    // 3. Advance to next puzzle after short delay
    setTimeout(() => {
      if (currentIndex < puzzles.length - 1) {
        setCurrentIndex(prev => prev + 1);
      } else {
        setIsSessionComplete(true);
      }
    }, 1500);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Navigation & Progress */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Button 
            variant="ghost" 
            onClick={onBack} 
            className="text-zinc-500 hover:text-white pl-0"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Back
          </Button>
          
          <div className="flex gap-1.5">
            {puzzles.map((_, idx) => (
              <div 
                key={idx} 
                className={`h-1.5 w-8 rounded-full transition-all duration-300 ${
                  idx === currentIndex 
                    ? (isPhase1 ? 'bg-red-500 w-12' : 'bg-purple-500 w-12') 
                    : idx < currentIndex ? 'bg-green-500' : 'bg-zinc-800'
                }`} 
              />
            ))}
          </div>
        </div>

        {/* Phase Indicator */}
        <div className={`flex items-center justify-center gap-3 py-2 px-6 rounded-full border w-fit mx-auto transition-colors duration-500 ${phaseBg}`}>
           <span className={`text-sm font-bold tracking-wide uppercase flex items-center gap-2 ${phaseColor}`}>
             {isPhase1 ? <ArrowLeft className="w-4 h-4 rotate-[-45deg]" /> : <ArrowRight className="w-4 h-4" />}
             {phaseLabel}
           </span>
        </div>
      </div>

      {/* Info Banner */}
      <Card className="p-6 bg-zinc-900 border border-zinc-800 shadow-xl max-w-[600px] mx-auto hidden md:block animate-in fade-in slide-in-from-top-4">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-purple-500/10 rounded-full flex-shrink-0">
            <Brain className="w-8 h-8 text-purple-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-2">How It Works</h3>
            <p className="text-zinc-400 text-sm leading-relaxed mb-3">
              Each puzzle below was generated using a <strong>Genetic Algorithm</strong>. 
              The first card shows your original mistake. The subsequent cards are <strong>tactical mutations</strong> 
              — mirrored or shifted variations that preserve the core pattern but change the geometry.
            </p>
            <div className="flex flex-wrap gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span className="text-zinc-500"><strong>Seed:</strong> Your actual mistake</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span className="text-zinc-500"><strong>Mutations:</strong> Evolved variations</span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Active Card Area */}
      <div className="flex justify-center min-h-[550px] items-start">
        {/* Increased max-w to 600px to accommodate larger board */}
        <div className="w-full max-w-[600px] animate-in slide-in-from-bottom-4 duration-500 fade-in">
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
