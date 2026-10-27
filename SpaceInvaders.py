
import pygame
import random
import sys

# =====================================
# SPACE INVADERS - COMPLETE PYTHON GAME
# =====================================

pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()
FPS = 60

# Colors
BLACK = (8, 10, 30)
WHITE = (255, 255, 255)
GREEN = (50, 255, 100)
RED = (255, 70, 90)
BLUE = (70, 170, 255)
YELLOW = (255, 230, 60)
PURPLE = (180, 90, 255)
CYAN = (50, 240, 255)

# Fonts
font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 64)

# Stars in the background
stars = [
    (random.randrange(WIDTH), random.randrange(HEIGHT))
    for _ in range(100)
]


def create_aliens():
    """Create a grid of alien invaders."""
    aliens = []

    for row in range(4):
        for col in range(9):
            x = 90 + col * 72
            y = 80 + row * 55

            aliens.append({
                "rect": pygame.Rect(x, y, 36, 28),
                "color": [GREEN, CYAN, PURPLE, RED][row],
                "points": (4 - row) * 10
            })

    return aliens


def reset_game():
    """Reset the game to its starting state."""
    player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 65, 50, 35)

    return {
        "player": player,
        "aliens": create_aliens(),
        "bullets": [],
        "enemy_bullets": [],
        "score": 0,
        "lives": 3,
        "alien_direction": 1,
        "alien_speed": 1,
        "shoot_cooldown": 0,
        "enemy_shoot_timer": 0,
        "game_over": False,
        "won": False
    }


game = reset_game()


def draw_player(rect):
    """Draw a spaceship using simple shapes."""
    pygame.draw.polygon(
        screen, BLUE,
        [
            (rect.centerx, rect.top),
            (rect.left, rect.bottom),
            (rect.centerx, rect.bottom - 10),
            (rect.right, rect.bottom)
        ]
    )

    pygame.draw.rect(
        screen, CYAN,
        (rect.centerx - 5, rect.top + 15, 10, 12)
    )


def draw_alien(alien):
    """Draw a simple pixel-style alien."""
    rect = alien["rect"]
    color = alien["color"]

    pygame.draw.rect(screen, color, rect)

    # Eyes
    pygame.draw.rect(
        screen, BLACK,
        (rect.left + 7, rect.top + 7, 6, 6)
    )
    pygame.draw.rect(
        screen, BLACK,
        (rect.right - 13, rect.top + 7, 6, 6)
    )

    # Legs
    pygame.draw.rect(
        screen, color,
        (rect.left + 3, rect.bottom - 1, 8, 7)
    )
    pygame.draw.rect(
        screen, color,
        (rect.right - 11, rect.bottom - 1, 8, 7)
    )


def draw_text(text, chosen_font, color, x, y, center=False):
    image = chosen_font.render(text, True, color)

    if center:
        position = image.get_rect(center=(x, y))
        screen.blit(image, position)
    else:
        screen.blit(image, (x, y))


def draw_background():
    screen.fill(BLACK)

    for x, y in stars:
        pygame.draw.circle(screen, WHITE, (x, y), 1)

    # Decorative horizon
    pygame.draw.line(
        screen, (30, 50, 90),
        (0, HEIGHT - 15), (WIDTH, HEIGHT - 15), 2
    )


