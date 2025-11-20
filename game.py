import numpy as np
from typing import Tuple, List, Optional
from collections import deque
from copy import deepcopy

class GoGame:
    #Manage the full game state, rules, and move transitions (Problem Class)
    SIZE, EMPTY, BLACK, WHITE = 9, 0, 1, 2
    KOMI = 7.5

    def __init__(self, **kwargs):
        #State Data
        self.grid = kwargs.get('grid', np.zeros((self.SIZE, self.SIZE), dtype = int))
        self.current_player = kwargs.get('current_player', self.BLACK)
        self.captured_black = kwargs.get('captured_black' , 0)
        self.captured_white = kwargs.get('captured_white', 0)
        self.consecutive_passes = kwargs.get('consecutive_passes', 0)
        self.ko_point = kwargs.get('ko_point', None)
        self.is_game_over = kwargs.get('is_game_over', False)

    def _get_neighbors(self, row: int, collumn: int) -> List[Tuple[int, int]]:
        #Return adjacent points
        neighbors = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = row + dr, collumn + dc
            if 0 <= nr < self.SIZE and 0 <= nc < self.SIZE:
                neighbors.append((nr, nc))
        return neighbors
    
    def _get_group_info(self, row: int, collumn: int, grid:np.ndarray) -> Tuple[int, List[Tuple[int, int]]]:
        #Calculate liberties and return group stone for the stone at (r, c)
        #Simplified implementation of BFS/DFS to find liberties and group
        if grid[row, collumn] == self.EMPTY: return 0, []

        player = grid[row, collumn]
        queue = deque([(row, collumn)])
        visited = set([(row, collumn)])
        liberties = set()
        group_stones = []

        while queue:
            current_row, current_collumn = queue.popleft()
            group_stones.append((current_row, current_collumn))
            for nr, nc in self._get_neighbors(current_row, current_collumn):
                point = (nr, nc)
                if point not in visited:
                    if grid[nr, nc] == self.EMPTY:
                        liberties.add(point)
                    elif grid[nr, nc] == player:
                        visited.add(point)
                        queue.append(point)
        return len(liberties), group_stones
    
    #Rule Checks

    def _check_suicide(self, row:int, collumn:int, player: int) -> bool:
        #Check if placing a stone at (r, c) results in suicide
        temp_grid = self.grid.copy()
        temp_grid[row, collumn] = player

        opponent = self.WHITE if player == self.BLACK else self.BLACK

        #Check for capture (capture prevent suicide)
        for nr, nc in self._get_neighbors(row, collumn):
            if temp_grid[nr, nc] == opponent:
                liberties_opp, _ = self._get_group_info(nr, nc, temp_grid)
                if liberties_opp == 0:
                    return False
                
        #Check if the resulting friendly group has at least one liberty
        liberties, _ = self._get_group_info(row, collumn, temp_grid)
        return liberties == 0

    def is_valid_move(self, row: int, collumn: int) -> bool:
        #Check basic rules (occpancy suicide, Ko). 
        player = self.current_player
        if not (0 <= row < self.SIZE and 0 <= collumn < self.SIZE): return False
        if self.grid[row, collumn] != self.EMPTY: return False
        if self._check_suicide(row, collumn, player): return False
        if self.ko_point and self.ko_point == (row, collumn) : return False
        return True
    
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        #Return all legal non-pass moves for the current player 
        moves = []
        for row in range(self.SIZE):
            for collumn in range(self.SIZE):
                if self.is_valid_move(row, collumn):
                    moves.append((row, collumn))
        return moves
    
    #States Transition (Key for Minimax)

    def get_next_state(self, move: Optional[Tuple[int, int]]) -> 'GoGame':
        #Calculate and return a new GoGame object after the move
        player= self.current_player

        #1.Prepare context for the new state by the deep copying curretn state
        context = deepcopy(vars(self))
        context['current_player'] = self.WHITE if player == self.BLACK else self.BLACK
        context['ko_point'] = None

        if move is None:
            #Handle Pass
            context ['consecutive_passes'] += 1 
        else:
            #Handle Stone Placement and Captures
            row, collumn = move
            new_grid = context['grid'].copy()
            new_grid[row, collumn] = player

            new_grid, new_ko, captured_count = self._calculate_captures(new_grid, move, player, context)

            context['grid'] = new_grid
            context['ko_point'] = new_ko
            context['consecutive_passes'] = 0

        new_game = GoGame(**context)

        if new_game.consecutive_passes >= 2:
            new_game.is_game_over = True

        return new_game
    
    def _calculate_captures(self, grid: np.ndarray, move: Tuple[int, int], player: int, context: dict) -> Tuple[np.ndarray, Optional[Tuple[int, int]], int]:
        #Calculate captures, removes them from the grid, updates score context, and return ko info
        row, collumn = move
        opponent = self.WHITE if player == self.BLACK else self.BLACK
        board_state = grid
        total_captured = 0
        new_ko_point = None

        for nr, nc in self._get_neighbors(row, collumn):
            if board_state[nr, nc] == opponent:
                liberties, group = self._get_group_info(nr, nc, board_state)

                if liberties == 0:
                    # --- FIX APPLIED: All logic relying on captured_count is correctly nested ---
                    captured_count = len(group)
                    total_captured += captured_count

                    #Remove the captured group
                    for cr, cc in group:
                        board_state[cr, cc] = self.EMPTY

                    #Update score in the context dictionary
                    if player == self.BLACK:
                        context['captured_black'] += captured_count
                    else:
                        context['captured_white'] += captured_count
                    
                    # Ko point assignment
                    if captured_count == 1:
                        new_ko_point = group[0]
                
        return board_state, new_ko_point, total_captured
    
    #Scoring for Heuristic

    def calculate_score_for_calculation(self) -> Tuple[float, float]:
        #Calculate score based on stones + captures + Komi
        score_black = self.captured_black + np.sum(self.grid == self.BLACK)
        score_white = self.captured_white + np.sum(self.grid == self.WHITE) + self.KOMI
        return score_black, score_white         