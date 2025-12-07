from game import GoGame
from agent import MinimaxAgent
from heuristic import SimpleGoHeuristic
from ui import GoUI
from typing import Optional

def calculate_and_print_results(game: GoGame, heuristic: Optional[SimpleGoHeuristic]):
    print("\n--- Final Game Summary (Base on Heuristic Evaluation) ---")

    score_black, score_white = game.calculate_score_for_evaluation()
    
    print(f"Final Captures (B/W): {game.captured_black} / {game.captured_white}")
    print(f"Estimated Final Score (B/W, including Komi): {score_black:.1f} / {score_white:.1f}")
    
    if score_white > score_black:
        print("Winner: White")
    elif score_black > score_white:
        print("Winner: Black")
    else:
        print("Result: Tie")

#GAME MODES 

def start_game_mode(is_ai_mode: bool):
    GAME_SIZE = 9
    game = GoGame(size=GAME_SIZE)
    
    MAX_TURNS_LIMIT = 20 
    
    if is_ai_mode:
        heuristic = SimpleGoHeuristic()
        agent = MinimaxAgent(heuristic = heuristic, depth_limit = 3) 
        print(f"Starting Mode 1: Human (Click) vs. AI (Minimax L={agent.depth_limit})")
        
        GoUI(game, agent).run_game(is_ai_mode=True, results_function=calculate_and_print_results, max_turns = MAX_TURNS_LIMIT)
    else:
        print("Starting Mode 2: Human (Click) vs. Human (Click)")
        
        GoUI(game).run_game(is_ai_mode=False, results_function=calculate_and_print_results, max_turns=MAX_TURNS_LIMIT)

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