from game import GoGame
from agent import MinimaxAgent
from heuristic import SimpleGoHeuristic
from ui import GoUI
from typing import Optional
import numpy as np


def print_board(grid: np.ndarray):
    size = grid.shape[0]
    print("  " + " ".join(map(str, range(size))))
    for i, row in enumerate(grid):
        stones = ['.', 'B', 'W']
        print(f"{i} " + " ".join([stones[x] for x in row]))

def calculate_and_print_results(game: GoGame, heuristic: Optional[SimpleGoHeuristic]):
    print("\n--- Final Game Summary ---")

    score_black, score_white = game.calculate_score_for_calculation()
    
    print(f"Final Captures (B/W): {game.captured_black} / {game.captured_white}")
    print(f"Estimated Final Score (B/W, including Komi): {score_black:.1f} / {score_white:.1f}")
    
    if score_white > score_black:
        print("Winner: White")
    elif score_black > score_white:
        print("Winner: Black")
    else:
        print("Result: Tie")

# --- GAME MODES `1---

def start_game_mode(is_ai_mode: bool):
    """Initializes and runs the selected game mode."""
    GAME_SIZE = 9
    game = GoGame(size=GAME_SIZE)
    
    # Set a very low limit for demonstration purposes.
    # L=12 means 6 moves each, which ensures a fast demo.
    MAX_TURNS_LIMIT = 20 
    
    if is_ai_mode:
        heuristic = SimpleGoHeuristic()
        agent = MinimaxAgent(heuristic = heuristic, depth_limit = 2) 
        print(f"Starting Mode 1: Human (Click) vs. AI (Minimax L={agent.depth_limit})")
        
        # Pass the results function AND the max_turns limit
        GoUI(game, agent).run_game(is_ai_mode=True, results_function=calculate_and_print_results, max_turns=MAX_TURNS_LIMIT)
    else:
        print("Starting Mode 2: Human (Click) vs. Human (Click)")
        
        # Pass the results function AND the max_turns limit
        GoUI(game).run_game(is_ai_mode=False, results_function=calculate_and_print_results, max_turns=MAX_TURNS_LIMIT)

# ... (rest of the file content remains the same)

if __name__ == '__main__':
    valid_input = False
    while not valid_input:
        try:
            choice = input("Select Game Mode: (1) Player vs AI | (2) Player vs Player: ")
            mode = int(choice)
            
            if mode == 1:
                start_game_mode(is_ai_mode=True)
                valid_input = True
            elif mode == 2:
                start_game_mode(is_ai_mode=False)
                valid_input = True
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")