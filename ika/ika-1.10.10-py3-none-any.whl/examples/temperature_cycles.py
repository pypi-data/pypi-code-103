"""
Script to:
    1. Heat the hot plate to "temperature" degrees C
    2. Hold for time "at_temperature_hold_time_minutes" minutes
    3. Turn off the hot plate for "off_temperature_hold_time_minutes" minutes
    4. Repeat steps 1-3 "n_cycles" number of times

A log file will be produced with everything that happened when this script runs, and a csv file for all the actions
that the plate does, and a csv file for ika properties (i.e. probe temperature) vs time

A temperature probe must be plugged into the IKA and placed in the solution to be monitored.
    If not, then remove the plate.wait_until_temperature_stable() line and replace it with a hardcoded value
"""

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

from ika.magnetic_stirrer import MagneticStirrer


if __name__ == '__main__':
    # todo fill in these variables

    # todo name for the files created by the script
    experiment_name = 'temperature cycles'

    # todo temperature to go to in degrees Celsius
    temperature = 50

    # todo number of times to go to the set temperature
    n_cycles = 5

    # todo maximum time to wait for the plate to get the probe temperature to be at the high temperature and stable
    #  before continuing to hold at the high temperature
    wait_until_probe_temperature_stable_time_minutes = 40

    # todo minutes to hold each temperature at
    at_temperature_hold_time_minutes = 60

    # todo minutes to hold at with heating off
    off_temperature_hold_time_minutes = 120

    # todo ika plate comport
    port = 'COM4'

    # todo wait time frequency - frequency to log the remaining time and current plate temperature during the at
    #  temperature/off temperature waits, and the frequency to check if the heating/off heat steps should end,
    #  in seconds
    wait_time_frequency = 120  # seconds

    # todo path to the the csv file to save temperature vs time data
    file_path = Path(experiment_name)

    # todo stir rate
    stir_rate = 400

    # shouldn't need to edit anything under this line
    # ------------------------------------------------------------

    logger = logging.getLogger(experiment_name)
    logger.setLevel(logging.INFO)
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=format, level=logging.INFO)

    # file logging set up
    LogFilePath = Path(
        fr'{datetime.now().strftime(f"{experiment_name} - %Y-%m-%d %H-%M")}.log')
    handler = logging.FileHandler(str(LogFilePath.absolute()))
    handler.setLevel(logging.INFO)  # todo change log level as needed
    file_format = logging.Formatter(format)
    handler.setFormatter(file_format)
    logger.addHandler(handler)

    plate = MagneticStirrer(device_port=port, save_path=file_path, safe_connect=False)

    # these parameters are for checking if the probe temperature vs time trend is stable.
    # number of measurements taken until a csv of time course data is saved
    plate.save_state_data_interval = 10
    # number of measurements used to check if the trend is stable
    plate.n = 60
    # how high the maximum value the standard deviation and standard error of the mean for the measurements can be in
    # order for the temperature probe over time trend to be considered stable
    plate.std_max = 0.05
    plate.sem_max = 0.05
    # if the plate upper and lower limits are <= 1, then if this is false then the  plate upper and lower limits for
    # checking if the probe temperature over time trend is stable is in absolute (degrees C) values. if this is true
    # and the upper and lower limits are <= 1, then the actual temperature limits for the probe temperature over
    # time trend to be considered is upper or lower * the total range of all the probe temperature measurements
    plate.relative_limits = False
    # how far above/below the probe temperature can be from the target temperature for the probe temperature over
    # time trend to be considered stable
    plate.upper_limit = 0.5
    plate.lower_limit = 0.5
    # the minimum r value the probe temperature over time measurements must have (for linear regression),
    # for the trend to be considered stable
    plate.r_min = None
    # upper and lower limits the probe temperature over time trend can have (for linear regression) for the trend to
    # be considered stable
    plate.slope_upper_limit = None
    plate.slope_lower_limit = None

    # start background monitoring of temperature and stir rate over time to a csv file
    plate.start_background_monitoring()

    # start stirring
    plate.target_stir_rate = stir_rate
    plate.start_stirring()

    logger.info(f'do {n_cycles} temperature cycles: heat to {temperature} C for '
                f'{at_temperature_hold_time_minutes} minutes then turn off heat for '
                f'{off_temperature_hold_time_minutes} minutes')
    for i in range(n_cycles):
        logger.info(f'start temperature cycle {i + 1} / {n_cycles}')
        logger.info(f'heat to {temperature} C')
        plate.target_temperature = temperature
        plate.start_heating()
        logger.info(f'waiting for the probe temperature to stabilize to {temperature} C')
        temperature_stabilized = plate.wait_until_temperature_stable(time_out=(wait_until_probe_temperature_stable_time_minutes * 60))

        if temperature_stabilized:
            logger.info(f'probe temperature stabilized at {temperature} C')
        else:
            logger.info(f'probe temperature did not stabilize at {temperature} C after '
                        f'{wait_until_probe_temperature_stable_time_minutes} minutes, moving onto the next step')

        logger.info(f'wait at temperature for {at_temperature_hold_time_minutes} minutes')
        start_at_temperature_time = datetime.now()
        end_at_temperature_time = start_at_temperature_time + timedelta(minutes=at_temperature_hold_time_minutes)
        while datetime.now() < end_at_temperature_time:
            at_temperature_time_remaining_minutes = round(((end_at_temperature_time - datetime.now()).seconds) / 60, 2)
            logger.info(f'wait at {temperature} C - time remaining: {at_temperature_time_remaining_minutes} '
                        f'minutes - current plate temperature: {plate.hotplate_sensor_temperature} - current probe '
                        f'temperature: {plate.probe_temperature} C')
            time.sleep(wait_time_frequency)
        plate.save_csv_files()

        logger.info(f'turn off heating for {off_temperature_hold_time_minutes} minutes')
        plate.stop_heating()
        start_off_temperature_time = datetime.now()
        end_off_temperature_time = start_off_temperature_time + timedelta(minutes=off_temperature_hold_time_minutes)
        while datetime.now() < end_off_temperature_time:
            off_temperature_time_remaining_minutes = round(((end_off_temperature_time - datetime.now()).seconds) / 60, 2)
            logger.info(f'heat off and wait - time remaining: {off_temperature_time_remaining_minutes} minutes - '
                        f'current plate temperature: {plate.hotplate_sensor_temperature} C - current probe '
                        f'temperature: {plate.probe_temperature} C')
            time.sleep(wait_time_frequency)
        plate.save_csv_files()

        logger.info(f'temperature cycle {i + 1} / {n_cycles} completed')

    plate.stop_stirring()
    plate.stop_background_monitoring()
    plate.save_csv_files()
    logger.info('completed all temperature cycles, script ending')


