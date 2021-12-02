import logging
from ika.magnetic_stirrer import MagneticStirrer
from examples.visualization.magnetic_stirrer_visual import MagneticStirrerVisual
from pathlib import Path


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    test_save_path = Path.cwd().joinpath('temp_stabilization_test')
    Path.mkdir(test_save_path, exist_ok=True)
    ika_magnetic_stirrer_port = 'COM8'  # todo
    # todo pick one of the two below for testing
    # ika_magnetic_stirrer = MagneticStirrer(device_port=ika_magnetic_stirrer_port)
    ika_magnetic_stirrer = MagneticStirrerVisual(device_port=ika_magnetic_stirrer_port,
                                                 save_path=test_save_path,
                                                 )
    ika_magnetic_stirrer.save_temperature_data_interval = 30  # seconds
    ika_magnetic_stirrer.n = 180
    ika_magnetic_stirrer.std_max = 0.05
    ika_magnetic_stirrer.sem_max = 0.05
    ika_magnetic_stirrer.upper_limit = 0.5
    ika_magnetic_stirrer.lower_limit = 0.5
    ika_magnetic_stirrer.r_min = None
    ika_magnetic_stirrer.slope_upper_limit = None
    ika_magnetic_stirrer.slope_lower_limit = None

    stir_rate = 250
    increment = 10
    initial_temp = 35
    current_temp = initial_temp - increment
    final_temp = 60
    time_out = 45 * 60  # seconds

    ika_magnetic_stirrer.target_stir_rate = stir_rate
    ika_magnetic_stirrer.start_stirring()
    ika_magnetic_stirrer.start_background_monitoring()
    ika_magnetic_stirrer.target_temperature = initial_temp
    ika_magnetic_stirrer.start_heating()

    while current_temp < final_temp:
        current_temp += increment
        ika_magnetic_stirrer.target_temperature = current_temp
        temp_stabilized: bool = ika_magnetic_stirrer.wait_until_temperature_stable(time_out=time_out)
        ika_magnetic_stirrer.save_graph_stable_visualized(file_name=f'ika_test_target_{current_temp}')
        logger.info(f'reached stabilized at temperature {current_temp}: {temp_stabilized}')

    ika_magnetic_stirrer.stop_background_monitoring()
    ika_magnetic_stirrer.stop_heating()


if __name__ == '__main__':
    main()
