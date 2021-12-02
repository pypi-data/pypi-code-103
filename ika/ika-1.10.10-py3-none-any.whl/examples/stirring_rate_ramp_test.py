"""Simple script to run IKA hotplate at set rpm intervals, alternating between on and
off states every 't' seconds."""

# Import libraries and modules
import time
from ika.magnetic_stirrer import MagneticStirrer
import numpy as np

def main():
    # set parameters
    rpm_initial = 200
    rpm_current = rpm_initial
    rpm_interval = 50
    rpm_end = 1000
    time_mix = 5 * 60  # in seconds
    time_wait = 5 * 60  # in seconds

    ika_magnetic_stirrer_port = 'COM8'  # todo
    ika_magnetic_stirrer = MagneticStirrer(device_port=ika_magnetic_stirrer_port)

    # functions to control pump behavior
    def start():
        ika_magnetic_stirrer.target_stir_rate = rpm_current
        ika_magnetic_stirrer.start_stirring()
        print(f'Starting IKA at {rpm_current} rpm')

    def wait():
        print(f'Waiting {time_mix} seconds')
        time.sleep(time_mix)

    def stop_and_wait():
        ika_magnetic_stirrer.stop_stirring()
        print(f"Stopping the motor for {time_wait} seconds and changing stir rate")
        time.sleep(time_wait)

    def sequence():
        start()
        wait()
        stop_and_wait()

    # loop to cycle through sequence until done
    while rpm_current < rpm_end:
        sequence()
        time.sleep(1)
        rpm_current += rpm_interval


if __name__ == '__main__':
    main()
