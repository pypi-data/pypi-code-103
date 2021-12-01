import numpy as np
import math


class PIDControl:

    def __init__(self, kp=1.0, kd=0.0, ki=0.0):
        self.kp = kp
        self.kd = kd
        self.ki = ki
        self.last_error = 0.0
        self.error_sum = 0.0
        self.last_target = 0.0

    def get_control(self, measured, target, dt):
        if not np.isclose(self.last_target, target):
            self.error_sum = 0.0
            self.last_error = 0.0
        error = target-measured
        de_dt = (error-self.last_error)/dt
        self.error_sum += error * dt
        self.last_error = error
        self.last_target = target
        return self.kp * error + self.kd * de_dt + self.ki * self.error_sum


class PurePursuitControl:

    def __init__(self, L = 0.9, max_steer_angle=np.pi*0.1389):       # 25 degrees
        self.L = L
        self.max_steer_angle = max_steer_angle

    def get_control(self, target, dt, is_new=False):
        ld = np.linalg.norm(target)
        alpha = math.atan2(target[1], target[2])
        steer_angle = math.atan(2*self.L*math.sin(alpha)/ld)
        return steer_angle/self.max_steer_angle


