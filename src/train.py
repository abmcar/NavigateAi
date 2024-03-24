import os
import sys

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from sb3_contrib import QRDQN, MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from navigate_game_custom_wrapper_mlp import NavigateEnvMlp as NavigateEnv

NUM_ENV = 10
LOG_DIR = "../output/logs"
os.makedirs(LOG_DIR, exist_ok=True)


def make_env(seed=0):
    def _init():
        env = NavigateEnv(seed=seed)
        env = ActionMasker(env, NavigateEnv.get_action_mask)
        env = Monitor(env)
        env.seed(seed)
        return env

    return _init


def train(model_type: str, policy_type: str, devices: str = 'cpu', total_steps: int = 10000000):
    env = make_vec_env(make_env(), n_envs=NUM_ENV)
    if model_type == "QRDQN":
        model = QRDQN(
            policy=policy_type,
            env=env,
            device=devices,
            verbose=1,
            # gamma=,
            tensorboard_log=LOG_DIR + "/{}".format(model_type),
        )
    elif model_type == "PPO":
        model = MaskablePPO(
            policy=policy_type,
            env=env,
            device=devices,
            verbose=1,
            # gamma=,
            tensorboard_log=LOG_DIR + "/{}".format(model_type),
        )
    else:
        print("Model Type Error")
        return
    # Set the save directory
    save_dir = "../output/trained_models_{}/{}".format(policy_type, model_type)
    os.makedirs(save_dir, exist_ok=True)

    checkpoint_interval = 100000  # checkpoint_interval * num_envs = total_steps_per_checkpoint
    checkpoint_callback = CheckpointCallback(save_freq=checkpoint_interval, save_path=save_dir,
                                             name_prefix="qrdqn_navigate")

    # Writing the training logs from stdout to a file
    # original_stdout = sys.stdout
    # log_file_path = os.path.join(save_dir, "training_log.txt")
    # with open(log_file_path, 'w') as log_file:
    #     sys.stdout = log_file

    model.learn(
        total_timesteps=total_steps,
        callback=[checkpoint_callback],
    )
    env.close()

    # Restore stdout
    # sys.stdout = original_stdout

    # Save the final model
    model.save(os.path.join(save_dir, "{}_navigate_final.zip").format(model_type))


if __name__ == "__main__":
    train("QRDQN", "MlpPolicy", "cpu", int(1e7))
    train("QRDQN", "CnnPolicy", "mps", int(1e7))
    train("PPO", "MlpPolicy", "cpu", int(1e7))
    train("PPO", "CnnPolicy", "cpu", int(1e7))
