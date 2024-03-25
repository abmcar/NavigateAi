import time
import random

from sb3_contrib import MaskablePPO
from sb3_contrib import QRDQN

from navigate_game_custom_wrapper_cnn import NavigateEnvCnn
from navigate_game_custom_wrapper_mlp import NavigateEnvMlp

NUM_EPISODE = 10

RENDER = True
FRAME_DELAY = 0.01  # 0.01 fast, 0.05 slow
ROUND_DELAY = 0.5


def test(model_type, policy_type, render):
    seed = random.randint(0, 1e9)
    print(f"Using seed = {seed} for testing.")
    MODEL_PATH = r"../output/trained_models_{}/{}/{}_navigate_final.zip".format(policy_type, model_type, model_type)

    if policy_type == 'CnnPolicy':
        env = NavigateEnvCnn(seed=seed, limit_step=False, silent_mode=render)
    elif policy_type == 'MlpPolicy':
        env = NavigateEnvMlp(seed=seed, limit_step=False, silent_mode=render)
    else:
        print("Policy Type Error")
        return
    # Load the trained model
    if model_type == 'QRDQN':
        model = QRDQN.load(MODEL_PATH)
    elif model_type == 'PPO':
        model = MaskablePPO(MODEL_PATH)
    else:
        print("Model Type Error")
        return

    total_reward = 0
    total_score = 0
    min_score = 1e9
    max_score = 0

    for episode in range(NUM_EPISODE):
        obs, info = env.reset()
        episode_reward = 0
        done = False

        num_step = 0
        info = None

        sum_step_reward = 0

        retry_limit = 9
        print(f"=================== Episode {episode + 1} ==================")

        step_counter = 0
        while not done:
            action, _ = model.predict(obs)

            prev_mask = env.get_action_mask()
            prev_direction = env.game.direction

            num_step += 1
            obs, reward, done, over_time, info = env.step(action)

            if done:
                last_action = ["UP", "LEFT", "RIGHT", "DOWN"][action]
                print(f"Gameover Penalty: {reward:.4f}. Last action: {last_action}")
            elif info["destination_arrived"]:
                print(
                    f"Food obtained at step {num_step:04d}. Food Reward: {reward:.4f}. Step Reward: {sum_step_reward:.4f}")
                sum_step_reward = 0  # Reset step reward accumulator.
            else:
                sum_step_reward += reward  # Accumulate step rewards.

            episode_reward += reward

            if RENDER:
                env.render()
                time.sleep(FRAME_DELAY)

        episode_score = env.game.score
        if episode_score < min_score:
            min_score = episode_score
        if episode_score > max_score:
            max_score = episode_score

        print(
            f"Episode {episode + 1}: Reward Sum: {episode_reward:.4f}, Score: {episode_score}, Total Steps: {num_step}")
        total_reward += episode_reward
        total_score += env.game.score
        if RENDER:
            time.sleep(ROUND_DELAY)

    env.close()
    print(f"=================== Summary ==================")
    print(
        f"Average Score: {total_score / NUM_EPISODE}, Min Score: {min_score}, Max Score: {max_score}, Average reward: {total_reward / NUM_EPISODE}")


if __name__ == '__main__':
    test('QRDQN', 'CnnPolicy', not RENDER)
