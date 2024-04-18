import math
import random
import time

import gymnasium as gym
import numpy as np

from src.navigate_game import NavigateGame


class NavigateEnv(gym.Env):
    def __init__(self, seed=0, board_size=12, silent_mode=True, limit_step=True):
        super().__init__()
        self.game = NavigateGame(seed=seed, board_size=board_size, silent_mode=silent_mode)
        self.game.reset()

        self.action_space = gym.spaces.Discrete(4)  # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT

        self.board_size = board_size
        self.grid_size = board_size ** 2

        self.done = False
        self.over_time = False

        self.step_limit = 500
        self.reward_step_counter = 0
        self.total_step = 0
        self.path = None
        self.total_reward = 0
        self.already_achieve = 1

    def seed(self, sed):
        self.game.seed(sed)
        # self.game.seed(random.randint(0, 1e9))

    def reset(self, seed=None, options=None):
        info = self.game.reset()

        self.done = False
        self.over_time = False
        self.reward_step_counter = 0
        self.total_step = 0
        self.path = set()
        self.already_achieve = 0

        obs = self._generate_observation()
        # return obs, reward, self.done, self.over_time, info
        return obs, info

    def step(self, action):
        self.done, info = self.game.step(action + 1)
        obs = self._generate_observation()

        if self.done:
            return obs, 0, self.done, self.over_time, info

        navigator = info["navigator_pos"]
        prev_navigator = info["prev_navigator_pos"]
        destination = info["destination_pos"]
        reward = 0

        distance = self.game.distance[navigator[0]][navigator[1]]
        prev_distance = self.game.distance[prev_navigator[0]][prev_navigator[1]]
        if distance < prev_distance:
            reward += 1
        else:
            reward -= 2
        # reward += 2 / max(1, distance)

        # if navigator in self.path:
        #     reward -= 1

        # self.path.add(navigator)
        self.total_step += 1
        # self.reward_step_counter += 1

        if info["destination_arrived"]:
            self.already_achieve += 1
            reward += 100 * self.already_achieve ** 0.6
            self.reward_step_counter = 0
            # self.path = set()

        # 处理步数限制导致的游戏结束
        if self.total_step > self.step_limit:
            self.over_time = True

        # 如果智能体撞墙或其他结束游戏的条件
        # elif self.done:
        #     reward -= 10 - self.already_achieve ** 1.1 * 10
        #     reward += min(10, self.total_step ** 0.5)

        reward += self.total_step ** 0.01 - 1

        if not self.game.silent_mode:
            self.game.render()

        return obs, reward, self.done, self.over_time, info

    def render(self):
        self.game.render()

    def get_action_mask(self) -> np.ndarray:
        return np.array([[self._check_action_validity(a) for a in range(self.action_space.n)]])

    # Check if the action is against the current direction of the navigator or is ending the game.
    def _check_action_validity(self, action):
        row, col = self.game.navigator
        action = action + 1
        row += self.game.next_row[action]
        col += self.game.next_col[action]
        game_over = (
                row < 0
                or row >= self.board_size
                or col < 0
                or col >= self.board_size
                or (row, col) in self.game.obstacles
        )

        # return True
        if game_over:
            return False
        else:
            return True

    # def _generate_observation(self):
    #     obs = np.zeros((self.game.board_size, self.game.board_size), dtype=np.float32)
    #     obs[tuple(self.game.navigator)] = 1.0
    #     obs[tuple(self.game.destination)] = 100
    #     for obstacle in self.game.obstacles:
    #         obs[tuple(obstacle)] = -1.0
    #     return obs

    def _generate_observation(self):
        pass

# Test the environment using random actions
# NUM_EPISODES = 100
# RENDER_DELAY = 0.001
# from matplotlib import pyplot as plt

# if __name__ == "__main__":
#     env = SnakeEnv(silent_mode=False)

# # Test Init Efficiency
# print(MODEL_PATH_S)
# print(MODEL_PATH_L)
# num_success = 0
# for i in range(NUM_EPISODES):
#     num_success += env.reset()
# print(f"Success rate: {num_success/NUM_EPISODES}")

# sum_reward = 0

# # 0: UP, 1: LEFT, 2: RIGHT, 3: DOWN
# action_list = [1, 1, 1, 0, 0, 0, 2, 2, 2, 3, 3, 3]

# for _ in range(NUM_EPISODES):
#     obs = env.reset()
#     done = False
#     i = 0
#     while not done:
#         plt.imshow(obs, interpolation='nearest')
#         plt.show()
#         action = env.action_space.sample()
#         # action = action_list[i]
#         i = (i + 1) % len(action_list)
#         obs, reward, done, info = env.step(action)
#         sum_reward += reward
#         if np.absolute(reward) > 0.001:
#             print(reward)
#         env.render()

#         time.sleep(RENDER_DELAY)
#     # print(info["snake_length"])
#     # print(info["food_pos"])
#     # print(obs)
#     print("sum_reward: %f" % sum_reward)
#     print("episode done")
#     # time.sleep(100)

# env.close()
# print("Average episode reward for random strategy: {}".format(sum_reward/NUM_EPISODES))
