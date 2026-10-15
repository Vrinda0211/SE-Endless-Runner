
import pygame
from .player import Player
from .obstacle import Obstacle

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)
RED = (200, 40, 40)
GRAY = (100, 100, 100)

DIFFICULTIES = {
    "1": ("Easy", 4, 10, 90),
    "2": ("Medium", 6, 14, 70),
    "3": ("Hard", 9, 18, 50)
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40
        self.font = pygame.font.SysFont("Arial", 26)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.difficulty_font = pygame.font.SysFont("Arial", 24)
        self.difficulty = "Medium"
        self.game_over = False
        self.reset_game(self.difficulty)

    def reset_game(self, difficulty):
        self.difficulty = difficulty
        settings = next(
            values for values in DIFFICULTIES.values()
            if values[0] == difficulty
        )
        self.speed = settings[1]
        self.max_speed = settings[2]
        self.spawn_interval = settings[3]
        self.speed_increase_per_frame = 0.003
        self.player = Player(80, self.ground_y)
        self.obstacles = []
        self._spawn_timer = 0
        self.distance = 0
        self.score = 0
        self.game_over = False

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.game_over:
            if event.key == pygame.K_1:
                self.reset_game("Easy")
            elif event.key == pygame.K_2:
                self.reset_game("Medium")
            elif event.key == pygame.K_3:
                self.reset_game("Hard")
            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.jump()

    def handle_input(self):
        pass

    def update(self):
        if self.game_over:
            return

        self.speed = min(
            self.speed + self.speed_increase_per_frame,
            self.max_speed
        )

        self.player.update()
        self._spawn_timer += 1

        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.obstacles.append(
                Obstacle(self.width, self.ground_y, self.speed)
            )

        player_rect = self.player.rect()

        for obstacle in self.obstacles:
            previous_x = obstacle.x
            obstacle.speed = self.speed
            obstacle.move()
            current_x = obstacle.x

            swept_rect = pygame.Rect(
                min(previous_x, current_x),
                obstacle.y,
                obstacle.width + abs(previous_x - current_x),
                obstacle.height
            )

            if swept_rect.colliderect(player_rect):
                self.game_over = True
                return

        for obstacle in self.obstacles:
            if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                obstacle.scored = True
                self.score += 1

        self.obstacles = [
            obstacle for obstacle in self.obstacles
            if not obstacle.off_screen()
        ]

        self.distance += self.speed

    def render(self, screen):
        pygame.draw.line(
            screen, BROWN,
            (0, self.ground_y),
            (self.width, self.ground_y), 4
        )

        pygame.draw.rect(screen, WHITE, self.player.rect())

        for obstacle in self.obstacles:
            pygame.draw.rect(screen, DARK_GREEN, obstacle.rect())

        score_text = self.font.render(
            f"Score: {self.score}", True, BLACK
        )
        screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface(
                (self.width, self.height), pygame.SRCALPHA
            )
            overlay.fill((255, 255, 255, 210))
            screen.blit(overlay, (0, 0))

            title = self.title_font.render("GAME OVER", True, RED)
            final_score = self.font.render(
                f"Final Score: {self.score}", True, BLACK
            )
            difficulty_text = self.font.render(
                f"Difficulty: {self.difficulty}", True, BLACK
            )
            instructions = [
                "Choose a difficulty to play again:",
                "1 - Easy",
                "2 - Medium",
                "3 - Hard",
                "ESC - Quit"
            ]

            screen.blit(
                title,
                title.get_rect(
                    center=(self.width // 2, self.height // 2 - 115)
                )
            )
            screen.blit(
                final_score,
                final_score.get_rect(
                    center=(self.width // 2, self.height // 2 - 65)
                )
            )
            screen.blit(
                difficulty_text,
                difficulty_text.get_rect(
                    center=(self.width // 2, self.height // 2 - 30)
                )
            )

            for i, line in enumerate(instructions):
                text = self.difficulty_font.render(line, True, GRAY if i == 0 else BLACK)
                screen.blit(
                    text,
                    text.get_rect(
                        center=(
                            self.width // 2,
                            self.height // 2 + 10 + i * 30
                        )
                    )
                )
