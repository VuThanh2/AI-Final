from typing import Tuple, Optional
from game import GoGame
from heuristic import GoHeuristic
import numpy as np

class MinimaxAgent:
    #Implement the Minimax Search Algorithm with Alpha-Beta Pruning
    def __init__(self, heuristic: GoHeuristic, depth_limit: int):
        #Dependency Injection
        self.heuristic = heuristic
        self.depth_limit = depth_limit
        self.ai_player = GoGame.WHITE 

    def get_best_move(self, game: GoGame) -> Optional[Tuple[int, int]]:
        valid_moves = game.get_valid_moves()

        # If no moves → forced pass
        if len(valid_moves) == 0:
            return None

        best_score = -np.inf
        best_move = None

        #Evaluate all legal moves ONLY — do NOT evaluate pass!
        for move in valid_moves:
            new_state = game.get_next_state(move)
            score = self.minimax_algorithm(new_state, self.depth_limit - 1, -np.inf, np.inf, False)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move
    
    def minimax_algorithm(self, game: GoGame, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        # Terminal state
        if depth == 0 or game.is_game_over:
            return self.heuristic.evaluate(game)

        # Get all valid moves for current player
        moves = game.get_valid_moves()

        # If no moves → current player must pass
        if not moves:
            moves = [None]

        if maximizing_player:
            max_evaluation = -np.inf
            for move in moves:
                new_state = game.get_next_state(move)
                evaluation_score = self.minimax_algorithm(new_state, depth - 1, alpha, beta, False)
                max_evaluation = max(max_evaluation, evaluation_score)
                alpha = max(alpha, evaluation_score)
                if beta <= alpha:
                    break
            return max_evaluation
        else:
            min_evaluation = np.inf
            for move in moves:
                new_state = game.get_next_state(move)
                evaluation_score = self.minimax_algorithm(new_state, depth - 1, alpha, beta, True)
                min_evaluation = min(min_evaluation, evaluation_score)
                beta = min(beta, evaluation_score)
                if beta <= alpha:
                    break
            return min_evaluation
