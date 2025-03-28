import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
GRASS_HEIGHT = 100  # Height of grass area
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Archer vs Aircraft")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)  # Grass color
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)
BLUE = (0, 150, 255)

# Load sound effects
shoot_sound = pygame.mixer.Sound("shoot.wav")  # Arrow release sound
explosion_sound = pygame.mixer.Sound("explosion.wav")  # Explosion sound

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Player (Archer) class
class Player:
    def __init__(self):
        self.width = 30
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - GRASS_HEIGHT + 20  # On grass
        self.speed = 5
        self.color = WHITE

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed

    def draw(self):
        # Draw archer as a triangle (body) with a bow (line)
        pygame.draw.polygon(screen, self.color, [(self.x + self.width // 2, self.y - self.height), 
                                                 (self.x, self.y), 
                                                 (self.x + self.width, self.y)])
        pygame.draw.line(screen, RED, (self.x + self.width // 2, self.y - self.height), 
                         (self.x + self.width // 2, self.y - self.height - 10), 2)  # Bow

# Arrow class
class Arrow:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.length = 20
        self.speed = -8  # Upward
        self.color = YELLOW

    def move(self):
        self.y += self.speed

    def draw(self):
        # Draw arrow as a line with a small triangle head
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.x, self.y + self.length), 2)
        pygame.draw.polygon(screen, self.color, [(self.x, self.y), 
                                                 (self.x - 3, self.y + 5), 
                                                 (self.x + 3, self.y + 5)])

# Enemy (Aircraft) class
class Aircraft:
    def __init__(self):
        self.width = 50
        self.height = 20
        self.x = random.randint(0, WIDTH - self.width)
        self.y = -self.height
        self.speed = random.uniform(2, 4)
        self.color = GRAY

    def move(self):
        self.y += self.speed

    def draw(self):
        # Draw aircraft as a rectangle with wings
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.polygon(screen, self.color, [(self.x, self.y + self.height // 2), 
                                                 (self.x - 10, self.y + self.height), 
                                                 (self.x - 10, self.y)])  # Left wing
        pygame.draw.polygon(screen, self.color, [(self.x + self.width, self.y + self.height // 2), 
                                                 (self.x + self.width + 10, self.y + self.height), 
                                                 (self.x + self.width + 10, self.y)])  # Right wing

# Explosion effect class
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.max_radius = random.randint(30, 50)
        self.color = (255, random.randint(100, 200), 0)
        self.life = 15

    def update(self):
        self.radius += 2
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius), 3)

# Button class for UI
class Button:
    def __init__(self, text, x, y, width, height, color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = font.render(text, True, WHITE)
        self.color = color
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text, (self.rect.x + (self.rect.width - self.text.get_width()) // 2, 
                               self.rect.y + (self.rect.height - self.text.get_height()) // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Game variables
player = Player()
arrows = []
aircrafts = []
explosions = []
score = 0
clock = pygame.time.Clock()
game_state = "menu"

# Buttons
play_button = Button("Play", WIDTH // 2 - 50, HEIGHT // 2 - 60, 100, 40, BLUE, lambda: "playing")
resume_button = Button("Resume", WIDTH // 2 - 50, HEIGHT // 2 - 60, 100, 40, BLUE, lambda: "playing")
exit_button = Button("Exit", WIDTH // 2 - 50, HEIGHT // 2 + 20, 100, 40, RED, lambda: "exit")

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == "playing":
                arrows.append(Arrow(player.x + player.width // 2, player.y - player.height))
                shoot_sound.play()
            elif event.key == pygame.K_p and game_state in ["playing", "paused"]:
                game_state = "paused" if game_state == "playing" else "playing"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if game_state == "menu" and play_button.is_clicked(pos):
                game_state = play_button.action()
                score = 0
                aircrafts.clear()
                arrows.clear()
                explosions.clear()
            elif game_state == "paused" and resume_button.is_clicked(pos):
                game_state = resume_button.action()
            elif (game_state in ["menu", "paused"]) and exit_button.is_clicked(pos):
                running = False

    # Game logic (only when playing)
    if game_state == "playing":
        # Move player
        keys = pygame.key.get_pressed()
        player.move(keys)

        # Update arrows
        for arrow in arrows[:]:
            arrow.move()
            if arrow.y < -arrow.length:
                arrows.remove(arrow)

        # Spawn aircraft (intensity increases with score)
        spawn_rate = min(0.02 + score / 1000, 0.1)
        if random.random() < spawn_rate:
            aircrafts.append(Aircraft())

        # Update aircraft
        for aircraft in aircrafts[:]:
            aircraft.move()
            if aircraft.y + aircraft.height > HEIGHT - GRASS_HEIGHT:
                game_state = "game_over"  # Game over if aircraft touches grass

        # Check collisions
        for arrow in arrows[:]:
            for aircraft in aircrafts[:]:
                distance = math.sqrt((arrow.x - (aircraft.x + aircraft.width // 2)) ** 2 + 
                                     (arrow.y - (aircraft.y + aircraft.height // 2)) ** 2)
                if distance < aircraft.width / 2 + arrow.length / 2:
                    arrows.remove(arrow)
                    aircrafts.remove(aircraft)
                    explosions.append(Explosion(aircraft.x + aircraft.width // 2, aircraft.y + aircraft.height // 2))
                    explosion_sound.play()
                    score += 10
                    break

        # Update explosions
        for explosion in explosions[:]:
            explosion.update()
            if explosion.life <= 0:
                explosions.remove(explosion)

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - GRASS_HEIGHT, WIDTH, GRASS_HEIGHT))  # Grass

    if game_state == "menu":
        title = title_font.render("Archer vs Aircraft", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 150))
        play_button.draw()
        exit_button.draw()
    elif game_state == "paused":
        paused_text = title_font.render("Paused", True, WHITE)
        screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2 - 150))
        resume_button.draw()
        exit_button.draw()
    elif game_state == "playing":
        player.draw()
        for arrow in arrows:
            arrow.draw()
        for aircraft in aircrafts:
            aircraft.draw()
        for explosion in explosions:
            explosion.draw()
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
    elif game_state == "game_over":
        game_over_text = title_font.render("Game Over!", True, WHITE)
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.flip()
        pygame.time.wait(3000)  # Show for 3 seconds
        game_state = "menu"

    # Update display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Quit Pygame
pygame.quit()