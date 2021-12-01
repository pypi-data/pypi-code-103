import json

import numpy as np
import gym
from gym.error import ResetNeeded
from gym.wrappers import TimeLimit

from pogema.animation import MarlSvgVisualization
from pogema.grid import Grid, CooperativeGrid
from pogema.grid_config import GridConfig


class PogemaBase(gym.Env):

    def step(self, action):
        raise NotImplemented

    def reset(self):
        raise NotImplemented

    def __init__(self, config: GridConfig = GridConfig()):
        # noinspection PyTypeChecker
        self.grid: Grid = None
        self.config = config

        full_size = self.config.obs_radius * 2 + 1
        self.observation_space = gym.spaces.Box(0.0, 1.0, shape=(3, full_size, full_size))
        self.action_space = gym.spaces.Discrete(len(self.config.MOVES))

    def _get_agents_obs(self, agent_id=0):
        return np.concatenate([
            self.grid.get_obstacles(agent_id)[None],
            self.grid.get_positions(agent_id)[None],
            self.grid.get_square_target(agent_id)[None]
        ])

    def check_reset(self):
        if self.grid is None:
            raise ResetNeeded("Please reset environment first!")

    def render(self, mode='human'):
        self.check_reset()
        return self.grid.render(mode=mode)


class PogemaCoopFinish(PogemaBase):
    def __init__(self, config=GridConfig(num_agents=2)):
        super().__init__(config)
        self.num_agents = self.config.num_agents
        self.is_multiagent = True

    def _obs(self):
        return [self._get_agents_obs(index) for index in range(self.config.num_agents)]

    def step(self, action: list):
        assert len(action) == self.config.num_agents
        rewards = []

        infos = [dict() for _ in range(self.config.num_agents)]

        dones = []
        for agent_idx in range(self.config.num_agents):
            agent_done = self.grid.move(agent_idx, action[agent_idx])

            if agent_done:
                rewards.append(1.0)
            else:
                rewards.append(0.0)

            dones.append(agent_done)

        obs = self._obs()
        return obs, rewards, dones, infos

    def reset(self):
        self.grid: CooperativeGrid = CooperativeGrid(grid_config=self.config)
        self.active = {agent_idx: True for agent_idx in range(self.config.num_agents)}
        return self._obs()


class Pogema(PogemaBase):
    def __init__(self, config=GridConfig(num_agents=2)):
        super().__init__(config)
        self.num_agents = self.config.num_agents
        self.is_multiagent = True
        self.active = None

    def _obs(self):
        return [self._get_agents_obs(index) for index in range(self.config.num_agents)]

    def step(self, action: list):
        assert len(action) == self.config.num_agents
        rewards = []

        infos = [dict() for _ in range(self.config.num_agents)]

        dones = []
        for agent_idx in range(self.config.num_agents):
            if self.active[agent_idx]:
                self.grid.move(agent_idx, action[agent_idx])

            on_goal = self.grid.on_goal(agent_idx)
            if on_goal and self.active[agent_idx]:
                rewards.append(1.0)
            else:
                rewards.append(0.0)
            dones.append(on_goal)

        for agent_idx in range(self.config.num_agents):
            if self.grid.on_goal(agent_idx):
                self.grid.hide_agent(agent_idx)
                self.active[agent_idx] = False

            infos[agent_idx]['is_active'] = self.active[agent_idx]

        obs = self._obs()
        return obs, rewards, dones, infos

    def reset(self):
        self.grid: Grid = Grid(grid_config=self.config)
        self.active = {agent_idx: True for agent_idx in range(self.config.num_agents)}
        return self._obs()


class MultiTimeLimit(TimeLimit):
    def step(self, action):
        observation, reward, done, info = self.env.step(action)
        self._elapsed_steps += 1
        if self._elapsed_steps >= self._max_episode_steps:
            for agent_idx in range(self.env.config.num_agents):
                info[agent_idx]["TimeLimit.truncated"] = not done[agent_idx]
                # log.debug('Set TimeLimit.truncated')
            done = [True] * self.num_agents
        return observation, reward, done, info


def main():
    grid_config = GridConfig(num_agents=40, size=8, obs_radius=5, density=0.0, seed=None,
                             map=[
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 0, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                                 [0, 0, 0, 1, 0, 0, 0],
                             ])
    # grid_config = GridConfig(num_agents=1, size=8, obs_radius=1, density=0.0, seed=None,)
    #
    # env = gym.make('Pogema-v0', config=grid_config)
    env = PogemaCoopFinish(config=grid_config)
    env = MultiTimeLimit(env, max_episode_steps=50)
    # env = AnimationMonitor(env)
    # env = MovingObstaclesWrapper(env, mo_config)
    obs = env.reset()

    done = [False, ...]
    to_save = []
    for index in range(50):
        env.render()
        obs, reward, done, info = env.step([env.action_space.sample() for _ in range(env.config.num_agents)])
        to_save.append({
            'obstacles': list([list(map(int, line)) for line in env.grid.obstacles]),
            'positions_xy': list(env.grid.positions_xy),
            'finishes_xy': list(env.grid.finishes_xy),
            'obs_radius': env.config.obs_radius,
        })
        MarlSvgVisualization.draw_frame(env.grid.obstacles,
                                        env.grid.positions_xy,
                                        env.grid.finishes_xy, f'animations/{index}.svg',
                                        env.config.obs_radius)
        if all(done):
            break
    with open('out.json', "w") as f:
        json.dump(to_save, f)
    env.reset()


def m3():
    grid_config = GridConfig(num_agents=8, size=10, obs_radius=3, density=0.3, seed=42,)
    env = Pogema(grid_config, )
    env = MultiTimeLimit(env, max_episode_steps=100000)
    env.reset()

    done = [False, ...]
    to_save = []
    for index in range(50):
        env.render()
        obs, reward, done, info = env.step([env.action_space.sample() for _ in range(env.config.num_agents)])
        to_save.append({
            'obstacles': list([list(map(int, line)) for line in env.grid.obstacles]),
            'positions_xy': list(env.grid.positions_xy),
            'finishes_xy': list(env.grid.finishes_xy),
            'obs_radius': env.config.obs_radius,
        })
        MarlSvgVisualization.draw_frame(env.grid.obstacles,
                                        env.grid.positions_xy,
                                        env.grid.finishes_xy, f'animations/{index}.svg',
                                        env.config.obs_radius)
        if all(done):
            break


if __name__ == '__main__':
    m3()
    # main()
