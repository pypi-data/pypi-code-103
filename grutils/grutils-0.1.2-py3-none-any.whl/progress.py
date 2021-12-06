#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Progress:
    def __init__(self):
        self.curr = 0
        self.max = 10000
        self.progress_bar = None

    def set_process_bar(self, process_bar):
        self.progress_bar = process_bar
        if self.progress_bar is not None:
            self.progress_bar["value"] = self.curr
            self.progress_bar["maximum"] = self.max

    def set(self, val: int):
        if val < 0:
            val = 0

        self.curr = val
        print("percent:", self.curr_percent())
        if self.progress_bar is not None:
            self.progress_bar["value"] = min(self.curr, self.max)
            self.progress_bar.update()

    def set_percent(self, percent: float):
        self.set(int(percent * self.max))

    def curr_percent(self):
        return float(self.curr) / float(self.max)

    def increase_percent(self, delta_percent: float):
        percent = self.curr_percent() + delta_percent
        self.set_percent(percent)

    def reset(self):
        self.set(0)

    def finish(self):
        self.set(self.max)

    def remaining(self):
        return self.max - self.curr

    def remaining_percent(self):
        return 1.0 - self.curr_percent()


shared_progress = Progress()
