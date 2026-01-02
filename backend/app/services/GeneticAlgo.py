import chess
import chess.engine
import copy
from backend.app.services.mutation_engine import mutation_engine
from backend.app.core.logger import logger

class EvolutionaryPuzzleGenerator:
    def __init__(self, stockfish_path):
        self.engine_path = stockfish_path

    def evolve_puzzle(self, parent_fen, motif, solution_move_uci, num_generations=1):
        """
        The Main Loop (Refined Workflow):
        1. Takes a user's mistake (parent_fen) as the single parent.
        2. Mutates it using valid chess geometry (Asexual Reproduction).
        3. Validates the 'children' with Stockfish to ensure the tactic is preserved.
        4. Uses Elitism: Always keeps the original parent.
        5. Returns top 3 unique puzzles sorted by fitness.
        """
        
        # 1. Population Initialization (Single Parent)
        current_population = [parent_fen]
        valid_offspring = []
        
        # Elitism: Evaluate and store the original parent
        parent_fitness, parent_best_move = self._evaluate_fitness(parent_fen)
        logger.info(f"Parent puzzle fitness: {parent_fitness:.2f}, best move: {parent_best_move}")
        
        # Store parent as a candidate (it will always be considered)
        if parent_fitness >= 0.5:  # Parent must be at least somewhat valid
            valid_offspring.append({
                "fen": parent_fen,
                "best_move": parent_best_move or solution_move_uci,
                "fitness": parent_fitness,
                "motif": motif,
                "type": "original",
                "is_parent": True
            })

        # We rely on Stockfish to find the best move in the mutated position.
        # The motif should be preserved by the geometric transformations.

        for generation in range(num_generations):
            new_candidates = set()
            
            # 2. Mutation (Asexual Reproduction - No Crossover)
            logger.info(f"Generation {generation + 1}: Generating mutations...")
            for fen in current_population:
                # Generate ~5 mutants per parent (limited to avoid API overload)
                mutants = mutation_engine.generate_candidates(fen, motif, num_candidates=5)
                new_candidates.update(mutants)
                logger.info(f"Generated {len(mutants)} mutation candidates")

            # 3. Genotype -> Phenotype Validation
            logger.info(f"Validating {len(new_candidates)} candidates...")
            for child_fen in new_candidates:
                # Skip if identical to parent
                if child_fen == parent_fen:
                    continue
                    
                # Validate the board is legal
                try:
                    board = chess.Board(child_fen)
                    if not board.is_valid():
                        logger.debug(f"Invalid board rejected: {child_fen[:30]}...")
                        continue
                except Exception as e:
                    logger.debug(f"Board creation failed: {e}")
                    continue
                
                # 4. Fitness Evaluation
                fitness_score, best_move_uci = self._evaluate_fitness(child_fen)
                
                # Fitness Criteria (Refined):
                # 1. Valid Board ✓
                # 2. Clear Solution (Gap >= 0.5 for moderate clarity, >= 1.5 for high clarity)
                # 3. Not identical to parent ✓
                # 4. Side to move has winning advantage
                
                if fitness_score >= 0.5:  # Lowered threshold for more variations
                    valid_offspring.append({
                        "fen": child_fen,
                        "best_move": best_move_uci,
                        "fitness": fitness_score,
                        "motif": motif,
                        "type": "evolved",
                        "is_parent": False
                    })
                    logger.info(f"Valid offspring found with fitness: {fitness_score:.2f}")

            # 5. Stop Condition: After 1 generation (as per refined workflow)
            logger.info(f"Generation {generation + 1} complete. Total valid offspring: {len(valid_offspring)}")
            break  # Stop after 1 generation
        
        # 6. Replacement (Survival of the Fittest with Elitism)
        # ALWAYS include the parent as the first puzzle (elitism)
        parent_fitness, parent_best_move = self._evaluate_fitness(parent_fen)
        
        # If parent evaluation failed, use the original best move passed in
        # Fallback: If engine calc failed, use the user provided solution move
        if not parent_best_move:
             logger.warning("Engine failed to verify parent best move. Using provided solution move.")
             # Normalize solution_move_uci (remove promotion if needed or keep it)
             parent_best_move = solution_move_uci 
             parent_fitness = 1.0 # Force validity
        
        parent_puzzle = {
            "fen": parent_fen,
            "best_move": parent_best_move,
            "fitness": parent_fitness if parent_fitness >= 0 else 0.0,
            "motif": motif,
            "type": "original",
            "is_parent": True
        }
        
        logger.info(f"Parent puzzle fitness: {parent_fitness:.2f}")
        
        # Remove duplicates from offspring based on FEN (keep highest fitness)
        unique_puzzles = {}
        for puzzle in valid_offspring:
            fen = puzzle['fen']
            if fen not in unique_puzzles or puzzle['fitness'] > unique_puzzles[fen]['fitness']:
                unique_puzzles[fen] = puzzle
        
        offspring_population = list(unique_puzzles.values())
        
        # Sort offspring by clarity (fitness) - highest first
        offspring_population.sort(key=lambda x: x['fitness'], reverse=True)
        
        # Return parent + top offspring (total = 4 puzzles: 1 parent + 3 evolved)
        top_puzzles = [parent_puzzle] + offspring_population[:3]
        
        logger.info(f"Evolution complete. Returning {len(top_puzzles)} puzzles (1 parent + {len(offspring_population[:3])} evolved).")
        for i, p in enumerate(top_puzzles):
            logger.info(f"Puzzle {i+1}: Fitness={p['fitness']:.2f}, Type={p['type']}, is_parent={p['is_parent']}")
        
        return top_puzzles

    def _evaluate_fitness(self, fen):
        """
        Returns (Score_Gap, Best_Move_UCI).
        
        Fitness Formula:
        Score_Gap = (Best Move Score) - (2nd Best Move Score) / 100
        
        High Gap (>= 1.5): Puzzle has a very clear, obvious solution
        Medium Gap (0.5 - 1.5): Puzzle is moderate, solution is findable
        Low Gap (< 0.5): Puzzle is ambiguous or confusing
        
        Also validates:
        - Side to move has winning advantage (> +1 pawn)
        - Position is not already mate/stalemate
        """
        try:
            board = chess.Board(fen)
            if not board.is_valid():
                return -1, None
            
            # Check for immediate game over
            if board.is_game_over():
                return -1, None

        except Exception as e:
            logger.debug(f"Board validation error: {e}")
            return -1, None

        try:
            # Connect to engine for this specific evaluation
            with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
                # Analyze for top 2 moves with slightly more time for accuracy
                info = engine.analyse(board, chess.engine.Limit(time=0.5), multipv=2)
                
                if len(info) < 1:
                    return -1, None  # No moves found

                # Get Score of Best Move
                best_score_obj = info[0]["score"].relative
                best_move = info[0]["pv"][0].uci()
                
                # Handle mate scores
                if best_score_obj.is_mate():
                    mate_in = best_score_obj.mate()
                    if mate_in > 0:  # Winning mate
                        # Mate puzzles have high fitness
                        best_score = 10000
                    else:
                        return -1, None  # Getting mated, not a valid puzzle
                else:
                    best_score = best_score_obj.score(mate_score=10000)

                # If winning side doesn't have advantage, reject
                if best_score < 100:  # Less than +1 pawn advantage
                    return -1, None

                # Calculate Gap (Distinctness)
                if len(info) >= 2:
                    second_score_obj = info[1]["score"].relative
                    
                    if second_score_obj.is_mate():
                        second_mate_in = second_score_obj.mate()
                        second_score = 10000 if second_mate_in > 0 else -10000
                    else:
                        second_score = second_score_obj.score(mate_score=10000)
                    
                    gap = best_score - second_score
                    
                    # Normalize Gap to pawns (centipawns / 100)
                    fitness = gap / 100.0
                    
                    # Cap fitness at reasonable value
                    fitness = min(fitness, 15.0)
                else:
                    # Only 1 good move found -> High Fitness (Forced move)
                    fitness = 10.0 

                return fitness, best_move

        except Exception as e:
            logger.error(f"Engine evaluation error: {e}")
            return -1, None