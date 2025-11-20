from abc import ABC, abstractmethod
from game import GoGame
import numpy as np

class GoHeuristic(ABC):
    #Abstract interface for evaluating the Go Game state
    def __init__(self):
        pass

    @abstractmethod
    def evaluate(self, game_obj: GoGame) -> float:
        #Return a score for the given game state (Maximizing player POV)
        pass

class SimpleGoHeuristic(GoHeuristic):
    #Implementation of the Heuristic Function
    #Evaluation = (White Score - Black Score) + 0.1 * (White Liberties - Black Liberties)
    def __init__(self):
        super().__init__()
        self.SAFETY_WEIGHT = 0.1

    def evaluate(self, game_object: GoGame) -> float:
        score_black, score_white = game_object.calculate_score_for_calculation()
        base_evaluation = score_white - score_black

        liberty_diff = 0
        visited_groups = np.zeros_like(game_object.grid, dtype = bool)

        for row in range(game_object.SIZE):
            for collumn in range(game_object.SIZE):
                if game_object.grid[row, collumn] != game_object.EMPTY and not visited_groups[row, collumn]:
                    #Calculate liberties for the group
                    liberties, group = game_object._get_group_info(row, collumn, game_object.grid)

                    for grid_row, grid_collumn in group:
                        visited_groups[grid_row, grid_collumn] = True

                    #Calculate liberty difference
                    player = game_object.grid[row, collumn]
                    if player == game_object.WHITE:
                        liberty_diff += liberties   
                    else:
                        liberty_diff -= liberties
        
        safety_bonus = liberty_diff * self.SAFETY_WEIGHT

        return base_evaluation + safety_bonus