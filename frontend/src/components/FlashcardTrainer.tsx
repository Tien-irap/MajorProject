import { useState } from "react";
import { Button } from "./ui/stubs";
import { Brain } from "lucide-react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";

type Flashcard = {
  id: string;
  name: string;
  theme: string;
  sideToMove: "White" | "Black";
  prompt: string;
  answer: string;
  fen: string;
};

const DEMO_CARDS: Flashcard[] = [
  {
    id: "fork-1",
    name: "Knight Fork",
    theme: "Fork",
    sideToMove: "White",
    prompt:
      "White to move. You have a knight near the enemy king and queen. Can you jump with tempo to attack both?",
    answer:
      "Your knight can hop forward and give check to the king while also threatening the queen. This is called a 'fork' — one move attacking two valuable pieces.",
    fen: "r1bqkb1r/pppp1ppp/2n5/4p3/3P4/2N2N2/PPP1PPPP/R1BQKB1R w KQkq - 0 1", // Nf6+ attacks the Queen on d8 and King on e8
  },
  {
    id: "pin-1",
    name: "Pin on the file",
    theme: "Pin",
    sideToMove: "Black",
    prompt:
      "Black to move. One of White’s pieces is pinned against the king on the same file. How can you increase the pressure?",
    answer:
      "The stuck piece is 'pinned' — it cannot move without putting the king in danger. Bring another attacker (like your rook) to build up pressure until the pinned piece falls.",
    fen: "r1bqk2r/ppp2ppp/2n2n2/4p3/3P4/2N2N2/PPP1BPPP/R1BQK2R b kq - 0 1", // The pawn on d4 is pinned against Kg1 by the Queen on d8
  },
  {
    id: "lpdo-1",
    name: "Loose Piece Drop Off",
    theme: "Loose Piece",
    sideToMove: "White",
    prompt:
      "White to move. One of Black’s pieces is completely undefended. Can you create a simple tactic that wins it?",
    answer:
      "Always look for pieces that are not protected. When you spot one, see if you can capture it safely, add attackers, or give a threat that wins it next move.",
    fen: "r1bqkb1r/pppp1ppp/2n5/4p3/3P4/2N1P3/PPP2PPP/R1BQKB1R w KQkq - 0 1", // White can play dxe5, attacking the undefended pawn on e5
  },
  {
    id: "fork-2",
    name: "Knight Double Attack",
    theme: "Fork",
    sideToMove: "White",
    prompt:
      "Your knight can jump into the center and attack two pieces at the same time. Look for a square where the knight attacks both the king and something valuable.",
    answer:
      "Knights are best at forking. The pattern is noticing when two enemy pieces sit far from each other but both can be hit by a knight move.",
    fen: "r1bqk2r/ppp2ppp/2n5/4p3/3P4/5N2/PPP1PPPP/R1BQKB1R w KQkq - 0 1", // White plays Nf6, forking the Queen on d8 and Rook on h8
  },
  {
    id: "pin-2",
    name: "Pin Against the King",
    theme: "Pin",
    sideToMove: "White",
    prompt:
      "One of the enemy knights cannot move because the king is behind it. How can you add pressure to the pinned piece?",
    answer:
      "When a piece is stuck in front of its king, adding attackers builds pressure until it collapses. This is the key idea of a pin.",
    fen: "r2qk2r/ppp2ppp/2n2n2/4p3/3P4/2N1PN2/PPP2PPP/R1BQKB1R w KQ - 0 1", // White plays Bb5, pinning the Nc6 against the King on e8
  },
  {
    id: "lp-2",
    name: "Hanging Bishop",
    theme: "Loose Piece",
    sideToMove: "Black",
    prompt:
      "White has a piece that is completely unprotected. Can you capture it safely?",
    answer:
      "Look for pieces with no defenders. These are the easiest targets in chess and often lead to free material.",
    fen: "rnbqkbnr/ppp2ppp/3p4/4p3/3P4/2N5/PPP1PPPP/R1BQKBNR b KQkq - 0 1", // Black plays ...exd4, capturing the undefended pawn
  },
  {
    id: "br-1",
    name: "Back Rank Danger",
    theme: "Checkmate Threat",
    sideToMove: "White",
    prompt:
      "Black’s king is trapped behind its pawns. If your rook can get to the back rank with check, it could be checkmate.",
    answer:
      "Back-rank mates happen when the king has no escape squares. Always watch the last row if it is blocked by pawns.",
    fen: "r4rk1/pbp1qppp/1p1p1n2/4p3/1PP1P3/3P4/PB2BPPP/R2Q1RK1 w - - 0 1", // Sets up a common Back Rank theme for White to exploit
  },
  {
    id: "discover-1",
    name: "Discover the Attack",
    theme: "Discovered Attack",
    sideToMove: "White",
    prompt:
      "One of your pieces is in front of a stronger piece. If the front piece moves, a surprise attack opens up.",
    answer:
      "A discovered attack works because the enemy cannot stop both threats at once.",
    fen: "rnbqkbnr/pppp1ppp/8/4p3/3P4/3BPN2/PPP2PPP/RNBQK2R w KQkq - 0 1", // White plays dxe5, discovering the attack by the Bishop on d3 to Nf6
  },
  {
    id: "remove-1",
    name: "Remove the Guard",
    theme: "Removing Defender",
    sideToMove: "Black",
    prompt:
      "One of White’s pieces is protecting something important. If you can remove that defending piece, the target becomes vulnerable.",
    answer:
      "Often a simple exchange removes the only defender of a key square or piece, making the rest of the tactic work.",
    fen: "r2qkb1r/ppp2ppp/2n2n2/3p4/3P4/2N1BN2/PPP2PPP/R2QKB1R b KQkq - 0 1", // Black plays ...Ng4, attacking the Be3, which defends the pawn on d4
  },
  {
    id: "overload-1",
    name: "Too Many Jobs",
    theme: "Overloading",
    sideToMove: "White",
    prompt:
      "A single black piece is trying to defend two things at once. Can you force it to fail one of its duties?",
    answer:
      "Overloading happens when one defender cannot protect everything. You attack something it defends, and it becomes overwhelmed.",
    fen: "r2qkb1r/ppp2ppp/2n2n2/4p3/3P4/2N1PN2/PPP2PPP/R1BQ1RK1 w kq - 0 1", // White plays Bb5, attacking the Nc6 which is overloaded defending e5 and itself
  },
  {
    id: "deflect-1",
    name: "Pull the Defender Away",
    theme: "Deflection",
    sideToMove: "Black",
    prompt:
      "White has a piece guarding an important square. Can you lure it away so that the square becomes weak?",
    answer:
      "Deflection works by forcing a defending piece to move to a different square, which leaves something unprotected.",
    fen: "r1bqkb1r/ppp2ppp/2n2n2/4p3/3P4/2N1PN2/PPP1BPPP/R1BQ1RK1 b kq - 0 1", // Black plays ...Ne4, deflecting the Bishop on e2 from protecting the Queen on d1
  },
  {
    id: "zwischen-1",
    name: "The Surprise Move",
    theme: "In-Between Move",
    sideToMove: "White",
    prompt:
      "Instead of immediately recapturing, you can play a surprising move that forces your opponent to respond first.",
    answer:
      "Zwischenzug works when your in-between threat is stronger than their original attack.",
    fen: "rnbqk2r/ppp2ppp/5n2/8/3p4/2N2N2/PPP1PPPP/R1BQKB1R w KQkq - 0 1", // White plays e4, creating a counter-threat before recapturing the piece on d4
  },
  {
    id: "mate-net-1",
    name: "Closing the Net",
    theme: "Mate Pattern",
    sideToMove: "White",
    prompt:
      "Black’s king has limited space. You can combine checks to trap it in a corner.",
    answer:
      "A checkmate net is created when the king's escape squares are controlled and every forcing move pushes it closer to mate.",
    fen: "r1bq1rk1/ppp2ppp/5n2/4p3/3P4/1QN1PN2/PP3PPP/R1B2RK1 w - - 0 0", // Sets up a common Kingside attack position where a Mate Net can be forced
  }
];

