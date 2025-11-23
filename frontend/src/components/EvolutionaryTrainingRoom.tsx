import { useState, useEffect } from "react";
import { EvolutionaryPuzzleCard } from "./EvolutionaryPuzzleCard";
import { Button, Card } from "./ui/stubs";
import { ArrowLeft, Loader2, Dna, Brain, Trophy, TrendingUp } from "lucide-react";
import type { PuzzleDB, SubmitPuzzleResult } from "../types";

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
  const [completedPuzzles, setCompletedPuzzles] = useState<Set<string>>(new Set());
  const [performance, setPerformance] = useState<{
    correct: number;
    total: number;
    avgTime: number;
  }>({ correct: 0, total: 0, avgTime: 0 });

  const handlePuzzleComplete = async (puzzleId: string, timeSeconds: number, isCorrect: boolean) => {
    // Mark as completed
    setCompletedPuzzles(prev => new Set(prev).add(puzzleId));

    // Update performance stats
    setPerformance(prev => ({
      correct: prev.correct + (isCorrect ? 1 : 0),
      total: prev.total + 1,
      avgTime: (prev.avgTime * prev.total + timeSeconds) / (prev.total + 1),
    }));

    // Submit to backend
    try {
      await onSubmitResult({
        puzzle_id: puzzleId,
        user_id: "demo_user", // TODO: Replace with actual user ID from auth
        is_correct: isCorrect,
        time_taken_seconds: timeSeconds,
      });
    } catch (error) {
      console.error("Failed to submit result:", error);
    }
  };

  // Styling
  const textForeground = "text-white";
  const textMuted = "text-zinc-400";
  const gradientBoard = "bg-zinc-900";
  const borderBorder = "border-zinc-800";
  const textAccent = "text-cyan-400";
  const gradientGold = "bg-gradient-to-r from-yellow-400 via-yellow-500 to-orange-500";
  const textPrimaryForeground = "text-black";

  if (isLoading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4 animate-in fade-in duration-500">
        <Loader2 className="w-16 h-16 text-cyan-400 animate-spin" />
        <h3 className="text-2xl font-bold text-white">Evolving Your Puzzles...</h3>
        <p className="text-zinc-400 max-w-md text-center">
          Our genetic algorithm is mutating the position to create tactical variations.
        </p>
      </div>
    );
  }

  if (!puzzles || puzzles.length === 0) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <div className="p-6 bg-red-500/10 rounded-full mb-4">
          <Brain className="w-16 h-16 text-red-400" />
        </div>
        <h3 className="text-2xl font-bold text-white">No Puzzles Generated</h3>
        <p className="text-zinc-400 max-w-md text-center">
          We couldn't generate tactical variations from your position. This might happen if the position is too simple or already solved.
        </p>
        <Button onClick={onBack} className="mt-4 bg-zinc-800 hover:bg-zinc-700 text-zinc-300">
          <ArrowLeft className="w-4 h-4 mr-2" /> Go Back
        </Button>
      </div>
    );
  }

  // Separate seed from mutations
  const seedPuzzle = puzzles.find(p => p.generator_type === "seed");
  const mutatedPuzzles = puzzles.filter(p => p.generator_type === "evolutionary");

  const allCompleted = completedPuzzles.size === puzzles.length;
  const accuracy = performance.total > 0 
    ? Math.round((performance.correct / performance.total) * 100) 
    : 0;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button 
            onClick={onBack} 
            className="bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Analysis
          </Button>
          <div>
            <h2 className={`text-3xl font-bold ${textForeground} flex items-center gap-3`}>
              <Dna className="w-8 h-8 text-purple-500" />
              Evo-Chess Training Lab
            </h2>
            <p className={`${textMuted} mt-1`}>
              Train pattern recognition through evolutionary variations
            </p>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <Card className={`p-6 ${gradientBoard} ${borderBorder} border shadow-xl`}>
        <div className="flex items-start gap-4">
          <div className="p-3 bg-purple-500/10 rounded-full flex-shrink-0">
            <Brain className="w-8 h-8 text-purple-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white mb-2">How It Works</h3>
            <p className={`${textMuted} leading-relaxed mb-3`}>
              Each puzzle below was generated using a <strong>Genetic Algorithm</strong>. 
              The first card shows your original mistake. The subsequent cards are <strong>tactical mutations</strong> 
              — mirrored or shifted variations that preserve the core pattern but change the geometry.
            </p>
            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span className={textMuted}><strong>Seed:</strong> Your actual mistake</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span className={textMuted}><strong>Mutations:</strong> Evolved variations</span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Performance Stats */}
      {performance.total > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className={`p-4 ${gradientBoard} ${borderBorder} border shadow-lg`}>
            <div className="flex items-center gap-3">
              <Trophy className="w-8 h-8 text-yellow-500" />
              <div>
                <p className="text-xs text-zinc-500 uppercase font-semibold">Accuracy</p>
                <p className="text-2xl font-bold text-white">{accuracy}%</p>
              </div>
            </div>
          </Card>
          
          <Card className={`p-4 ${gradientBoard} ${borderBorder} border shadow-lg`}>
            <div className="flex items-center gap-3">
              <TrendingUp className="w-8 h-8 text-cyan-500" />
              <div>
                <p className="text-xs text-zinc-500 uppercase font-semibold">Solved</p>
                <p className="text-2xl font-bold text-white">
                  {performance.correct}/{performance.total}
                </p>
              </div>
            </div>
          </Card>
          
          <Card className={`p-4 ${gradientBoard} ${borderBorder} border shadow-lg`}>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/10 rounded-full">
                <Dna className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <p className="text-xs text-zinc-500 uppercase font-semibold">Avg. Time</p>
                <p className="text-2xl font-bold text-white">{performance.avgTime.toFixed(1)}s</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Seed Puzzle Section */}
      {seedPuzzle && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <div className="h-[2px] flex-grow bg-gradient-to-r from-red-500/50 to-transparent"></div>
            <h3 className="text-lg font-bold text-red-400 uppercase tracking-wider">
              Phase 1: The Original Mistake
            </h3>
            <div className="h-[2px] flex-grow bg-gradient-to-l from-red-500/50 to-transparent"></div>
          </div>
          <div className="max-w-2xl mx-auto">
            <EvolutionaryPuzzleCard
              puzzle={seedPuzzle}
              onComplete={(time, correct) => handlePuzzleComplete(seedPuzzle._id, time, correct)}
              cardNumber={1}
            />
          </div>
        </div>
      )}

      {/* Mutated Puzzles Section */}
      {mutatedPuzzles.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <div className="h-[2px] flex-grow bg-gradient-to-r from-purple-500/50 to-transparent"></div>
            <h3 className="text-lg font-bold text-purple-400 uppercase tracking-wider">
              Phase 2: Evolutionary Variations
            </h3>
            <div className="h-[2px] flex-grow bg-gradient-to-l from-purple-500/50 to-transparent"></div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {mutatedPuzzles.map((puzzle, idx) => (
              <EvolutionaryPuzzleCard
                key={puzzle._id}
                puzzle={puzzle}
                onComplete={(time, correct) => handlePuzzleComplete(puzzle._id, time, correct)}
                cardNumber={idx + 2}
              />
            ))}
          </div>
        </div>
      )}

      {/* Completion Banner */}
      {allCompleted && (
        <Card className={`p-8 ${gradientBoard} ${borderBorder} border-2 shadow-2xl text-center animate-in zoom-in-95 duration-300`}>
          <div className="flex flex-col items-center gap-4">
            <div className={`p-6 rounded-full ${gradientGold}`}>
              <Trophy className="w-16 h-16 text-black" />
            </div>
            <h3 className="text-3xl font-bold text-white">Training Complete! 🎉</h3>
            <p className={`${textMuted} max-w-md text-lg`}>
              You've successfully completed all evolutionary variations. 
              Your pattern recognition skills just leveled up!
            </p>
            <div className="flex gap-4 mt-4">
              <Button 
                onClick={onBack}
                className={`${gradientGold} ${textPrimaryForeground} font-semibold hover:opacity-90 transition-opacity px-8 py-6 text-lg`}
              >
                Return to Analysis
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
