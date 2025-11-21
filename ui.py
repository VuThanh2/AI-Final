import pygame
from game import GoGame 
import threading
from agent import MinimaxAgent
from typing import Tuple, Optional, Callable, List
import time

TOP_UI_HEIGHT = 60
SQUARE_SIZE = 60
BOARD_MARGIN = 30
BOARD_SIZE_PX = 9 * SQUARE_SIZE
SCREEN_SIZE = BOARD_SIZE_PX + 2 * BOARD_MARGIN + TOP_UI_HEIGHT
STONE_RADIUS = SQUARE_SIZE // 2 - 5

BOARD_COLOR = (218, 165, 32) 
LINE_COLOR = (50, 50, 50)
BLACK_STONE_COLOR = (10, 10, 10)
WHITE_STONE_COLOR = (245, 245, 245)
PASS_COLOR = (120, 120, 120)

PASS_BUTTON = pygame.Rect(SCREEN_SIZE - 120, SCREEN_SIZE - 40 - TOP_UI_HEIGHT, 100, 30)
GIVE_UP_BUTTON = pygame.Rect(SCREEN_SIZE - 120, SCREEN_SIZE - 80 - TOP_UI_HEIGHT, 100, 30)

NO_ACTION = "NO_ACTION"
PASS_MOVE = "PASS"

