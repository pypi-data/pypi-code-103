# This file is placed in the Public Domain.


from .tmr import Timer
from .thr import launch


class Repeater(Timer):

    def run(self):
        thr = launch(self.start)
        super().run()
        return thr
