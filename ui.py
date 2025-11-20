import pygame
from game import GoGame 
import threading
from agent import MinimaxAgent
from typing import Tuple, Optional, Callable
import time

SQUARE_SIZE = 60
BOARD_MARGIN = 30
BOARD_SIZE_PX = 9 * SQUARE_SIZE
SCREEN_SIZE = BOARD_SIZE_PX + 2 * BOARD_MARGIN
STONE_RADIUS = SQUARE_SIZE // 2 - 5

BACKGROUND_COLOR = (205, 133, 63)
LINE_COLOR = (0, 0, 0)
BLACK_STONE_COLOR = (0, 0, 0)
WHITE_STONE_COLOR = (255, 255, 255)

class GoUI:
    def __init__(self, game: GoGame, agent: Optional[MinimaxAgent] = None):
        pygame.init()
        self.game = game
        self.agent = agent
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption("Go 9x9 (Task 2 AI)")
        self.running = True
        self.font = pygame.font.Font(None, 36)
        
        # --- NEW THREADING STATE ---
        self.ai_thinking = False
        self.ai_next_move = None
        self.ai_heuristic = self.agent.heuristic if self.agent else None

    def _get_coords(self, r: int, c: int) -> Tuple[int, int]:
        #Convert board (row, col) to screen (x, y) coordinates.
        x = c * SQUARE_SIZE + BOARD_MARGIN
        y = r * SQUARE_SIZE + BOARD_MARGIN
        return x, y

    def _get_board_pos(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        #Convert screen (x, y) to board (row, col). Returns None if outside grid.
        r = round((y - BOARD_MARGIN) / SQUARE_SIZE)
        c = round((x - BOARD_MARGIN) / SQUARE_SIZE)
        
        if 0 <= r < self.game.SIZE and 0 <= c < self.game.SIZE:
            return r, c
        return None

    def draw_board(self):
        #Renders the board lines and stones
        self.screen.fill(BACKGROUND_COLOR)

        # Draw grid lines
        for i in range(self.game.SIZE):
            # Vertical lines
            start_x, start_y = self._get_coords(0, i)
            end_x, end_y = self._get_coords(self.game.SIZE - 1, i)
            pygame.draw.line(self.screen, LINE_COLOR, (start_x, start_y), (end_x, end_y), 2)
            
            # Horizontal lines
            start_x, start_y = self._get_coords(i, 0)
            end_x, end_y = self._get_coords(i, self.game.SIZE - 1)
            pygame.draw.line(self.screen, LINE_COLOR, (start_x, start_y), (end_x, end_y), 2)

        # Draw stones
        for r in range(self.game.SIZE):
            for c in range(self.game.SIZE):
                if self.game.grid[r, c] != self.game.EMPTY:
                    color = BLACK_STONE_COLOR if self.game.grid[r, c] == self.game.BLACK else WHITE_STONE_COLOR
                    x, y = self._get_coords(r, c)
                    pygame.draw.circle(self.screen, color, (x, y), STONE_RADIUS)
        
        # Display turn info
        self.draw_info()

    def draw_info(self):
        #Displays current player and score information.
        text = f"Turn: {'BLACK' if self.game.current_player == self.game.BLACK else 'WHITE'}"
        score = f"B Captures: {self.game.captured_black} | W Captures: {self.game.captured_white}"
        
        text_surface = self.font.render(text, True, LINE_COLOR)
        score_surface = self.font.render(score, True, LINE_COLOR)
        
        self.screen.blit(text_surface, (10, 10))
        self.screen.blit(score_surface, (SCREEN_SIZE - score_surface.get_width() - 10, 10))

    def handle_click(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        #Processes mouse click input and converts it to a board move (r, c).
        r_c = self._get_board_pos(*pos)
        
        if r_c and self.game.is_valid_move(*r_c):
            return r_c
        return None

    def _start_ai_search(self):
        """Starts the AI search in a separate thread."""
        if not self.ai_thinking:
            self.ai_thinking = True
            
            # Use a wrapper function for the thread target
            def search_wrapper():
                # The slow blocking call happens here, in the background thread
                start_time = time.time()
                move = self.agent.get_best_move(self.game)
                end_time = time.time()
                
                self.ai_next_move = move
                self.ai_thinking = False # Signal the main thread that the result is ready
                
                print(f"AI search finished: {move} (Time: {end_time - start_time:.3f}s)")
            
            # Start the thread
            threading.Thread(target=search_wrapper).start()

    def run_game(self, is_ai_mode: bool, results_function: Callable, max_turns: int = 60):
        """Main loop that manages game flow, including AI and Human turns."""
        clock = pygame.time.Clock()
        turn_counter = 1
        
        while self.running and not self.game.is_game_over and turn_counter <= max_turns:
            
            move = None
            
            # --- 1. Event Handling (for Human Clicks) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN and not self.ai_thinking:
                    # Only allow clicks if the AI is not currently searching
                    if self.game.current_player == self.game.BLACK or not is_ai_mode:
                        move = self.handle_click(event.pos)

            # --- 2. Start AI Search (Non-Blocking) ---
            if is_ai_mode and self.game.current_player == self.game.WHITE and not self.ai_thinking:
                if self.ai_next_move is None: # Only start search if we don't have a move waiting
                    self._start_ai_search()

            # --- 3. Process AI Result (Once Ready) ---
            if self.ai_next_move is not None:
                move = self.ai_next_move
                self.ai_next_move = None # Clear the result
            
            # --- 4. Apply Move (Human Click or AI Result) ---
            if move is not None or (is_ai_mode and self.game.current_player == self.game.WHITE and not self.ai_thinking):
                if move is not None:
                    # Ensure we only process a valid human move or a ready AI move
                    self.game = self.game.get_next_state(move)
                    turn_counter += 1
                    
                    # Print evaluation after AI moves (when the next player is BLACK)
                    if is_ai_mode and self.game.current_player == self.game.BLACK:
                        eval_score = self.ai_heuristic.evaluate(self.game)
                        print(f"Heuristic Evaluation (AI POV): {eval_score:.2f}")

            # --- Rendering ---
            self.draw_board()
            
            # Optional: Add "Thinking" text while ai_thinking is True
            if self.ai_thinking:
                 thinking_surface = self.font.render("AI Thinking...", True, LINE_COLOR)
                 self.screen.blit(thinking_surface, (SCREEN_SIZE / 2 - 50, 5))
            
            pygame.display.flip()
            clock.tick(60)

        # --- Game Over Screen/Forced End ---
        # ... (Game over logic remains the same)
        
        # Ensure Pygame quits safely
        if self.running:
             results_function(self.game, self.agent.heuristic if self.agent else None)
             time.sleep(5)
             pygame.quit()