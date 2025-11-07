import { Trophy, TrendingUp, Target } from "lucide-react";
import { Card } from "@/components/ui/card";

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

  return (
    <Card className="p-6 bg-gradient-board border-border shadow-card">
      <h3 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
        <Trophy className="w-5 h-5 text-accent" />
        Your Profile
      </h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Rating</span>
          <span className="text-2xl font-bold text-accent">{stats.rating}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Rank</span>
          <span className="text-lg font-semibold text-foreground">{stats.rank}</span>
        </div>
        <div className="h-px bg-border my-3" />
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-success">{stats.gamesWon}</div>
            <div className="text-xs text-muted-foreground">Wins</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-destructive">{stats.gamesLost}</div>
            <div className="text-xs text-muted-foreground">Losses</div>
          </div>
        </div>
        <div className="flex items-center justify-between pt-2">
          <span className="text-sm text-muted-foreground flex items-center gap-1">
            <TrendingUp className="w-4 h-4" />
            Win Rate
          </span>
          <span className="text-lg font-semibold text-accent">{winRate}%</span>
        </div>
      </div>
    </Card>
  );
};
