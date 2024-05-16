import torch
import torch.nn as nn
from stable_baselines3 import DQN
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class CustomNetwork(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim):
        super(CustomNetwork, self).__init__(observation_space, features_dim)

        self.conv = nn.Sequential(
            nn.Conv2d(3, 4, kernel_size=3, stride=1),
            nn.Conv2d(4, 8, kernel_size=3, stride=1),
        )

        self.mlp = nn.Sequential(
            nn.Linear(32*32*8,1024),
            nn.ReLU(),
            nn.Linear(1024, 256),
            nn.ReLU(),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, features_dim)  # 输出层
        )

    def forward(self, x):
        x = self.conv(x)
        x = torch.flatten(x, 1)
        x = self.mlp(x)
        return x
