import React from "react";
import { Book } from "lucide-react";
// Changed from relative path to alias path for better resolution
import { Card, SimpleAccordionItem } from "@/components/ui/stubs";

const chessRules = [
  {
    title: "Basic Piece Movements",
    content: "Pawns move forward one square, two on first move. Rooks move horizontally/vertically. Bishops move diagonally. Knights move in L-shape. Queen moves in any direction. King moves one square in any direction."
  },
  {
    title: "Special Moves",
    content: "Castling: King and rook move simultaneously for protection. En Passant: Special pawn capture. Pawn Promotion: Transform pawn reaching opposite end into any piece (usually queen)."
  },
  {
    title: "Check and Checkmate",
    content: "Check: King is under attack. Must be resolved immediately. Checkmate: King is in check with no legal moves to escape. This ends the game."
  },
  {
    title: "Opening Principles",
    content: "Control the center with pawns and pieces. Develop knights and bishops early. Castle early for king safety. Don't move the same piece twice in opening. Connect your rooks."
  },
  {
    title: "Middle Game Strategy",
    content: "Look for tactical opportunities (pins, forks, skewers). Improve piece positions. Control key squares. Create threats. Watch for opponent's plans."
  },
  {
    title: "Endgame Fundamentals",
    content: "Activate your king. Push passed pawns. Use opposition. Know basic checkmates (queen+king, rook+king). Coordinate pieces for maximum effect."
  }
];

export const RuleBook = () => {
  // Styles matching your theme
  const textForeground = "text-white";
  const textAccent = "text-cyan-400";
  const bgGradient = "bg-zinc-900";
  const borderBorder = "border-zinc-800";

  return (
    <Card className={`p-6 ${bgGradient} ${borderBorder} shadow-xl`}>
      <h3 className={`text-xl font-semibold ${textForeground} mb-4 flex items-center gap-2`}>
        <Book className={`w-5 h-5 ${textAccent}`} />
        Chess Rule Book
      </h3>
      <div className="w-full">
        {chessRules.map((rule, index) => (
          <SimpleAccordionItem key={index} title={rule.title} content={rule.content} />
        ))}
      </div>
    </Card>
  );
};