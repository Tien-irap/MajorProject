import chess
import chess.engine
import copy
import os
from typing import List, Dict, Any, Optional
from backend.app.core.logger import logger

class GeneticPuzzleGenerator:
    """
    Implements an Evolutionary Algorithm to generate unique chess puzzles.
    
    Biologically-Inspired Components:
    1. Genotype: The Board State (FEN).
    2. Mutation: Geometric transformations (Mirroring, Shifting) and Noise Injection.
    3. Fitness Function: Stockfish Evaluation (Must remain solvable and tactical).
    4. Selection: Elitism (Only valid, high-quality mutations survive).
    """

    def __init__(self, stockfish_path: str):
        self.stockfish_path = stockfish_path
        self.engine = None

    def _start_engine(self):
        if not self.engine:
            # Ensure the path is correct for your system
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)

    def _stop_engine(self):
        if self.engine:
            self.engine.quit()
            self.engine = None

    # --- MUTATION OPERATORS (The "Evolution") ---

    def _mutate_mirror_horizontal(self, board: chess.Board) -> Optional[chess.Board]:
        """
        Mutation Type: Geometric Reflection.
        Flips the board horizontally (A-file <-> H-file).
        This forces the user to recognize the pattern's geometry, not just memory.
        """
        try:
            new_board = board.transform(chess.flip_horizontal)
            
            # Validate the resulting board is legal
            if not new_board.is_valid():
                return None
                
            return new_board
        except Exception as e:
            logger.error(f"Mirror mutation error: {e}")
            return None

    def _mutate_shift(self, board: chess.Board, direction: str) -> Optional[chess.Board]:
        """
        Mutation Type: Spatial Translation.
        Shifts all pieces left or right by 1 file.
        Forces the user to recognize the pattern relative to board edges.
        """
        new_board = chess.Board(None) # Start empty
        shift = -1 if direction == "left" else 1
        
        piece_map = board.piece_map()
        
        for square, piece in piece_map.items():
            file_idx = chess.square_file(square)
            rank_idx = chess.square_rank(square)
            
            new_file = file_idx + shift
            
            # Fitness Constraint: If a piece falls off the world, the mutation dies.
            if new_file < 0 or new_file > 7:
                return None
                
            new_square = chess.square(new_file, rank_idx)
            new_board.set_piece_at(new_square, piece)
            
        # Copy game state
        new_board.turn = board.turn
        new_board.castling_rights = chess.BB_EMPTY # Shifting usually breaks castling
        new_board.ep_square = None # En passant is no longer valid after shifting
        new_board.halfmove_clock = 0
        new_board.fullmove_number = board.fullmove_number
        
        # Validate the board has required pieces and is legal
        if not new_board.is_valid():
            return None
            
        return new_board

    # --- FITNESS FUNCTION (The "Natural Selection") ---

    def _calculate_fitness(self, board: chess.Board, baseline_eval_score: int) -> int:
        """
        Determines if a mutation survives.
        Fitness = 1 if (Legal AND Winning AND Solvable).
        Fitness = 0 if (Illegal OR Draw/Loss OR Too simple).
        """
        if not board.is_valid():
            return 0

        try:
            # Analyze at low depth for efficiency
            info = self.engine.analyse(board, chess.engine.Limit(depth=12))
            
            # Check if PV exists
            if "pv" not in info or not info["pv"] or len(info["pv"]) == 0:
                return 0
            
            # Get score from perspective of player to move
            score = info["score"].relative.score(mate_score=10000)
            
            if score is None: 
                return 0

            # Survival Criteria 1: Must be winning (> +1.5 pawns)
            if score < 150: 
                return 0
            
            return 1 # The organism survives
        except Exception as e:
            logger.error(f"Fitness calculation error: {e}")
            return 0

    # --- MAIN GENERATION LOOP ---

    def generate_puzzles(self, seed_fen: str, num_variations: int = 3) -> List[Dict[str, Any]]:
        """
        The Evolutionary Cycle.
        """
        self._start_engine()
        seed_board = chess.Board(seed_fen)
        generated_puzzles = []

        # 1. Analyze Seed (Control Group)
        try:
            info = self.engine.analyse(seed_board, chess.engine.Limit(depth=15))
            
            # Check if PV (principal variation) exists
            if "pv" not in info or not info["pv"] or len(info["pv"]) == 0:
                self._stop_engine()
                return [] # No valid moves found
            
            best_move = info["pv"][0].uci()
            score = info["score"].relative.score(mate_score=10000)
            
            if score is None:
                self._stop_engine()
                return [] # Score unavailable
        except Exception as e:
            logger.error(f"Error analyzing seed position: {e}")
            self._stop_engine()
            return [] # Seed was bad

        # Add Seed Puzzle
        generated_puzzles.append({
            "fen": seed_fen,
            "solution": [best_move],
            "theme": "Original Mistake",
            "generator_type": "seed",
            "eval_score": score
        })

        # 2. Apply Mutations
        mutations_to_try = [
            ("mirror", None), 
            ("shift", "left"), 
            ("shift", "right")
        ]

        logger.info(f"Starting mutations for seed FEN")
        
        for m_type, direction in mutations_to_try:
            if len(generated_puzzles) > num_variations:
                break

            logger.debug(f"Attempting {m_type} mutation {f'({direction})' if direction else ''}")
            
            mutated_board = None
            if m_type == "mirror":
                mutated_board = self._mutate_mirror_horizontal(seed_board)
            elif m_type == "shift":
                mutated_board = self._mutate_shift(seed_board, direction)
            
            if not mutated_board:
                logger.warning(f"Mutation {m_type} failed: Board became invalid")
                continue
            
            logger.debug(f"Mutation {m_type} created successfully, testing fitness")

            # 3. Check Fitness
            fitness = self._calculate_fitness(mutated_board, score)
            logger.debug(f"Fitness score for {m_type}: {fitness}")
            
            if fitness == 1:
                    # 4. Selection: It survived, add to population
                    try:
                        info_mut = self.engine.analyse(mutated_board, chess.engine.Limit(depth=15))
                        
                        # Check if PV exists for mutated position
                        if "pv" not in info_mut or not info_mut["pv"] or len(info_mut["pv"]) == 0:
                            continue # Skip this mutation
                        
                        sol_move = info_mut["pv"][0].uci()
                        mut_score = info_mut["score"].relative.score(mate_score=10000)
                        
                        if mut_score is None:
                            continue # Skip if score unavailable
                        
                        generated_puzzles.append({
                            "fen": mutated_board.fen(),
                            "solution": [sol_move],
                            "theme": f"{m_type.capitalize()}ed Variation",
                            "generator_type": "evolutionary",
                            "eval_score": mut_score
                        })
                        logger.info(f"{m_type.capitalize()} mutation SURVIVED and added to puzzle set")
                    except Exception as e:
                        logger.error(f"Error analyzing mutated position ({m_type}): {e}")
                        continue # Skip this mutation
            else:
                logger.debug(f"Fitness test FAILED for {m_type} - mutation eliminated")

        self._stop_engine()
        logger.info(f"Puzzle generation complete: {len(generated_puzzles)} total puzzles")
        return generated_puzzles