export function FlashcardTrainer() {
  const [cards] = useState<Flashcard[]>(DEMO_CARDS);
  const [index, setIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);

  const current = cards[index];

  const goNext = () => {
    setShowAnswer(false);
    setIndex((prev) => (prev + 1) % cards.length);
  };

  const goPrev = () => {
    setShowAnswer(false);
    setIndex((prev) => (prev - 1 + cards.length) % cards.length);
  };

  return (
    <div className="border border-zinc-800 bg-zinc-900 rounded-xl p-6 shadow-lg space-y-4">
      {/* HEADER */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-cyan-500/10 rounded-full">
            <Brain className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">Tactical Flashcards</h2>
            <p className="text-xs text-zinc-400">
              Train pattern recognition with tiny, repeatable drills.
            </p>
          </div>
        </div>
        <span className="text-xs text-zinc-500">
          Card {index + 1} / {cards.length}
        </span>
      </div>

      {/* CARD CONTENT */}
      <div className="bg-zinc-950/40 border border-zinc-800 rounded-lg p-4 space-y-3">

        {/* BOARD SECTION */}
        <div className="flex justify-center py-2">
          <div className="border border-zinc-800 rounded-lg overflow-hidden">
            <Chessboard
              id="FlashcardBoard"
              position={current.fen}
              boardWidth={300}
              animationDuration={200}
              customDarkSquareStyle={{ backgroundColor: "#1e1e1e" }}
              customLightSquareStyle={{ backgroundColor: "#3a3a3a" }}
            />
          </div>
        </div>

        {/* METADATA */}
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-zinc-400">
          <span className="uppercase tracking-wide text-cyan-400">
            {current.theme}
          </span>
          <span>Side to move: {current.sideToMove}</span>
        </div>

        {/* NAME */}
        <h3 className="text-base font-semibold text-white">{current.name}</h3>

        {/* PROMPT / ANSWER */}
        <div className="mt-2 text-sm text-zinc-300">
          {!showAnswer ? (
            <p>{current.prompt}</p>
          ) : (
            <p className="font-medium text-zinc-100">{current.answer}</p>
          )}
        </div>
      </div>

      {/* CONTROLS */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-2">
          <Button
            onClick={goPrev}
            className="bg-zinc-800 hover:bg-zinc-700 text-xs px-3 py-2"
          >
            Previous
          </Button>
          <Button
            onClick={goNext}
            className="bg-zinc-800 hover:bg-zinc-700 text-xs px-3 py-2"
          >
            Next
          </Button>
        </div>

        <Button
          onClick={() => setShowAnswer((v) => !v)}
          className="bg-cyan-600 hover:bg-cyan-700 text-xs px-4 py-2"
        >
          {showAnswer ? "Hide Explanation" : "Show Explanation"}
        </Button>
      </div>

      {/* FOOTER TIP */}
      <p className="text-[10px] text-zinc-500">
        Tip: Repeat these patterns until your brain starts recognizing them instantly.
      </p>
    </div>
  );
}