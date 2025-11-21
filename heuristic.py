from abc import ABC, abstractmethod
from game import GoGame
import numpy as np
from collections import deque
from typing import Tuple, Set, List

class GoHeuristic(ABC):
    @abstractmethod
    def evaluate(self, game_obj: GoGame) -> float:
        #Return a score for the given game state (Maximizing player POV)
        pass

class SimpleGoHeuristic(GoHeuristic):
    def __init__(self):
        super().__init__()
        self.LIBERTY_WEIGHT = 0.3
        self.TERRITORY_WEIGHT = 0.8
        self.WIN_BONUS = 1000 #Make sure AI always prefers winning than scoring

    def evaluate(self, game_object: GoGame) -> float:
        #Calculates the heuristic score based on Terminal State, Material, Safety, and Territory.
        score_black, score_white = game_object.calculate_score_for_evaluation()
        
        #1. Terminal state check 
        if game_object.is_game_over:
            if score_white > score_black:
                return self.WIN_BONUS + (score_white - score_black)
            elif score_black > score_white:
                return -self.WIN_BONUS - (score_black - score_white)
            else:
                return 0  # Tie
        
        #2. Calculation of Liberty and Territory scores
        liberty_score, territory_score = self.analyze_board(game_object)
        
        #3.Heuristic Score  
        base_evaluation = score_white - score_black
        total = (base_evaluation + liberty_score * self.LIBERTY_WEIGHT + territory_score * self.TERRITORY_WEIGHT)
        
        return total

    def analyze_board(self, game: GoGame) -> Tuple[float, float]:
        #Compute liberties of groups and empty regions for territory.
        visited = np.zeros_like(game.grid, dtype = bool)
        liberty_different = 0.0
        territory_different = 0.0

        for row in range(game.SIZE):
            for collumn in range(game.SIZE):
                if visited[row, collumn]:
                    continue

                cell = game.grid[row, collumn]

                if cell != game.EMPTY:
                    # Stone group
                    liberties, group = game.get_group_info(row, collumn, game.grid)
                    for gr, gc in group:
                        visited[gr, gc] = True

                    # Weighted liberties
                    if liberties == 1:
                        weighted_liberties = -5.0
                    elif liberties == 2:
                        weighted_liberties = -1.0
                    else:
                        weighted_liberties = liberties * 0.5

                    if cell == game.WHITE:
                        liberty_different += weighted_liberties
                    else:
                        liberty_different -= weighted_liberties

                else:
                    # Empty region (territory)
                    region, borders = self.bfs_empty_region(game, row, collumn, visited)
                    for rr, rc in region:
                        visited[rr, rc] = True

                    if len(borders) == 1:
                        border_color = borders.pop()
                        if border_color == game.WHITE:
                            territory_different += len(region)
                        elif border_color == game.BLACK:
                            territory_different -= len(region)

        return liberty_different, territory_different

    def bfs_empty_region(self, game: GoGame, start_row: int, start_col: int, visited: np.ndarray) -> Tuple[List[Tuple[int, int]], Set[int]]:
        queue = deque([(start_row, start_col)])
        region = []
        borders: Set[int] = set()
        visited[start_row, start_col] = True

        while queue:
            r, c = queue.popleft()
            region.append((r, c))

            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < game.SIZE and 0 <= nc < game.SIZE:
                    neighbor_cell = game.grid[nr, nc]
                    if neighbor_cell == game.EMPTY and not visited[nr, nc]:
                        visited[nr, nc] = True
                        queue.append((nr, nc))
                    elif neighbor_cell != game.EMPTY:
                        borders.add(neighbor_cell)

        return region, borders