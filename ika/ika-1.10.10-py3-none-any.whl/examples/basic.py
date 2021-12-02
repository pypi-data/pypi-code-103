import time
from ika.magnetic_stirrer import MagneticStirrer

port = 'COM5'
plate = MagneticStirrer(device_port=port)
plate.start_stirring()
plate.target_stir_rate = 100
time.sleep(10)
plate.target_stir_rate = 200
plate.stop_stirring()

plate.target_temperature = 20
plate.start_heating()
plate.target_temperature = 19
time.sleep(5)
plate.stop_heating()

plate.disconnect()