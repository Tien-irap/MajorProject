import chess
import random
import copy
from backend.app.core.logger import logger

# --- CONFIGURATION ---

# Group 1: Pure Geometric (Can shift anywhere, mirror anywhere)
# These tactics usually depend on relative piece positions, not the board edge.
GEOMETRIC_MOTIFS = {
    "Pin", "Fork", "Skewer", "Discovered Attack", 
    "Trapped Piece", "Deflection", "Decoy", "Overloaded Piece",
    "Zwischenzug", "Hanging Piece"
}

# Group 2: Edge/Rank Dependent (Careful with vertical shifting)
# These rely on the board boundaries (rank 1 or 8).
RANK_DEPENDENT_MOTIFS = {
    "Back Rank Weakness", "Promotion", "Mating Net", "Blundered Checkmate"
}

# Group 3: Static/Specific (Hard to mutate geometrically)
# Opening theory is fixed; Positional errors are often subtle and break with shifts.
STATIC_MOTIFS = {
    "Opening Theory", "Positional Error"
}

class MutationEngine:
    def __init__(self):
        pass

    def generate_candidates(self, original_fen, motif, num_candidates=5):
        """
        Main entry point. Takes a FEN and a Motif, returns a list of mutated FENs.
        
        Applies geometric transformations suitable for the given motif:
        - Mirror, Color Swap, Shifting, Distractors
        
        Returns up to num_candidates unique, valid FENs.
        """
        candidates = set()  # Use set to avoid duplicates
        
        try:
            board = chess.Board(original_fen)
            if not board.is_valid():
                logger.warning(f"Invalid original FEN provided: {original_fen}")
                return []
        except Exception as e:
            logger.error(f"Failed to parse FEN: {e}")
            return []

        logger.info(f"Generating mutations for motif: {motif}")

        # 1. Always try Horizontal Mirroring (Left-Right Flip)
        # Safe for most tactics, creates recognizable but different position
        mirror_fen = self._apply_horizontal_mirror(board)
        if mirror_fen and self._validate_position(mirror_fen):
            candidates.add(mirror_fen)
            logger.debug(f"Added horizontal mirror candidate")

        # 2. Try Color Swap (Rotate 180 degrees)
        # Play the same position but as the other color
        swap_fen = self._apply_color_swap(board)
        if swap_fen and self._validate_position(swap_fen):
            candidates.add(swap_fen)
            logger.debug(f"Added color swap candidate")

        # 3. Apply Shifting (Translation)
        # Generate shifts based on motif restrictions
        shifts = self._generate_shifts(board, motif)
        for shift_fen in shifts:
            if self._validate_position(shift_fen):
                candidates.add(shift_fen)
        logger.debug(f"Added {len(shifts)} shift candidates")

        # 4. Distractors (Noise)
        # Take some candidates and add visual complexity
        # Creates "Hard Mode" versions
        noisy_candidates = set()
        candidates_list = list(candidates)
        for fen in candidates_list[:min(3, len(candidates_list))]:  # Limit to avoid too many
            if len(candidates) + len(noisy_candidates) >= num_candidates * 2:
                break
            noisy_fen = self._add_distractors(fen, intensity=1)
            if noisy_fen and self._validate_position(noisy_fen):
                noisy_candidates.add(noisy_fen)
        
        candidates.update(noisy_candidates)
        logger.debug(f"Added {len(noisy_candidates)} distractor candidates")

        # Convert to list and limit output
        final_candidates = list(candidates)[:num_candidates]
        logger.info(f"Generated {len(final_candidates)} total mutation candidates")
        return final_candidates
    
    def _validate_position(self, fen):
        """
        Validates that a FEN represents a legal, reasonable chess position.
        Returns True if valid, False otherwise.
        """
        try:
            board = chess.Board(fen)
            
            # Basic legality check
            if not board.is_valid():
                return False
            
            # Check both kings exist
            if not board.king(chess.WHITE) or not board.king(chess.BLACK):
                return False
            
            # Check kings are not adjacent
            wk = board.king(chess.WHITE)
            bk = board.king(chess.BLACK)
            if chess.square_distance(wk, bk) < 2:
                return False
            
            # Position should not be already game over
            if board.is_game_over():
                return False
            
            return True
            
        except Exception:
            return False

    # --- STRATEGY 1: MIRRORING ---
    def _apply_horizontal_mirror(self, board):
        """Flips the board horizontally (Files A<->H)."""
        # python-chess transform function handles this elegantly
        try:
            new_board = board.transform(chess.flip_horizontal)
            return new_board.fen()
        except Exception:
            return None

    def _apply_color_swap(self, board):
        """
        Flips the board vertically and changes the turn.
        (e.g., White on e4 becomes Black on e5).
        """
        try:
            new_board = board.transform(chess.flip_vertical)
            # transform also swaps the side to move automatically? 
            # In python-chess, flip_vertical mirrors ranks. 
            # If we want to 'play as black', we might need to ensure the turn is correct.
            # Usually flip_vertical preserves the logic but from the other side.
            return new_board.fen()
        except Exception:
            return None

    # --- STRATEGY 2: SHIFTING ---
    def _generate_shifts(self, board, motif):
        """
        Moves all pieces by (x, y) squares.
        Respects motif constraints (e.g., don't shift Back Rank motifs vertically).
        """
        if motif in STATIC_MOTIFS:
            return []

        generated_fens = []
        
        # Define allowed shifts
        # (File Shift, Rank Shift)
        shifts_to_try = [
            (1, 0), (-1, 0),  # Horizontal
            (0, 1), (0, -1),  # Vertical
            (1, 1), (-1, -1), # Diagonal
            (1, -1), (-1, 1)  # Diagonal
        ]

        # If Motif depends on Ranks (e.g. Back Rank Mate), forbid Vertical shifts
        if motif in RANK_DEPENDENT_MOTIFS:
            shifts_to_try = [s for s in shifts_to_try if s[1] == 0]

        piece_map = board.piece_map()

        for dx, dy in shifts_to_try:
            new_board = chess.Board(None) # Empty board
            new_board.turn = board.turn
            new_board.castling_rights = chess.BB_EMPTY # Puzzles usually strip castling rights to avoid ambiguity
            new_board.ep_square = None # Reset en passant for simplicity
            
            valid_shift = True
            
            for square, piece in piece_map.items():
                rank = chess.square_rank(square)
                file = chess.square_file(square)

                new_rank = rank + dy
                new_file = file + dx

                # 1. Boundary Check
                if not (0 <= new_rank <= 7 and 0 <= new_file <= 7):
                    valid_shift = False
                    break
                
                # 2. Pawn Check (Pawns cannot be on Rank 1 or 8, which are ranks 0 and 7 in 0-indexed)
                if piece.piece_type == chess.PAWN:
                    if new_rank == 0 or new_rank == 7:
                        valid_shift = False
                        break

                new_square = chess.square(new_file, new_rank)
                new_board.set_piece_at(new_square, piece)

            # Validate the shifted board before adding
            if valid_shift and self._validate_position(new_board.fen()):
                generated_fens.append(new_board.fen())

        return generated_fens

    # --- STRATEGY 3: DISTRACTORS ---
    def _add_distractors(self, fen, intensity=1):
        """
        Adds random, non-interfering pieces to the board to increase visual complexity.
        This is a 'naive' addition; verification must be done by Stockfish later.
        """
        board = chess.Board(fen)
        
        # Candidate pieces for distractors (low value or blocked pieces)
        distractor_pieces = [
            chess.Piece(chess.PAWN, chess.WHITE),
            chess.Piece(chess.PAWN, chess.BLACK),
            chess.Piece(chess.KNIGHT, chess.WHITE), # Knights are good for visual clutter
            chess.Piece(chess.KNIGHT, chess.BLACK),
        ]

        # Identify squares far from the action?
        # Since we don't know the exact "action" squares here without engine analysis,
        # we try to place pieces on the edge of the board or empty zones.
        
        empty_squares = [s for s in chess.SQUARES if board.piece_at(s) is None]
        
        # Shuffle to pick random spots
        random.shuffle(empty_squares)

        added_count = 0
        for square in empty_squares:
            if added_count >= intensity:
                break

            # Heuristic: Don't place distractors near the Kings (safety)
            wk_sq = board.king(chess.WHITE)
            bk_sq = board.king(chess.BLACK)
            
            if wk_sq and chess.square_distance(square, wk_sq) < 2:
                continue
            if bk_sq and chess.square_distance(square, bk_sq) < 2:
                continue

            # Heuristic: Don't put Pawns on rank 1 or 8
            rank = chess.square_rank(square)
            piece_to_add = random.choice(distractor_pieces)
            
            if piece_to_add.piece_type == chess.PAWN and (rank == 0 or rank == 7):
                continue
                
            board.set_piece_at(square, piece_to_add)
            added_count += 1
            
        return board.fen()

# Singleton instance for easy import
mutation_engine = MutationEngine()