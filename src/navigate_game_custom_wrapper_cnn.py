import numpy as np
import gymnasium
from navigate_game_custom_wrapper import NavigateEnv


class NavigateEnvCnn(NavigateEnv):
    def __init__(self, seed, limit_step=False, silent_mode=True):
        super().__init__(seed=seed, limit_step=limit_step, silent_mode=silent_mode)
        self.observation_space = gymnasium.spaces.Box(
            low=0, high=255,
            shape=(36, 36, 3),
            dtype=np.uint8
        )

    def _generate_observation(self):
        obs = np.zeros((self.game.board_size, self.game.board_size), dtype=np.uint8)
        # Stack single layer into 3-channel-image.
        obs = np.stack((obs, obs, obs), axis=-1)
        # Set the snake head to green and the tail to blue
        if (0 <= self.game.navigator[0] < 12 and
            0 <= self.game.navigator[1] < 12):
            obs[self.game.navigator] = [0, 255, 0]
        for obstacle in self.game.obstacles:
            obs[obstacle] = [255, 0, 0]
        # Set the food to red
        obs[self.game.destination] = [0, 0, 255]
        # Enlarge the observation to 84x84
        obs = np.repeat(np.repeat(obs, 3, axis=0), 3, axis=1)
        return obs
