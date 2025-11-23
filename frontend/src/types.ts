export interface MoveAnalysis {
  move_num: number;
  move: string; // SAN or UCI string
  classification: "Blunder" | "Mistake" | "Inaccuracy" | "Good Move" | "Best Move" | "Book";
  eval: number; // Current eval
  eval_diff: number; // Centipawn loss
  eval_before: number; // Eval before move
  board_before_fen: string; // Essential for rendering the board state
  best_move: string;
  global_cluster?: number; // Optional: if the move was assigned a cluster ID
}

export interface WeaknessProfile {
  global_pattern_name: string;
  num_mistakes: number;
  avg_centipawn_loss: number;
  example_moves: string[]; // Array of UCI strings, e.g., ["e2e4"]
  llm_explanation: string;
}

export interface KeyMoveSummaryItem {
  move_info: MoveAnalysis;
  explanation: string;
}

export interface AnalysisResult {
  game_headers: {
    White: string;
    Black: string;
    Site?: string;
    Date?: string;
    Result?: string;
    [key: string]: any;
  };
  move_by_move_analysis: MoveAnalysis[];
  
  // The weakness report is a dictionary where keys are cluster IDs (strings)
  weakness_report: Record<string, WeaknessProfile> | null;
  
  key_move_summary: {
    mistakes: KeyMoveSummaryItem[];
    best_moves: KeyMoveSummaryItem[];
  };
}

export interface StatusResponse {
  status: "PENDING" | "STARTED" | "COMPLETED" | "FAILED";
  error?: string;
  analysis_id?: string;
}

// --- Evolutionary Puzzle Types ---
export interface PuzzleDB {
  _id: string;
  fen: string;
  solution: string[];
  theme: string;
  generator_type: "seed" | "evolutionary";
  difficulty_level?: number;
  created_at?: string;
}

export interface GeneratePuzzleRequest {
  fen: string;
  move_uci: string;
  difficulty_level: number;
}

export interface SubmitPuzzleResult {
  puzzle_id: string;
  user_id: string;
  is_correct: boolean;
  time_taken_seconds: number;
}