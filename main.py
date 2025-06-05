import pygame

# Initialize Pygame
pygame.init()
pygame.font.init() # Initialize font module
pygame.mixer.init() # Initialize mixer module

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Window title
pygame.display.set_caption("My Pygame Window")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)
PLAYER_BODY_COLOR = (0, 0, 255)  # Blue
PLAYER_HAT_COLOR = (255, 0, 0)   # Red
GROUND_PLATFORM_COLOR = (0, 100, 0) # Dark Green
BRICK_PLATFORM_COLOR = (200, 100, 50) # Orange-Red


# Font
font = pygame.font.Font(None, 36) # Default system font, size 36

# Sound Effects & Music - load with error handling
jump_sound = None
coin_sound = None
stomp_sound = None
hit_sound = None
using_placeholder_sounds = False

try:
    jump_sound = pygame.mixer.Sound('assets/sounds/jump.wav')
except pygame.error:
    print("Warning: Could not load 'jump.wav'. Placeholder used.")
    using_placeholder_sounds = True
try:
    coin_sound = pygame.mixer.Sound('assets/sounds/coin.wav')
except pygame.error:
    print("Warning: Could not load 'coin.wav'. Placeholder used.")
    using_placeholder_sounds = True
try:
    stomp_sound = pygame.mixer.Sound('assets/sounds/stomp.wav')
except pygame.error:
    print("Warning: Could not load 'stomp.wav'. Placeholder used.")
    using_placeholder_sounds = True
try:
    hit_sound = pygame.mixer.Sound('assets/sounds/hit.wav')
except pygame.error:
    print("Warning: Could not load 'hit.wav'. Placeholder used.")
    using_placeholder_sounds = True

try:
    pygame.mixer.music.load('assets/sounds/music.ogg')
    pygame.mixer.music.set_volume(0.5) # Adjust volume (0.0 to 1.0)
    pygame.mixer.music.play(-1) # Play indefinitely
except pygame.error:
    print("Warning: Could not load or play 'music.ogg'. No background music.")
    using_placeholder_sounds = True

if using_placeholder_sounds:
    print("One or more sound files failed to load. Game will run without some/all sounds.")


# --- Game Constants ---
# Physics & Gameplay
GRAVITY = 0.8
JUMP_POWER = -18
ENEMY_SPEED = 1.5
STOMP_THRESHOLD = 15 # How close player.bottom needs to be to enemy.top for a stomp
BOUNCE_POWER = -10 # Player's upward velocity after a stomp
COIN_SIZE = 20 # Diameter for the coin circle

# Original Colors (kept for reference or if some entities don't get new colors)
PLAYER_COLOR_OLD = (255, 0, 0) # Old Red for player
PLATFORM_COLOR_OLD = (100, 100, 100) # Old Grey for platforms
ENEMY_COLOR = (150, 75, 0) # Brownish for Goomba
COIN_COLOR = (255, 223, 0) # Gold for Coin

# Global score variable
score = 0
# Game state variables
lives = 3
game_state = 'playing' # 'playing', 'game_over', 'won'


# Helper function to draw text
def draw_text(text, font_obj, color, surface, x, y, center_align=False):
    """Renders text and blits it to a surface."""
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center_align:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


