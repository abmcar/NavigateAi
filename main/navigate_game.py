import os
import sys
import random

import numpy as np

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from pygame import mixer


class NavigateGame:
    def __init__(self, seed=0, board_size=12, silent_mode=True):
        self.board_size = board_size
        self.grid_size = self.board_size ** 2
        self.cell_size = 40
        self.width = self.height = self.board_size * self.cell_size

        self.border_size = 20
        self.display_width = self.width + 2 * self.border_size
        self.display_height = self.height + 2 * self.border_size + 40

        self.silent_mode = silent_mode
        if not silent_mode:
            pygame.init()
            pygame.display.set_caption("Navigate Game")
            self.screen = pygame.display.set_mode((self.display_width, self.display_height))
            self.font = pygame.font.Font(None, 36)

            # 加载音效
            mixer.init()
            self.sound_eat = mixer.Sound("sound/eat.wav")
            self.sound_game_over = mixer.Sound("sound/game_over.wav")
            self.sound_victory = mixer.Sound("sound/victory.wav")
        else:
            self.screen = None
            self.font = None

        self.navigator = None
        self.non_navigator = None

        self.direction = None
        self.score = 0
        self.destination = None
        self.seed_value = seed

        random.seed(seed)  # Set random seed.

        self.reset()

    def seed(self, sed):
        random.seed(sed)  # Set random seed.

    def reset(self):
        # 初始化开始位置为中心
        self.navigator = (self.board_size // 2, self.board_size // 2)
        # 其余空余位置
        self.non_navigator = set([(row, col) for row in range(self.board_size) for col in range(self.board_size) if
                                  (row, col) != self.navigator])

        # 初始方向（下一步要走的方向）
        self.direction = "NONE"
        self.destination = self._generate_destination()
        self.score = 0

        destination_arrived = (self.navigator == self.destination)

        info = {
            "navigator_pos": self.navigator,
            "destination_pos": np.array(self.destination),
            "destination_arrived": destination_arrived
        }
        return info

    # def step(self, action):
    #     # 从键盘动作得到下一步的方向
    #     self._update_direction(action)
    #
    #     # 移动 Navigator 位置
    #     row, col = self.navigator
    #     if self.direction == "UP":
    #         row -= 1
    #     elif self.direction == "DOWN":
    #         row += 1
    #     elif self.direction == "LEFT":
    #         col -= 1
    #     elif self.direction == "RIGHT":
    #         col += 1
    #
    #     self.direction = "NONE"
    #
    #     # 检查是否到达终点
    #     if (row, col) == self.destination:
    #         destination_arrived = True
    #         self.score += 10
    #         if not self.silent_mode:
    #             self.sound_eat.play()
    #     else:
    #         destination_arrived = False
    #
    #     # 检查是否撞墙
    #     done = (
    #             row < 0
    #             or row >= self.board_size
    #             or col < 0
    #             or col >= self.board_size
    #     )
    #
    #     if not done:
    #         self.non_navigator.add(self.navigator)
    #         self.non_navigator.remove((row, col))
    #         self.navigator = (row, col)
    #
    #     else:
    #         if not self.silent_mode:
    #             self.sound_game_over.play()
    #
    #     # Add new food after snake movement completes.
    #     if destination_arrived:
    #         self.destination = self._generate_destination()
    #
    #     info = {
    #         "navigator_pos": self.navigator,
    #         "destination_pos": self.destination,
    #         "destination_arrived": destination_arrived
    #     }
    #
    #     return done, info

    def step(self, action):
        # 从键盘动作得到下一步的方向
        self._update_direction(action)

        # 移动 Navigator 位置
        row, col = self.navigator
        if self.direction == "UP":
            row -= 1
        elif self.direction == "DOWN":
            row += 1
        elif self.direction == "LEFT":
            col -= 1
        elif self.direction == "RIGHT":
            col += 1

        self.direction = "NONE"

        # 检查是否撞墙
        done = (
                row < 0
                or row >= self.board_size
                or col < 0
                or col >= self.board_size
        )

        # 检查是否到达终点
        if (row, col) == self.destination:
            destination_arrived = True
            self.score += 10
            if not self.silent_mode:
                self.sound_eat.play()
        else:
            destination_arrived = False

        if not done:
            self.non_navigator.add(self.navigator)
            self.non_navigator.remove((row, col))
            self.navigator = (row, col)

        else:
            if not self.silent_mode:
                self.sound_game_over.play()

        info = {
            "navigator_pos": self.navigator,
            "destination_pos": self.destination,
            "destination_arrived": destination_arrived
        }
        if destination_arrived:
            self.destination = self._generate_destination()
            # done = destination_arrived
            # if self.score >= 100:
            #     done = True

        return done, info

    # 0: UP, 1: LEFT, 2: RIGHT, 3: DOWN
    def _update_direction(self, action):
        if action == 0:
            self.direction = "UP"
        elif action == 1:
            self.direction = "LEFT"
        elif action == 2:
            self.direction = "RIGHT"
        elif action == 3:
            self.direction = "DOWN"

    def _generate_destination(self):
        destination = random.sample(list(self.non_navigator), 1)[0]
        return destination

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.border_size, self.height + 2 * self.border_size))

    def draw_welcome_screen(self):
        title_text = self.font.render("SNAKE GAME", True, (255, 255, 255))
        start_button_text = "START"

        self.screen.fill((0, 0, 0))
        self.screen.blit(title_text, (self.display_width // 2 - title_text.get_width() // 2, self.display_height // 4))
        self.draw_button_text(start_button_text, (self.display_width // 2, self.display_height // 2))
        pygame.display.flip()

    def draw_game_over_screen(self):
        game_over_text = self.font.render("GAME OVER", True, (255, 255, 255))
        final_score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        retry_button_text = "RETRY"

        self.screen.fill((0, 0, 0))
        self.screen.blit(game_over_text,
                         (self.display_width // 2 - game_over_text.get_width() // 2, self.display_height // 4))
        self.screen.blit(final_score_text, (self.display_width // 2 - final_score_text.get_width() // 2,
                                            self.display_height // 4 + final_score_text.get_height() + 10))
        self.draw_button_text(retry_button_text, (self.display_width // 2, self.display_height // 2))
        pygame.display.flip()

    def draw_button_text(self, button_text_str, pos, hover_color=(255, 255, 255), normal_color=(100, 100, 100)):
        mouse_pos = pygame.mouse.get_pos()
        button_text = self.font.render(button_text_str, True, normal_color)
        text_rect = button_text.get_rect(center=pos)

        if text_rect.collidepoint(mouse_pos):
            colored_text = self.font.render(button_text_str, True, hover_color)
        else:
            colored_text = self.font.render(button_text_str, True, normal_color)

        self.screen.blit(colored_text, text_rect)

    def draw_countdown(self, number):
        countdown_text = self.font.render(str(number), True, (255, 255, 255))
        self.screen.blit(countdown_text, (self.display_width // 2 - countdown_text.get_width() // 2,
                                          self.display_height // 2 - countdown_text.get_height() // 2))
        pygame.display.flip()

    def is_mouse_on_button(self, button_text):
        mouse_pos = pygame.mouse.get_pos()
        text_rect = button_text.get_rect(
            center=(
                self.display_width // 2,
                self.display_height // 2,
            )
        )
        return text_rect.collidepoint(mouse_pos)

    def render(self):
        self.screen.fill((0, 0, 0))

        # Draw border
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (self.border_size - 2, self.border_size - 2, self.width + 4, self.height + 4), 2)

        # Draw snake
        self.draw_snake()

        # Draw destination
        r, c = self.destination
        pygame.draw.rect(self.screen, (255, 0, 0), (
            c * self.cell_size + self.border_size, r * self.cell_size + self.border_size, self.cell_size,
            self.cell_size))

        # Draw score
        self.draw_score()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def draw_snake(self):
        # Draw the head
        # head_r, head_c = self.snake[0]
        # head_x = head_c * self.cell_size + self.border_size
        # head_y = head_r * self.cell_size + self.border_size

        r, c = self.navigator
        x = c * self.cell_size + self.border_size
        y = r * self.cell_size + self.border_size

        # Draw the Navigator (Blue)
        pygame.draw.polygon(self.screen, (100, 100, 255), [
            (x + self.cell_size // 2, y),
            (x + self.cell_size, y + self.cell_size // 2),
            (x + self.cell_size // 2, y + self.cell_size),
            (x, y + self.cell_size // 2)
        ])

        eye_size = 3
        eye_offset = self.cell_size // 4
        pygame.draw.circle(self.screen, (255, 255, 255), (x + eye_offset, y + eye_offset), eye_size)
        pygame.draw.circle(self.screen, (255, 255, 255), (x + self.cell_size - eye_offset, y + eye_offset),
                           eye_size)


if __name__ == "__main__":
    import time

    seed = random.randint(0, 1e9)
    game = NavigateGame(seed=seed, silent_mode=False)
    pygame.init()
    game.screen = pygame.display.set_mode((game.display_width, game.display_height))
    pygame.display.set_caption("Navigate Game")
    game.font = pygame.font.Font(None, 36)

    game_state = "welcome"

    # Two hidden button for start and retry click detection
    start_button = game.font.render("START", True, (0, 0, 0))
    retry_button = game.font.render("RETRY", True, (0, 0, 0))

    update_interval = 0.01
    start_time = time.time()
    action = -1

    while True:

        for event in pygame.event.get():

            if game_state == "running":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        action = 0
                    elif event.key == pygame.K_DOWN:
                        action = 3
                    elif event.key == pygame.K_LEFT:
                        action = 1
                    elif event.key == pygame.K_RIGHT:
                        action = 2

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == "welcome" and event.type == pygame.MOUSEBUTTONDOWN:
                if game.is_mouse_on_button(start_button):
                    for i in range(3, 0, -1):
                        game.screen.fill((0, 0, 0))
                        game.draw_countdown(i)
                        game.sound_eat.play()
                        pygame.time.wait(1000)
                    action = -1  # Reset action variable when starting a new game
                    game_state = "running"

            if game_state == "game_over" and event.type == pygame.MOUSEBUTTONDOWN:
                if game.is_mouse_on_button(retry_button):
                    for i in range(3, 0, -1):
                        game.screen.fill((0, 0, 0))
                        game.draw_countdown(i)
                        game.sound_eat.play()
                        pygame.time.wait(1000)
                    game.reset()
                    action = -1  # Reset action variable when starting a new game
                    game_state = "running"

        if game_state == "welcome":
            game.draw_welcome_screen()

        if game_state == "game_over":
            game.draw_game_over_screen()

        if game_state == "running":
            if time.time() - start_time >= update_interval:
                done, _ = game.step(action)
                game.render()
                start_time = time.time()
                action = -1

                if done:
                    game_state = "game_over"

        pygame.time.wait(1)
