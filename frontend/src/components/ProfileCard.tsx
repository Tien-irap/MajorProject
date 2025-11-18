import React from "react";
import { Trophy, TrendingUp } from "lucide-react";
// Changed from relative path to alias path for better resolution
import { Card } from "@/components/ui/stubs";

interface ProfileStats {
  gamesWon: number;
  gamesLost: number;
  rank: string;
  rating: number;
}

interface ProfileCardProps {
  stats: ProfileStats;
}

export const ProfileCard = ({ stats }: ProfileCardProps) => {
  const totalGames = stats.gamesWon + stats.gamesLost;
  const winRate = totalGames > 0 ? ((stats.gamesWon / totalGames) * 100).toFixed(1) : "0";

  // Styles
  const textForeground = "text-white";
  const textMutedForeground = "text-zinc-400";
  const borderBorder = "border-zinc-800";
  const bgGradient = "bg-zinc-900"; // Simplified gradient
  const textAccent = "text-cyan-400";
  const textSuccess = "text-green-500";
  const textDestructive = "text-red-500";

  return (
    <Card className={`p-6 ${bgGradient} ${borderBorder} shadow-xl`}>
      <h3 className={`text-xl font-semibold ${textForeground} mb-4 flex items-center gap-2`}>
        <Trophy className={`w-5 h-5 ${textAccent}`} />
        Your Profile
      </h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className={textMutedForeground}>Rating</span>
          <span className={`text-2xl font-bold ${textAccent}`}>{stats.rating}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className={textMutedForeground}>Rank</span>
          <span className={`text-lg font-semibold ${textForeground}`}>{stats.rank}</span>
        </div>
        <div className={`h-px bg-zinc-800 my-3`} />
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className={`text-2xl font-bold ${textSuccess}`}>{stats.gamesWon}</div>
            <div className={`text-xs ${textMutedForeground}`}>Wins</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${textDestructive}`}>{stats.gamesLost}</div>
            <div className={`text-xs ${textMutedForeground}`}>Losses</div>
          </div>
        </div>
        <div className="flex items-center justify-between pt-2">
          <span className={`text-sm ${textMutedForeground} flex items-center gap-1`}>
            <TrendingUp className="w-4 h-4" />
            Win Rate
          </span>
          <span className={`text-lg font-semibold ${textAccent}`}>{winRate}%</span>
        </div>
      </div>
    </Card>
  );
};