// --- Central Type Definitions ---

/**
 * Represents the status of an analysis job.
 */
export interface StatusResponse {
  status: "PENDING" | "IN_PROGRESS" | "COMPLETED" | "FAILED";
  error?: string;
}

/**
 * Information about a single move and its evaluation.
 */
export interface MoveInfo {
  move_num: number;
  move: string;
  eval_before: number;
  eval_after: number;
  eval_diff: number;
  board_before_fen: string;
}

/**
 * A "key move" (like a mistake or best move) with an explanation.
 */
export interface KeyMove {
  move_info: MoveInfo;
  explanation: string;
}

/**
 * The final, complete analysis result for a game.
 */
export interface AnalysisResult {
  game_headers: {
    Site?: string;
    White?: string;
    Black?: string;
    [key: string]: string | undefined; // Allow other headers
  };
  key_move_summary: {
    mistakes: KeyMove[];
    best_moves: KeyMove[];
  };
  move_by_move_analysis: MoveInfo[];
}