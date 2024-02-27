import os
import sys
import random

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from navigate_game_custom_wrapper_mlp import NavigateEnv

NUM_ENV = 32
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

from stable_baselines3.common.callbacks import BaseCallback


class CustomCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(CustomCallback, self).__init__(verbose)

    def _on_step(self) -> bool:
        # 这里可以打印或处理您需要的信息
        # print("Step number: ", self.num_timesteps)
        self.model.env.render()
        return True


# Linear scheduler

def make_env(seed=0):
    def _init():
        env = NavigateEnv(seed=seed)
        env = ActionMasker(env, NavigateEnv.get_action_mask)
        env = Monitor(env)
        env.seed(seed)
        return env

    return _init


def main():
    seed_set = set()
    while len(seed_set) < NUM_ENV:
        seed_set.add(random.randint(0, 1e9))

    env = make_vec_env(make_env(seed=1), n_envs=16)

    # env = NavigateEnv(seed=114514,silent_mode=False)
    # env = ActionMasker(env, NavigateEnv.get_action_mask)
    # env = Monitor(env)
    # env.render()

    model = MaskablePPO(
        "MlpPolicy",
        env,
        # device="mps",
        verbose=1,
        tensorboard_log=LOG_DIR
    )

    # Set the save directory
    save_dir = "trained_models_mlp"
    os.makedirs(save_dir, exist_ok=True)

    checkpoint_interval = 10240 # checkpoint_interval * num_envs = total_steps_per_checkpoint
    checkpoint_callback = CheckpointCallback(save_freq=checkpoint_interval, save_path=save_dir,
                                             name_prefix="ppo_navigate")

    # Writing the training logs from stdout to a file
    original_stdout = sys.stdout
    log_file_path = os.path.join(save_dir, "training_log.txt")
    # with open(log_file_path, 'w') as log_file:
    #     sys.stdout = log_file

    model.learn(
        total_timesteps=int(512 * 16) * 200,
        callback=[checkpoint_callback]
    )
    env.close()

    # Restore stdout
    # sys.stdout = original_stdout

    # Save the final model
    model.save(os.path.join(save_dir, "ppo_navigate_final.zip"))


if __name__ == "__main__":
    main()