# Platform class
class Platform(pygame.sprite.Sprite):
    """Represents a static platform in the game."""
    def __init__(self, x, y, width, height, color=BRICK_PLATFORM_COLOR): # Default to new brick color
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Player class
class Player(pygame.sprite.Sprite):
    """Represents the player character (Mario)."""
    def __init__(self):
        super().__init__()
        # Player's rect defines collision box and overall size. Drawing is custom.
        self.rect = pygame.Rect(0, 0, 30, 30) # Overall size 30x30
        # self.image is not strictly needed if draw() is fully custom.
        # Making it transparent can avoid issues if it's accidentally drawn.
        self.image = pygame.Surface([self.rect.width, self.rect.height], pygame.SRCALPHA)
        self.image.fill((0,0,0,0)) # Transparent fill

        self.initial_x = 50
        self.initial_y = screen_height - self.rect.height - 40 # Initial y, aligns with top of ground platform
        self.rect.x = self.initial_x
        self.rect.y = self.initial_y
        self.velocity_y = 0
        self.is_on_ground = False # Will be set true if starting on a platform / by collision
        self.movement_speed = 5

    def reset_position(self):
        """Resets player to their initial starting position."""
        self.rect.x = self.initial_x
        self.rect.y = self.initial_y
        self.velocity_y = 0
        self.is_on_ground = False # Let collision detection determine this next frame

    def update(self, platforms_list, enemies_list, coins_list):
        """Handles player movement, physics, and interactions."""
        global score, lives, game_state # Needed to modify global game variables
        keys = pygame.key.get_pressed()

        # --- Horizontal Movement ---
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.movement_speed
        if keys[pygame.K_RIGHT]:
            dx = self.movement_speed

        self.rect.x += dx

        # Horizontal collision detection
        for platform in platforms_list:
            if self.rect.colliderect(platform.rect):
                if dx > 0: # Moving right
                    self.rect.right = platform.rect.left
                elif dx < 0: # Moving left
                    self.rect.left = platform.rect.right

        # Vertical movement & Collision
        # Assume not on ground unless collision detected below
        self.is_on_ground = False

        # Apply gravity if not already on ground from a previous vertical collision check this frame
        # (This condition might be tricky; usually gravity is always applied, then collisions correct it)
        # For now, apply gravity, then check collisions
        self.velocity_y += GRAVITY

        # Jumping
        if keys[pygame.K_SPACE] and self.is_on_ground: # is_on_ground will be True if landed in previous frame
            # This check needs to be before applying gravity or after collision resolution
            # Let's re-evaluate is_on_ground *before* the jump check based on last frame's collisions.
            # The subtask implies is_on_ground is set, then jump is checked.
            # For now, this will mean you can only jump if you *were* on ground at start of this frame's update
             pass # Jump logic will be handled after collision checks determine if on ground

        # Update rect.y based on velocity
        self.rect.y += self.velocity_y

        # Vertical platform collision detection
        for platform in platforms_list:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0: # Falling down
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.is_on_ground = True
                elif self.velocity_y < 0: # Moving up
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0 # Stop upward movement

        # Screen bottom collision (fallback ground)
        if self.rect.bottom >= screen_height: # Check after platform collisions
            self.rect.bottom = screen_height
            self.velocity_y = 0
            self.is_on_ground = True

        # Actual Jump action - needs to be after is_on_ground is correctly determined for the current frame
        if keys[pygame.K_SPACE] and self.is_on_ground and self.velocity_y == 0:
            self.velocity_y = JUMP_POWER
            if jump_sound: jump_sound.play()
            self.is_on_ground = False # Immediately set to false when jumping

        # Player-Enemy collision
        for enemy in enemies_list:
            if self.rect.colliderect(enemy.rect):
                # Stomp condition: Player is falling and hits enemy's top
                if self.velocity_y > 0 and abs(self.rect.bottom - enemy.rect.top) < STOMP_THRESHOLD :
                    enemy.is_active = False # Mark enemy for removal
                    if stomp_sound: stomp_sound.play()
                    self.velocity_y = BOUNCE_POWER # Bounce
                    self.is_on_ground = False # Player is airborne after bounce
                else:
                    # Player hit by enemy from side or below
                    if hit_sound: hit_sound.play()
                    lives -= 1
                    # print(f"Lives: {lives}") # Removed debug print for lives
                    if lives > 0:
                        self.reset_position()
                    else:
                        game_state = 'game_over'
                        if pygame.mixer.music.get_busy(): pygame.mixer.music.stop() # Stop music on game over
                    break # Process only one enemy collision that results in reset per frame

        # Player-Coin collision (only if still playing)
        if game_state == 'playing': # Check game_state before coin interactions
            for coin_item in coins_list: # Renamed to avoid conflict with module 'coin' if any
                if coin_item.is_active and self.rect.colliderect(coin_item.rect):
                    coin_item.is_active = False
                    if coin_sound: coin_sound.play()
                    score += 1
                    print(f"Score: {score}") # Print score to console

            # Check for win condition (all coins collected)
            # Ensure coins_list is not empty before checking 'any' to prevent winning on empty coin list
            if len(coins_list) > 0 and not any(c.is_active for c in coins_list):
                game_state = 'won'
                if pygame.mixer.music.get_busy(): pygame.mixer.music.stop() # Stop music on win

        # Keep player on screen boundaries (horizontal and top)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0: # Prevent jumping through the ceiling
            self.rect.top = 0
            if self.velocity_y < 0: # If moving upwards, stop vertical movement
                self.velocity_y = 0


    def draw(self, surface):
        """Draws the player with a 'body' and 'hat'."""
        # Body (blue rectangle) - slightly shorter to make space for hat
        body_height = self.rect.height * 0.66
        body_y_offset = self.rect.height * 0.34
        pygame.draw.rect(surface, PLAYER_BODY_COLOR,
                         (self.rect.x, self.rect.y + body_y_offset, self.rect.width, body_height))

        # Hat (red rectangle on top)
        hat_height = self.rect.height * 0.33
        pygame.draw.rect(surface, PLAYER_HAT_COLOR,
                         (self.rect.x, self.rect.y, self.rect.width, hat_height))


