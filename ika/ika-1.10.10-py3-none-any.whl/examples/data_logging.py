"""Simple script to run an IKA hotplate at different temperatures and stir rates"""

# Import libraries and modules
import time
import random
from ika.magnetic_stirrer import MagneticStirrer
from pathlib import Path

random.seed(42)


def main():
    # set parameters
    t_initial = 40
    t_current = t_initial
    t_interval = 5
    t_end = 65
    mins = 30
    time_out = mins * 60  # in seconds

    port = 'COM13'  # todo
    path = Path.cwd().joinpath('data_logging_results')  # file name to store results in
    plate = MagneticStirrer(device_port=port,
                            save_path=path)
    plate.record_data_interval = 5  # log data every 5 seconds
    three_minutes = 120  # seconds
    # number of measurements used to determine if temperature has stabilized; calculated so that n is equal to 3
    # minutes worth of measurements
    plate.n = int(three_minutes/plate.record_data_interval)
    plate.start_background_monitoring()  # start recording data

    plate.target_stir_rate = 0
    plate.start_stirring()
    plate.target_temperature = 25
    plate.start_heating()
    # loop to go through temperature steps until max temperature achieved
    while t_current < t_end:
        plate.target_stir_rate = random.randint(100, 300)
        plate.target_temperature = t_current
        print(f'IKA at {plate.target_stir_rate} rpm, go to {t_current} C')
        plate.wait_until_temperature_stable(time_out=time_out)
        t_current += t_interval

    plate.stop_background_monitoring()
    plate.disconnect()


if __name__ == '__main__':
    main()
