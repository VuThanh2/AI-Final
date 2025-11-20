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

    def get_best_move(self, game_object: GoGame) -> Optional[Tuple[int, int]]:
        #Main search function, find the best move for the AI
        best_score = -np.inf
        best_move = None

        valid_moves = game_object.get_valid_moves()
        possible_moves = valid_moves + [None]

        #Start search (AI is maximizing)
        for move in possible_moves:
            new_game_object = game_object.get_next_state(move)

            #Opponent (Minimizer) moves next
            score = self._minimax(new_game_object, self.depth_limit - 1, -np.inf, np.inf, False)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move
    
    def _minimax(self, game_object: GoGame, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        #Core recursive Minimax algorithm
        if depth == 0 or game_object.is_game_over:
            return self.heuristic.evaluate(game_object)
        
        possible_moves = game_object.get_valid_moves() + [None]

        if maximizing_player: #AI/White
            max_evaluation = -np.inf

            for move in possible_moves:
                new_game_object = game_object.get_next_state(move)
                evaluation = self._minimax(new_game_object, depth - 1, alpha, beta, False)
                max_evaluation = max(max_evaluation, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha: return max_evaluation
            
            return max_evaluation
        else: #Player/Black
            min_evaluation = np.inf
            for move in possible_moves:
                new_game_object = game_object.get_next_state(move)
                evaluation = self._minimax(new_game_object, depth - 1, alpha, beta, True)
                min_evaluation = min(min_evaluation, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha: return min_evaluation
            return min_evaluation