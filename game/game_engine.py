
import pygame
from .player import Player
from .obstacle import Obstacle

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)
RED = (200, 40, 40)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40
        self.player = Player(80, self.ground_y)
        self.speed = 6
        self.max_speed = 14
        self.speed_increase_per_frame = 0.003
        self.spawn_interval = 70
        self._spawn_timer = 0
        self.obstacles = []
        self.distance = 0
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            if not self.game_over:
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
            screen,
            BROWN,
            (0, self.ground_y),
            (self.width, self.ground_y),
            4
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
            overlay.fill((255, 255, 255, 190))
            screen.blit(overlay, (0, 0))

            title = self.title_font.render("GAME OVER", True, RED)
            final_score = self.font.render(
                f"Final Score: {self.score}", True, BLACK
            )

            screen.blit(
                title,
                title.get_rect(
                    center=(self.width // 2, self.height // 2 - 40)
                )
            )
            screen.blit(
                final_score,
                final_score.get_rect(
                    center=(self.width // 2, self.height // 2 + 20)
                )
            )
