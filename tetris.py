import pygame
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_CELL_SIZE = 30
GRID_WIDTH = 10  # Number of columns
GRID_HEIGHT = 20  # Number of rows
GAME_AREA_WIDTH = GRID_WIDTH * GRID_CELL_SIZE
GAME_AREA_HEIGHT = GRID_HEIGHT * GRID_CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)  # I
YELLOW = (255, 255, 0)  # O
PURPLE = (128, 0, 128)  # T
GREEN = (0, 255, 0)  # S
RED = (255, 0, 0)  # Z
BLUE = (0, 0, 255)  # J
ORANGE = (255, 165, 0)  # L

# Standard Tetromino Shapes and Rotations
# Coordinates are relative to a pivot point for each shape.
# Pivot is generally the center of a 3x3 box or a specific block.
TETROMINO_SHAPES = {
    'I': [  # Pivot: center of the 4-block line
        [(0, 1), (1, 1), (2, 1), (3, 1)],  # Horizontal (around y=1)
        [(2, 0), (2, 1), (2, 2), (2, 3)]   # Vertical (around x=2)
    ],
    'O': [  # Pivot: top-left of the 2x2 square
        [(0, 0), (1, 0), (0, 1), (1, 1)]
    ],
    'T': [  # Pivot: (1,1) in a 3x3 grid
        [(0, 1), (1, 1), (2, 1), (1, 0)],  # T pointing down (top spike)
        [(1, 0), (0, 1), (1, 1), (1, 2)],  # T pointing left (right spike)
        [(0, 1), (1, 1), (2, 1), (1, 2)],  # T pointing up (bottom spike)
        [(1, 0), (1, 1), (2, 1), (1, 2)]   # T pointing right (left spike)
    ],
    'S': [  # Pivot: (1,1)
        [(1, 0), (2, 0), (0, 1), (1, 1)],  # Horizontal S
        [(0, 0), (0, 1), (1, 1), (1, 2)]   # Vertical S
    ],
    'Z': [  # Pivot: (1,1)
        [(0, 0), (1, 0), (1, 1), (2, 1)],  # Horizontal Z
        [(2, 0), (1, 1), (2, 1), (1, 2)]   # Vertical Z (corrected from (1,0),(0,1),(1,1),(0,2))
    ],
    'J': [  # Pivot: (1,1)
        [(0, 0), (0, 1), (1, 1), (2, 1)],  # J shape, long part pointing left, hook down
        [(1, 0), (2, 0), (1, 1), (1, 2)],  # Pointing up, hook right
        [(0, 1), (1, 1), (2, 1), (2, 2)],  # Pointing right, hook up
        [(1, 0), (1, 1), (0, 2), (1, 2)]   # Pointing down, hook left
    ],
    'L': [  # Pivot: (1,1)
        [(2, 0), (0, 1), (1, 1), (2, 1)],  # L shape, long part pointing right, hook down
        [(1, 0), (1, 1), (1, 2), (2, 2)],  # Pointing up, hook left
        [(0, 1), (1, 1), (2, 1), (0, 2)],  # Pointing left, hook up
        [(0, 0), (1, 0), (1, 1), (1, 2)]   # Pointing down, hook right
    ]
}

TETROMINO_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

class Tetromino:
    def __init__(self, x, y, shape_name):
        self.x = x
        self.y = y
        self.shape_name = shape_name
        self.rotation = 0
        self.shape = TETROMINO_SHAPES[self.shape_name][self.rotation] # Initial shape based on rotation 0
        self.color = TETROMINO_COLORS[self.shape_name]

    def move_down(self, board_grid):
        """Attempts to move the tetromino down. Returns True if successful, False otherwise."""
        if is_valid_position(self, board_grid, offset_y=1):
            self.y += 1
            return True
        return False

    def move_left(self, board_grid):
        """Attempts to move the tetromino left. Returns True if successful."""
        if is_valid_position(self, board_grid, offset_x=-1):
            self.x -= 1
            return True
        return False

    def move_right(self, board_grid):
        """Attempts to move the tetromino right. Returns True if successful."""
        if is_valid_position(self, board_grid, offset_x=1):
            self.x += 1
            return True
        return False

    def rotate(self, board_grid):
        """Attempts to rotate the tetromino. Returns True if successful."""
        original_rotation = self.rotation
        self.rotation = (self.rotation + 1) % len(TETROMINO_SHAPES[self.shape_name])
        self.shape = TETROMINO_SHAPES[self.shape_name][self.rotation]
        
        if not is_valid_position(self, board_grid):
            # Revert rotation if the new position is invalid
            self.rotation = original_rotation
            self.shape = TETROMINO_SHAPES[self.shape_name][self.rotation]
            return False
        return True

    def draw(self, screen, grid_offset_x, grid_offset_y):
        for block_x, block_y in self.shape:
            pygame.draw.rect(
                screen,
                self.color,
                (grid_offset_x + (self.x + block_x) * GRID_CELL_SIZE,
                 grid_offset_y + (self.y + block_y) * GRID_CELL_SIZE,
                 GRID_CELL_SIZE -1, # -1 to show grid lines
                 GRID_CELL_SIZE -1)
            )

