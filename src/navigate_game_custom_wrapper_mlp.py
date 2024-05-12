import numpy as np
import gymnasium
from navigate_game_custom_wrapper import NavigateEnv


class NavigateEnvMlp(NavigateEnv):
    def __init__(self, seed, limit_step=False, silent_mode=True):
        super().__init__(seed=seed, limit_step=limit_step, silent_mode=silent_mode)
        self.observation_space = gymnasium.spaces.Box(
            low=-1, high=1,
            shape=(self.game.board_size, self.game.board_size),
            dtype=np.float32
        )  # 0: empty,  1: navigator, -1: destination

    def _generate_observation(self):
        obs = np.zeros((self.game.board_size, self.game.board_size), dtype=np.float32)
        if 0 < self.game.navigator[0] < 12 and 0 < self.game.navigator[1] < 12:
            obs[tuple(self.game.navigator)] = 1.0
        obs[tuple(self.game.destination)] = 100
        for obstacle in self.game.obstacles:
            obs[tuple(obstacle)] = -1.0
        return obs
