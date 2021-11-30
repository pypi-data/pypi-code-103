import matplotlib.pyplot as plt
import argparse
from nimutool.data import Plotter, load_data
from pathlib import Path
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', default='ni_data.csv')
    parser.add_argument('--filename2', required=False, help='Optional another file to plot from')
    parser.add_argument('--filename2_offset_sec', required=False, default=0, help='Offset between file1 and file2')
    parser.add_argument('--save-path', required=False, help='Writes plots as png files to the given path')
    args = parser.parse_args()

    src = load_data(args.filename, args.filename2, file2_offset_sec=args.filename2_offset_sec)
    gyro, accelerometer, temps = src.get_timestamped_imu_data()
    dcm, inno, pos, vel, gbias, ascale, status = src.get_ekf_data()
    rpy = src.get_euler_angles()
    gps = src.get_gps_data()

    plotter = Plotter(Path(args.save_path) if args.save_path else None)
    plotter.add_df_plot('stat', 3600 * (180 / np.pi) * gyro.rolling(250 * 30).mean(), 'Angular velocity', 'deg/h')
    plotter.add_df_plot('stat', temps, 'Temperature', '')

    plotter.add_df_plot('raw', gyro, 'Angular velocity', 'rad/s')
    plotter.add_df_plot('raw', accelerometer, 'Linear acceleration', 'm/s^2')
    plotter.add_df_plot('raw', ((accelerometer - accelerometer.mean()) / 9.82 * 1000).rolling(500 * 30).mean(), 'Linear acceleration mean subtracted', 'mg')
    plotter.add_df_plot('ekf', dcm, 'DCM lowest row', '')
    plotter.add_df_plot('ekf', pos, 'EKF position', 'm')
    plotter.add_df_plot('ekf', vel, 'EKF velocity', 'm/s')
    plotter.add_df_plot('ekf2', inno, 'EKF innovation', 'm/s')
    plotter.add_df_plot('ekf2', gbias, 'EKF gyro bias', 'rad/s')
    plotter.add_df_plot('ekf2', ascale, 'EKF ascale', '')
    plotter.add_df_plot('ekf2', status, 'EKF update mode', '')
    plotter.add_df_plot('euler', rpy.filter(regex='roll'), 'Roll', 'deg')
    plotter.add_df_plot('euler', rpy.filter(regex='pitch'), 'Pitch', 'deg')
    plotter.add_df_plot('euler', rpy.filter(regex='yaw'), 'Yaw', 'deg')
    plotter.add_df_plot('gps', gps.filter(regex='gpstime'), 'GPS time', 'seconds')
    plotter.add_df_plot('gps', gps.filter(regex='gps_tp_status'), 'Timepulse status', '')
    plotter.add_df_plot('gps', gps.filter(regex='gps_tp_error_us'), 'Timepulse error', 'us')
    plotter.add_df_plot('gps', gps.filter(regex='gps_tp_vco_tune'), 'VCO tune', '')
    plotter.add_df_plot('gps', gps.filter(regex='gps_tp_cycles'), 'cycles/s', 'Hz')
    plotter.plot(color_by_sensor=False)

    plt.show()