def create_random_tetromino(grid_width):
    shape_name = random.choice(list(TETROMINO_SHAPES.keys()))
    # Start tetromino in the middle of the grid horizontally, near the top
    start_x = grid_width // 2 - 1 # Adjust if pieces are too far right
    start_y = 0 # Start at the very top. Some shapes might have blocks with negative y relative to pivot.
    return Tetromino(start_x, start_y, shape_name)

# --- Game Logic Helper Functions ---

def create_board_grid():
    """Creates an empty game board grid."""
    return [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def is_valid_position(tetromino, board_grid, offset_x=0, offset_y=0):
    """
    Checks if the tetromino's current or projected position is valid.
    - All blocks must be within game board boundaries (left, right, bottom).
    - Blocks cannot overlap with settled blocks in board_grid.
    - Blocks can be above the visible top of the board (y < 0), so no top boundary check here.
    """
    for block_rel_x, block_rel_y in tetromino.shape:
        # Actual grid coordinates of the block
        actual_x = tetromino.x + block_rel_x + offset_x
        actual_y = tetromino.y + block_rel_y + offset_y

        # Boundary checks
        if not (0 <= actual_x < GRID_WIDTH):  # Check left/right walls
            return False
        if actual_y >= GRID_HEIGHT:  # Check bottom wall (collides with floor)
            return False
        
        # Collision with settled blocks (only if block is within visible grid height and on the board)
        if actual_y >= 0: # Only check board_grid if block is at or below y=0 (on the visible board)
            if board_grid[actual_y][actual_x] != BLACK:  # BLACK represents an empty cell
                return False
    return True

def lock_tetromino(tetromino, board_grid):
    """Locks the tetromino onto the board_grid."""
    for block_rel_x, block_rel_y in tetromino.shape:
        actual_x = tetromino.x + block_rel_x
        actual_y = tetromino.y + block_rel_y
        # Only lock parts of the tetromino that are within the visible grid
        # This prevents errors if a piece locks while partially above the screen (e.g. game over scenario)
        if 0 <= actual_y < GRID_HEIGHT and 0 <= actual_x < GRID_WIDTH:
            board_grid[actual_y][actual_x] = tetromino.color

def clear_lines(board_grid):
    """
    Checks for and clears completed lines from the board_grid.
    Returns the number of lines cleared.
    """
    lines_cleared = 0
    row_idx = GRID_HEIGHT - 1  # Start checking from the bottom row

    while row_idx >= 0: # Iterate upwards
        is_line_full = True
        for col_idx in range(GRID_WIDTH):
            if board_grid[row_idx][col_idx] == BLACK:  # If any cell in the row is empty
                is_line_full = False
                break
        
        if is_line_full:
            lines_cleared += 1
            del board_grid[row_idx]  # Remove the full line
            # Add a new empty line at the top to maintain grid height
            board_grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
            # Don't decrement row_idx here because the line above (now at row_idx) needs to be checked
        else:
            row_idx -= 1  # Move to check the row above if current wasn't full
            
    return lines_cleared

# Scoring system
LINE_SCORES = {
    0: 0, # For 0 lines cleared
    1: 40,
    2: 100,
    3: 300,
    4: 1200 # Tetris!
}

# --- Main Game Function ---
def main():
    pygame.init()
    pygame.font.init()  # Initialize the font module
    score_font = pygame.font.SysFont('Consolas', 30) # Font for displaying score
    game_over_font = pygame.font.SysFont('Consolas', 50) # Font for "GAME OVER" message

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    # Calculate offsets to center the game area on the screen
    grid_offset_x = (SCREEN_WIDTH - GAME_AREA_WIDTH) // 2
    grid_offset_y = (SCREEN_HEIGHT - GAME_AREA_HEIGHT) // 2

    board_grid = create_board_grid()
    current_tetromino = create_random_tetromino(GRID_WIDTH)
    fall_time = 0
    fall_speed = 500  # Milliseconds per automatic step down (adjust for difficulty)
    score = 0
    game_over = False

    running = True
    while running:
        dt = clock.get_rawtime() # Time since last frame in milliseconds
        if not game_over:
            fall_time += dt

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN: # Handle key presses
                if not game_over:
                    if event.key == pygame.K_LEFT:
                        current_tetromino.move_left(board_grid)
                    elif event.key == pygame.K_RIGHT:
                        current_tetromino.move_right(board_grid)
                    elif event.key == pygame.K_UP:
                        current_tetromino.rotate(board_grid)
                    elif event.key == pygame.K_DOWN: # Soft drop
                        # Attempt to move down; if successful, reset fall timer for responsive feel
                        if current_tetromino.move_down(board_grid):
                            fall_time = 0 
                        else: # If soft drop fails, it means the piece should lock.
                              # Force the fall_time to exceed fall_speed to trigger lock in next block.
                            fall_time = fall_speed 
                else: # If game is over, allow restart on 'R' key press
                    if event.key == pygame.K_r:
                        board_grid = create_board_grid()
                        current_tetromino = create_random_tetromino(GRID_WIDTH)
                        score = 0
                        game_over = False
                        fall_time = 0


        # Game Logic (Automatic Falling and Locking)
        if not game_over and fall_time >= fall_speed:
            if not current_tetromino.move_down(board_grid):  # Attempt to move down automatically
                # If move_down returns False, the tetromino has landed or is blocked by another piece
                lock_tetromino(current_tetromino, board_grid)
                
                lines_cleared_count = clear_lines(board_grid)
                if lines_cleared_count > 0:
                    score += LINE_SCORES.get(lines_cleared_count, 0) # Add score based on lines cleared
                
                current_tetromino = create_random_tetromino(GRID_WIDTH)
                # Check for game over: if the new tetromino is immediately in an invalid position
                if not is_valid_position(current_tetromino, board_grid):
                    game_over = True
                    print(f"Game Over! Final Score: {score}") # Log to console
            fall_time = 0 # Reset timer after successful move or after locking and spawning new piece

        # --- Drawing ---
        screen.fill(BLACK)  # Clear screen with black background

        # Draw game area border
        pygame.draw.rect(screen, WHITE, 
                         (grid_offset_x - 2, grid_offset_y - 2, 
                          GAME_AREA_WIDTH + 4, GAME_AREA_HEIGHT + 4), 2) # 2 is border thickness

        # Draw grid lines within the game area
        for x_idx in range(GRID_WIDTH + 1): # Vertical lines
            pygame.draw.line(screen, GRAY,
                             (grid_offset_x + x_idx * GRID_CELL_SIZE, grid_offset_y),
                             (grid_offset_x + x_idx * GRID_CELL_SIZE, grid_offset_y + GAME_AREA_HEIGHT))
        for y_idx in range(GRID_HEIGHT + 1): # Horizontal lines
            pygame.draw.line(screen, GRAY,
                             (grid_offset_x, grid_offset_y + y_idx * GRID_CELL_SIZE),
                             (grid_offset_x + GAME_AREA_WIDTH, grid_offset_y + y_idx * GRID_CELL_SIZE))
        
        # Draw settled blocks from board_grid
        for r_idx, row in enumerate(board_grid):
            for c_idx, cell_color in enumerate(row):
                if cell_color != BLACK:  # If the cell is not empty (doesn't contain background color)
                    pygame.draw.rect(
                        screen,
                        cell_color,
                        (grid_offset_x + c_idx * GRID_CELL_SIZE,
                         grid_offset_y + r_idx * GRID_CELL_SIZE,
                         GRID_CELL_SIZE - 1,  # Subtract 1 to show grid lines between blocks
                         GRID_CELL_SIZE - 1)
                    )

        # Draw current falling tetromino (if game is not over)
        if not game_over:
            current_tetromino.draw(screen, grid_offset_x, grid_offset_y)

        # Display Score
        score_text_surface = score_font.render(f"Score: {score}", True, WHITE)
        # Position score to the right of the game area
        screen.blit(score_text_surface, (grid_offset_x + GAME_AREA_WIDTH + 20, grid_offset_y + 20))
        
        # Display Game Over Message if game_over is True
        if game_over:
            game_over_surface = game_over_font.render("GAME OVER", True, RED)
            # Center the "GAME OVER" message on the screen
            text_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(game_over_surface, text_rect)
            
            restart_font = pygame.font.SysFont('Consolas', 20) # Smaller font for restart message
            restart_surface = restart_font.render("Press 'R' to Restart", True, WHITE)
            restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))
            screen.blit(restart_surface, restart_rect)


        pygame.display.flip()  # Update the full screen
        clock.tick(60) # Limit to 60 FPS

    pygame.font.quit() # Uninitialize font module when game loop ends
    pygame.quit()

if __name__ == '__main__':
    main()