def update_game():
    global game

    if game["game_over"]:
        return

    player = game["player"]
    keys = pygame.key.get_pressed()

    # Move the spaceship
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x -= 5

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x += 5

    player.clamp_ip(screen.get_rect())

    # Shooting cooldown
    if game["shoot_cooldown"] > 0:
        game["shoot_cooldown"] -= 1

    # Move player lasers
    for bullet in game["bullets"][:]:
        bullet.y -= 9

        if bullet.bottom < 0:
            game["bullets"].remove(bullet)

    # Move aliens
    hit_edge = False

    for alien in game["aliens"]:
        alien["rect"].x += (
            game["alien_speed"] * game["alien_direction"]
        )

        if (
            alien["rect"].right >= WIDTH - 10
            or alien["rect"].left <= 10
        ):
            hit_edge = True

    if hit_edge:
        game["alien_direction"] *= -1

        for alien in game["aliens"]:
            alien["rect"].y += 18

    # Enemy lasers
    game["enemy_shoot_timer"] += 1

    if game["enemy_shoot_timer"] >= 45 and game["aliens"]:
        shooter = random.choice(game["aliens"])
        rect = shooter["rect"]

        enemy_bullet = pygame.Rect(
            rect.centerx - 3,
            rect.bottom,
            6, 14
        )

        game["enemy_bullets"].append(enemy_bullet)
        game["enemy_shoot_timer"] = 0

    for bullet in game["enemy_bullets"][:]:
        bullet.y += 5

        if bullet.top > HEIGHT:
            game["enemy_bullets"].remove(bullet)
            continue

        if bullet.colliderect(player):
            game["enemy_bullets"].remove(bullet)
            game["lives"] -= 1

            if game["lives"] <= 0:
                game["game_over"] = True

    # Player lasers hit aliens
    for bullet in game["bullets"][:]:
        for alien in game["aliens"][:]:
            if bullet.colliderect(alien["rect"]):
                game["bullets"].remove(bullet)
                game["aliens"].remove(alien)
                game["score"] += alien["points"]
                break

    # Increase difficulty as aliens are destroyed
    destroyed = 36 - len(game["aliens"])
    game["alien_speed"] = 1 + destroyed // 8

    # Aliens reaching the player means game over
    for alien in game["aliens"]:
        if alien["rect"].bottom >= player.top:
            game["game_over"] = True

    # Victory
    if not game["aliens"]:
        game["game_over"] = True
        game["won"] = True


def draw_game():
    draw_background()

    # Player
    draw_player(game["player"])

    # Aliens
    for alien in game["aliens"]:
        draw_alien(alien)

    # Player lasers
    for bullet in game["bullets"]:
        pygame.draw.rect(screen, YELLOW, bullet)
        pygame.draw.rect(
            screen, WHITE,
            (bullet.x + 1, bullet.y, 2, bullet.height)
        )

    # Enemy lasers
    for bullet in game["enemy_bullets"]:
        pygame.draw.rect(screen, RED, bullet)

    # HUD
    draw_text(
        f"Score: {game['score']}",
        font, WHITE, 20, 15
    )

    draw_text(
        f"Lives: {game['lives']}",
        font, GREEN, WIDTH - 120, 15
    )

    draw_text(
        "MOVE: A/D or ARROWS    SHOOT: SPACE",
        font, CYAN, WIDTH // 2, HEIGHT - 27, center=True
    )

    if game["game_over"]:
        # Dark transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        if game["won"]:
            title = "YOU WIN!"
            title_color = GREEN
        else:
            title = "GAME OVER"
            title_color = RED

        draw_text(
            title, big_font, title_color,
            WIDTH // 2, HEIGHT // 2 - 55, center=True
        )

        draw_text(
            f"Final Score: {game['score']}",
            font, WHITE,
            WIDTH // 2, HEIGHT // 2, center=True
        )

        draw_text(
            "Press R to play again",
            font, YELLOW,
            WIDTH // 2, HEIGHT // 2 + 45, center=True
        )

    pygame.display.flip()


# =====================================
# MAIN GAME LOOP
# =====================================

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if (
                event.key == pygame.K_SPACE
                and not game["game_over"]
                and game["shoot_cooldown"] == 0
            ):
                player = game["player"]

                bullet = pygame.Rect(
                    player.centerx - 3,
                    player.top - 12,
                    6, 16
                )

                game["bullets"].append(bullet)
                game["shoot_cooldown"] = 15

            if event.key == pygame.K_r and game["game_over"]:
                game = reset_game()

    update_game()
    draw_game()

pygame.quit()
sys.exit()
