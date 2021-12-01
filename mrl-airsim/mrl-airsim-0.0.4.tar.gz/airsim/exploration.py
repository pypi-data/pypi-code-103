import numpy as np
import quaternion


class RandomActionExploration:

    def __init__(self, min_a=-1.0, max_a=1.0, dim=1):
        self.min_a = min_a
        self.max_a = max_a
        self.dim = dim

    def get_action(self, timestep):
        val = np.random.uniform(self.min_a, self.min_a, self.dim)
        if self.dim == 1:
            return val[0]
        return val


class TimedRandomActionExploration:

    def __init__(self, switch_timesteps=4, noise_std_dev=1, min_a=-1.0, max_a=1.0, dim=1):
        self.switch_timesteps = switch_timesteps
        self.noise_std_dev = noise_std_dev
        self.dim = dim
        self.min_a = min_a
        self.max_a = max_a
        self.target_action = np.zeros(self.dim)

    def get_action(self, timestep):

        if timestep % self.switch_timesteps == 0:
            self.target_action = np.random.uniform(self.min_a, self.max_a, self.dim)

        val = np.maximum(np.minimum(self.target_action + np.random.normal(scale=self.noise_std_dev, size=self.dim), self.max_a), self.min_a)
        if self.dim == 1:
            return val[0]
        return val


class SplineSteeringExploration:

    def __init__(self, client, spline_name, off_exploration, config):
        self.client = client
        self.spline_name = spline_name
        self.off_exploration = off_exploration
        self.on_off_timesteps = config['on_off_timesteps']
        self.max_steering = config['max_steering']
        self.lookahead = config['path_lookahead']

    def get_action(self, timestep):

        rem_timestep = timestep % (self.on_off_timesteps[0] + self.on_off_timesteps[1])
        is_on = rem_timestep < self.on_off_timesteps[0]
        if is_on:
            spline_heading = self.client.simGetHeadingToSpline(self.spline_name, self.lookahead)
            quat = np.quaternion(spline_heading.w_val, spline_heading.x_val, spline_heading.y_val, spline_heading.z_val)
            rot = quaternion.as_rotation_matrix(quat)
            x_vec = rot[:, 0]
            steering = np.arctan2(x_vec[1], x_vec[0])
            return max(min(steering/self.max_steering, 1.0), -1.0)
        else:
            return self.off_exploration.get_action(timestep)