player = Player()

# Create platforms
platforms = [
    Platform(0, screen_height - 40, screen_width, 40, color=GROUND_PLATFORM_COLOR), # Main ground platform
    Platform(200, screen_height - 150, 150, 20, color=BRICK_PLATFORM_COLOR),       # Elevated platform 1
    Platform(400, screen_height - 250, 100, 20, color=BRICK_PLATFORM_COLOR),       # Elevated platform 2
    Platform(50, screen_height - 350, 120, 20, color=BRICK_PLATFORM_COLOR)         # Elevated platform 3 (was green)
]

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    """Represents an enemy character (Goomba-like)."""
    def __init__(self, x, y, width=35, height=25, color=ENEMY_COLOR, direction=1, speed=ENEMY_SPEED): # Now wider
        super().__init__()
        self.image = pygame.Surface([width, height]) # Use new dimensions
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = direction  # 1 for right, -1 for left
        self.speed = speed
        self.is_active = True # For removal upon stomp

    def update(self, platforms_list):
        if not self.is_active:
            return

        self.rect.x += self.direction * self.speed

        # Collision with platforms (horizontal)
        for platform in platforms_list:
            if self.rect.colliderect(platform.rect):
                if self.direction > 0: # Moving right
                    self.rect.right = platform.rect.left
                else: # Moving left
                    self.rect.left = platform.rect.right
                self.direction *= -1 # Reverse direction
                break

        # Screen edge collision
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        elif self.rect.right > screen_width:
            self.rect.right = screen_width
            self.direction = -1

    def draw(self, surface):
        if self.is_active:
            surface.blit(self.image, self.rect)

# Create enemies
enemies = [
    Enemy(250, screen_height - 150 - 25, direction=-1), # On platform 1, starts moving left
    Enemy(420, screen_height - 250 - 25),             # On platform 2
    Enemy(600, screen_height - 40 - 25)               # On main ground
]

# Coin Class
class Coin(pygame.sprite.Sprite):
    """Represents a collectible coin."""
    def __init__(self, x, y, size=COIN_SIZE, color=COIN_COLOR):
        super().__init__()
        # Rect is still used for collision detection and positioning center
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        # self.image is not strictly needed if draw() is custom.
        # Can make it transparent or a placeholder if group drawing is ever used.
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        self.image.fill((0,0,0,0)) # Transparent
        self.is_active = True

    def draw(self, surface):
        """Draws the coin as a circle if active."""
        if self.is_active:
            pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width // 2)