class GoUI:
    def __init__(self, game: GoGame, agent: Optional[MinimaxAgent] = None):
        pygame.init()
        self.game = game
        self.agent = agent
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption("Go 9x9 (Task 2 AI)")
        self.running = True
        self.font = pygame.font.Font(None, 36)
        
        #THREADING STATE 
        self.ai_thinking = False
        self.ai_result_ready = False 
        self.ai_next_move = NO_ACTION 
        self.ai_heuristic = self.agent.heuristic if self.agent else None

    def get_coordinate(self, row, collumn):
        x = collumn * SQUARE_SIZE + BOARD_MARGIN
        y = row * SQUARE_SIZE + BOARD_MARGIN + TOP_UI_HEIGHT   
        return x, y

    def get_board_position(self, x, y):
        y -= TOP_UI_HEIGHT   # FIX

        row = round((y - BOARD_MARGIN) / SQUARE_SIZE)
        collumn = round((x - BOARD_MARGIN) / SQUARE_SIZE)

        if 0 <= row < self.game.SIZE and 0 <= collumn < self.game.SIZE:
            return row, collumn
        return None

    def draw_board(self):
        self.screen.fill(BOARD_COLOR)

        # Draw grid lines
        for i in range(self.game.SIZE):
            # Vertical lines
            start_x, start_y = self.get_coordinate(0, i)
            end_x, end_y = self.get_coordinate(self.game.SIZE - 1, i)
            pygame.draw.line(self.screen, LINE_COLOR, (start_x, start_y), (end_x, end_y), 2)
            
            # Horizontal lines
            start_x, start_y = self.get_coordinate(i, 0)
            end_x, end_y = self.get_coordinate(i, self.game.SIZE - 1)
            pygame.draw.line(self.screen, LINE_COLOR, (start_x, start_y), (end_x, end_y), 2)

        # Draw stones (with simple 3D effect)
        for row in range(self.game.SIZE):
            for collumn in range(self.game.SIZE):
                if self.game.grid[row, collumn] != self.game.EMPTY:
                    x, y = self.get_coordinate(row, collumn)
                    
                    if self.game.grid[row, collumn] == self.game.BLACK:
                        # Draw shadow (offset slightly)
                        pygame.draw.circle(self.screen, (0, 0, 0, 100), (x + 2, y + 2), STONE_RADIUS)
                        # Draw stone
                        pygame.draw.circle(self.screen, BLACK_STONE_COLOR, (x, y), STONE_RADIUS)
                    else:
                        # Draw shadow
                        pygame.draw.circle(self.screen, (150, 150, 150, 100), (x + 2, y + 2), STONE_RADIUS)
                        # Draw stone
                        pygame.draw.circle(self.screen, WHITE_STONE_COLOR, (x, y), STONE_RADIUS)
        
        self._draw_pass_button()
        self._draw_give_up_button()
        self.draw_info()
        
    def _draw_pass_button(self):
        rectangle = PASS_BUTTON
        radius = 5
        
        # 1. Draw rounded button background (with slight shadow)
        shadow_color = (90, 90, 90)
        pygame.draw.rect(self.screen, shadow_color, rectangle.move(0, 1), border_radius=radius)
        
        # 2. Draw button main color
        pygame.draw.rect(self.screen, PASS_COLOR, rectangle, border_radius=radius)
        
        # 3. Draw text
        text_surface = self.font.render("PASS", True, LINE_COLOR)
        text_rect = text_surface.get_rect(center=rectangle.center)
        self.screen.blit(text_surface, text_rect)
    
    def _draw_give_up_button(self):
        rectangle = GIVE_UP_BUTTON
        radius = 5

        # Shadow
        shadow_color = (90, 90, 90)
        pygame.draw.rect(self.screen, shadow_color, rectangle.move(0, 1), border_radius=radius)

        # Button main color (red)
        pygame.draw.rect(self.screen, (200, 50, 50), rectangle, border_radius=radius)

        # Text
        text_surface = self.font.render("GIVE UP", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rectangle.center)
        self.screen.blit(text_surface, text_rect)


    def draw_info(self):
        header_rect = pygame.Rect(0, 0, SCREEN_SIZE, TOP_UI_HEIGHT)
        pygame.draw.rect(self.screen, (140, 100, 60), header_rect)

        turn_text = f"Turn: {'BLACK' if self.game.current_player == self.game.BLACK else 'WHITE'}"
        score_text = f"B Captures: {self.game.captured_black} | W Captures: {self.game.captured_white}"

        turn_surface = self.font.render(turn_text, True, WHITE_STONE_COLOR)
        score_surface = self.font.render(score_text, True, WHITE_STONE_COLOR)

        self.screen.blit(turn_surface, (10, 10))
        self.screen.blit(score_surface, (SCREEN_SIZE - score_surface.get_width() - 10, 10))

        if self.ai_thinking:
            thinking_surface = self.font.render("AI Thinking...", True, WHITE_STONE_COLOR)
            thinking_rect = thinking_surface.get_rect(center=(SCREEN_SIZE // 2, TOP_UI_HEIGHT // 2))
            self.screen.blit(thinking_surface, thinking_rect)


    def draw_game_over(self):
        score_black, score_white = self.game.calculate_score_for_evaluation()

        # If game ended by give up
        if hasattr(self.game, "winner"):
            winner_text = f"Winner: {'BLACK' if self.game.winner == self.game.BLACK else 'WHITE'} ( Player {'WHITE' if self.game.winner == self.game.BLACK else 'BLACK'} Give Up)"
            final_score_text = f"Score: B {score_black:.1f} | W {score_white:.1f}"
        else:
            if score_white > score_black:
                winner_text = "Winner: WHITE"
            elif score_black > score_white:
                winner_text = "Winner: BLACK"
            else:
                winner_text = "Result: TIE"
            final_score_text = f"Final Score: B {score_black:.1f} | W {score_white:.1f}"

        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        self.screen.blit(overlay, (0, 0))

        winner_surface = self.font.render(winner_text, True, (255, 255, 255)) 
        score_surface = self.font.render(final_score_text, True, (255, 255, 255))

        winner_rect = winner_surface.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 - 40))
        score_rect = score_surface.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + 10))

        self.screen.blit(winner_surface, winner_rect)
        self.screen.blit(score_surface, score_rect)

        pygame.display.flip()

        
    #GAME FLOW & THREADING 

    def handle_click(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        r_c = self.get_board_position(*pos)
        if r_c and self.game.is_valid_move(*r_c):
            return r_c
        return None

    def start_ai_search(self):
        if not self.ai_thinking:
            self.ai_thinking = True
            
            def search_wrapper():
                start_time = time.time()
                move = self.agent.get_best_move(self.game)
                end_time = time.time()
                
                if move is None:
                    self.ai_next_move = PASS_MOVE
                    print_move = "PASS"
                else:
                    self.ai_next_move = move
                    print_move = move
                    
                self.ai_result_ready = True 
                self.ai_thinking = False
                
                print(f"AI search finished: {print_move} (Time: {end_time - start_time:.3f}s)")
            
            threading.Thread(target=search_wrapper).start()

    def wait_before_quit(self, seconds: int):
        start_time = time.time()
        temp_clock = pygame.time.Clock()
        while time.time() < start_time + seconds:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return 
            temp_clock.tick(30)

    def run_game(self, is_ai_mode: bool, results_function: Callable, max_turns: int = 100):
        clock = pygame.time.Clock()
        turn_counter = 1
        
        while self.running and not self.game.is_game_over: 
            
            move_to_process = NO_ACTION
            
            #1. Event Handling (Player Input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.ai_thinking:
                    if self.game.current_player == self.game.BLACK or not is_ai_mode:
                        if GIVE_UP_BUTTON.collidepoint(event.pos):
                            giving_up_player = self.game.current_player
                            
                            if giving_up_player == self.game.BLACK:
                                self.game.winner = self.game.WHITE
                            else:
                                self.game.winner = self.game.BLACK
                                
                            self.game.is_game_over = True
                            print(f"Player { 'BLACK' if giving_up_player == self.game.BLACK else 'WHITE' } gave up! Winner: { 'BLACK' if self.game.winner == self.game.BLACK else 'WHITE' }")
                            move_to_process = NO_ACTION 
                            break 
                        elif PASS_BUTTON.collidepoint(event.pos):
                            print("Player chose to PASS")
                            move_to_process = PASS_MOVE
                        else:
                            clicked_move = self.handle_click(event.pos)
                            if clicked_move is not None:
                                move_to_process = clicked_move

            #2. Start AI Search
            if is_ai_mode and self.game.current_player == self.game.WHITE:
                if not self.ai_thinking and not self.ai_result_ready:
                    self.start_ai_search()

            #3. Process AI Result 
            if self.ai_result_ready:
                move_to_process = self.ai_next_move
                self.ai_next_move = NO_ACTION 
                self.ai_result_ready = False

            #4. Apply Move (Centralized Logic)
            if move_to_process != NO_ACTION and not self.game.is_game_over:
                
                # Convert PASS_MOVE sentinel or coordinates to the actual move (None or tuple)
                actual_move = None if move_to_process == PASS_MOVE else move_to_process
                
                self.game = self.game.get_next_state(actual_move)
                turn_counter += 1
                
                if is_ai_mode and self.game.current_player == self.game.BLACK and self.ai_heuristic:
                    eval_score = self.ai_heuristic.evaluate(self.game)
                    print(f"Heuristic Evaluation (AI POV): {eval_score:.2f}")
                
                # Emergency stop check
                if turn_counter > max_turns:
                    self.game.is_game_over = True

            self.draw_board()
            
            pygame.display.flip()
            clock.tick(60)

        #GAME OVER / CLEANUP 
        if self.running:
            results_function(self.game, self.agent.heuristic if self.agent else None)
            self.draw_game_over()
            self.wait_before_quit(5)
            pygame.quit()