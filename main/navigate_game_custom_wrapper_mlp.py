import math
import random
import time

import gymnasium as gym
import numpy as np

from navigate_game import NavigateGame


class NavigateEnv(gym.Env):
    def __init__(self, seed=0, board_size=12, silent_mode=True, limit_step=True):
        super().__init__()
        self.game = NavigateGame(seed=seed, board_size=board_size, silent_mode=silent_mode)
        self.game.reset()

        self.action_space = gym.spaces.Discrete(4)  # 0: UP, 1: LEFT, 2: RIGHT, 3: DOWN

        self.observation_space = gym.spaces.Box(
            low=-1, high=1,
            shape=(self.game.board_size, self.game.board_size),
            dtype=np.float32
        )  # 0: empty, 0.5: snake body, 1: navigator, -1: destination

        self.board_size = board_size
        self.grid_size = board_size ** 2  # Max length of snake is board_size^2

        self.done = False
        self.over_time = False

        self.step_limit = 2048
        self.reward_step_counter = 0
        self.total_step = 0
        self.path = list()
        self.total_reward = 0
        self.already_achieve = 1

    def seed(self, sed):
        # self.game.seed(sed)
        self.game.seed(random.randint(0, 1e9))

    def reset(self, seed=None, options=None):
        info = self.game.reset()

        self.done = False
        self.over_time = False
        self.reward_step_counter = 0
        self.total_step = 0
        self.path = []
        self.already_achieve = 0

        obs = self._generate_observation()
        # return obs, reward, self.done, self.over_time, info
        return obs, info

    def step(self, action):
        self.done, info = self.game.step(action)
        obs = self._generate_observation()

        navigator = info["navigator_pos"]
        destination = info["destination_pos"]

        # 更新距离奖励，使用更敏感的距离衡量方法
        distance = abs(destination[0] - navigator[0]) + abs(destination[1] - navigator[1])
        reward = 20 / max(1, distance)  # 奖励与距离负相关

        # 减轻对重复路径的惩罚，允许一定程度的探索
        if navigator in self.path:
            reward -= 10  # 适当减少惩罚

        self.path.append(navigator)
        self.total_step += 1

        # 到达目的地的奖励，奖励与所需步数的倒数平方成正比，同时加入动态因子以鼓励连续成功
        if info["destination_arrived"]:
            reward += 1000 + 1000 / max(1, (self.reward_step_counter))
            self.already_achieve += 1
            self.reward_step_counter = 0
            self.path = []

        # 处理步数限制导致的游戏结束
        if self.total_step > self.step_limit:
            self.over_time = True

        # 如果智能体撞墙或其他结束游戏的条件
        elif self.done:
            # reward -= min(200 * (max(1, self.already_achieve) ** 1.15),
            #               200 * (1.15 ** max(1, self.already_achieve)))  # 碰撞或其他失败条件导致较大惩罚
            reward -= 1000

        return obs, reward, self.done, self.over_time, info

    def render(self):
        self.game.render()

    def get_action_mask(self):
        return np.array([[True for a in range(self.action_space.n)]])

    # Check if the action is against the current direction of the snake or is ending the game.
    def _check_action_validity(self, action):
        row, col = self.game.navigator
        if action == 0:  # UP
            row -= 1
        elif action == 1:  # LEFT
            col -= 1
        elif action == 2:  # RIGHT
            col += 1
        elif action == 3:  # DOWN
            row += 1

        game_over = (
                row < 0
                or row >= self.board_size
                or col < 0
                or col >= self.board_size
        )

        if game_over:
            return False
        else:
            return True

    # EMPTY: 0; SnakeBODY: 0.5; SnakeHEAD: 1; FOOD: -1;
    def _generate_observation(self):
        obs = np.zeros((self.game.board_size, self.game.board_size), dtype=np.float32)
        obs[tuple(self.game.navigator)] = 1.0
        obs[tuple(self.game.destination)] = -1.0
        return obs