# Create coins - adjust y positions slightly if COIN_SIZE changed or to prevent overlap
coins = [
    Coin(100, screen_height - 40 - COIN_SIZE),      # On ground platform
    Coin(250, screen_height - 150 - COIN_SIZE),     # On platform 1
    Coin(280, screen_height - 150 - COIN_SIZE),     # On platform 1
    Coin(450, screen_height - 250 - COIN_SIZE),     # On platform 2
    Coin(100, screen_height - 350 - COIN_SIZE),     # On platform 3
    Coin(400, screen_height - 100 - COIN_SIZE // 2) # Floating coin (center y at this height)
]


# Game loop
running = True
clock = pygame.time.Clock() # Add a clock

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN: # Optional: allow restart on key press
            if (game_state == 'game_over' or game_state == 'won') and event.key == pygame.K_r:
                # Reset game (simplified: full re-init might be better for complex games)
                score = 0
                lives = 3
                game_state = 'playing'
                player.reset_position()
                # Reset enemies and coins (need to re-create them or reset their 'is_active' state)
                # For now, let's assume they are reset by re-filtering or re-creating the lists if needed
                # This part can be made more robust. For this task, assuming starting fresh means
                # the existing lists will be filtered and new coins/enemies would be added if level reloaded.
                # A simpler approach for now is that coins/enemies once gone are gone until full script restart.
                # To make R work fully, coin/enemy lists would need to be reset to their initial state.
                # For this subtask, focusing on the game states.
                # Re-activate all coins for a new game attempt after win/loss (if R is pressed)
                for c_obj in coins: c_obj.is_active = True # Makes coins reappear on R (renamed c to c_obj)
                # Enemies would also need similar reset for is_active and position.
                # This is a quick reset for testing. A full game would re-initialize level entities.
                # For now, enemy state won't reset on 'R' without more complex re-initialization.
                if not pygame.mixer.music.get_busy(): # Restart music if it was stopped
                    try:
                        pygame.mixer.music.play(-1)
                    except pygame.error:
                        print("Warning: Could not restart music.")


    if game_state == 'playing':
        # Update
        player.update(platforms, enemies, coins)

        active_enemies = []
        for enemy in enemies:
            if enemy.is_active: # Only update active enemies
                enemy.update(platforms)
                active_enemies.append(enemy)
        enemies = active_enemies

        active_coins = [] # This list is now only used for win condition check if not any.
                          # Player update handles setting coin.is_active = False
        all_coins_collected = True
        for coin in coins: # Iterate original list to check status
            if coin.is_active:
                all_coins_collected = False
                active_coins.append(coin) # Build active_coins for drawing
        # coins = active_coins # No, don't reassign here, player update modifies original list items' state

        if all_coins_collected and len(coins) > 0: # Ensure there were coins to collect
             game_state = 'won'


        # Draw
        screen.fill(BLACK)
        for platform in platforms:
            platform.draw(screen)
        for enemy in enemies: # Draw only active enemies (already filtered)
            enemy.draw(screen)
        for coin_instance in coins: # Draw from the original list, method handles is_active
            coin_instance.draw(screen)
        player.draw(screen)

        # HUD
        draw_text(f"Score: {score}", font, WHITE, screen, 10, 10)
        draw_text(f"Lives: {lives}", font, WHITE, screen, screen_width - 100, 10)

    elif game_state == 'game_over':
        screen.fill(DARK_GREY)
        draw_text("GAME OVER", font, WHITE, screen, screen_width // 2, screen_height // 2 - 50, center_align=True)
        draw_text(f"Final Score: {score}", font, WHITE, screen, screen_width // 2, screen_height // 2 + 10, center_align=True)
        draw_text("Press R to Restart (basic)", font, WHITE, screen, screen_width // 2, screen_height // 2 + 70, center_align=True)


    elif game_state == 'won':
        screen.fill(LIGHT_BLUE)
        draw_text("YOU WIN!", font, WHITE, screen, screen_width // 2, screen_height // 2 - 50, center_align=True)
        draw_text(f"Final Score: {score}", font, WHITE, screen, screen_width // 2, screen_height // 2 + 10, center_align=True)
        draw_text("Press R to Restart (basic)", font, WHITE, screen, screen_width // 2, screen_height // 2 + 70, center_align=True)


    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.mixer.quit() # Uninitialize mixer module
pygame.font.quit() # Uninitialize font module
pygame.quit()
