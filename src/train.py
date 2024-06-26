import os
import random
import sys

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from sb3_contrib import QRDQN, MaskablePPO, RecurrentPPO
from sb3_contrib.common.wrappers import ActionMasker

from navigate_game_custom_wrapper_mlp import NavigateEnvMlp
from navigate_game_custom_wrapper_cnn import NavigateEnvCnn

NUM_ENV = 8
LOG_DIR = "../output/logs"
os.makedirs(LOG_DIR, exist_ok=True)


def make_env(policy_type="MlpPolicy", seed=0, silent=True):
    def _init():
        if policy_type == "CnnPolicy":
            env = NavigateEnvCnn(seed=seed, silent_mode=silent)
            env = ActionMasker(env, NavigateEnvCnn.get_action_mask)
        else:
            env = NavigateEnvMlp(seed=seed, silent_mode=silent)
            env = ActionMasker(env, NavigateEnvMlp.get_action_mask)
        env = Monitor(env)
        env.seed(seed)
        return env

    return _init


def train(model_type: str, policy_type: str, devices: str = 'cpu', total_steps: int = 10000000):
    env = make_vec_env(make_env(policy_type), n_envs=NUM_ENV,seed=random.randint(0, int(1e9)))
    # env = NavigateEnvCnn(seed=0, silent_mode=False)
    # env = ActionMasker(env, NavigateEnvMlp.get_action_mask)
    if model_type == "QRDQN":
        model = QRDQN(
            policy=policy_type,
            env=env,
            device=devices,
            verbose=10,
            gamma=0.94,
            tensorboard_log=LOG_DIR + "/{}".format(model_type),
        )
    elif model_type == "PPO":
        model = MaskablePPO(
            policy=policy_type,
            env=env,
            device=devices,
            verbose=10,
            gamma=0.95,
            # learning_rate=0.2,
            # batch_size=128,
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
                                             name_prefix="{}_navigate".format(model_type))

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
    # train("QRDQN", "MlpPolicy", "cpu", int(2e7))
    # train("QRDQN", "CnnPolicy", "mps", int(5e7))
    # train("PPO", "MlpPolicy", "cpu", int(2e7))
    train("PPO", "CnnPolicy", "mps", int(2e7))
