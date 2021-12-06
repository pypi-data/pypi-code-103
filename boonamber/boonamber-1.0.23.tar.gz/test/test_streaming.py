import argparse
import math
import os
import random
import sys
from boonamber import AmberClient, AmberCloudError


def SignalGenerator(wave='sine', samplerate=1.0, amp=1.0, freq=0.01, phase=0.0, noise=0.0):
    """Producer which generates noisy data from a given waveform.

        Args:
            wave: waveform to use (one of 'sine', 'square', 'triangle')
            samplerate: signal sampling rate
            amp: wave amplitude
            freq: frequency in Hz
            phase: phase offset
            noise: sigma of added Gaussian noise
        
        Produces:
            sequential scalar values from the specified signal
    """

    try:
        sine = lambda x: math.sin(x)
        square = lambda x: math.copysign(1, math.sin(x))
        triangle = lambda x: (2 / math.pi) * math.asin(math.sin(x))
        func = {'sine': sine,
                'square': square,
                'triangle': triangle}[wave]
    except KeyError:
        raise ValueError("unsupported wave: '{}'".format(wave))

    t = 0.0
    while True:
        yield amp * func(2 * math.pi * freq * t + phase) + random.gauss(0.0, noise)
        t += 1 / samplerate


def main():
    signal = SignalGenerator(wave=args.waveform,
                             samplerate=args.sample_rate,
                             amp=args.amp,
                             freq=args.freq,
                             phase=args.phase,
                             noise=args.noise)

    amber = AmberClient(license_file="test.Amber.license")
    amber.password = os.environ['AMBER_TEST_PASSWORD']

    sensor_id = '846f218ab552fa82'
    if args.reset:
        try:
            amber.configure_sensor(sensor_id, feature_count=1, streaming_window_size=25)
        except AmberCloudError as e:
            print(e)
            sys.exit(1)

    try:
        config = amber.get_config(sensor_id)
    except AmberCloudError as e:
        print(e)
        sys.exit(1)
    print("using sensor: {}".format(sensor_id))
    print("configuration: {}".format(config))
    print()

    batch = []
    for sample in signal:
        if random.random() < args.anomaly_prob:
            max_skips = max(1, int((1 / args.freq) / args.sample_rate))
            num_skips = random.randint(1, max_skips)
            for _ in range(num_skips):
                next(signal)

        batch.append(sample)
        if len(batch) < args.batch_size:
            continue

        try:
            results = amber.stream_sensor(sensor_id, batch)
        except AmberCloudError as e:
            print(e)
            sys.exit(1)

        batch = []

        if results['state'] in ["Buffering", "Autotuning"]:
            state_pretty = '{} ({}%)'.format(results['state'], results['progress'])
        else:
            state_pretty = results['state']
        si_pretty = ' '.join("{:4.3f}".format(val) for val in results['SI'])
        print("{}: {} inferences, {} clusters, SI: [{}]".format(
            state_pretty, results['totalInferences'], results['clusterCount'], si_pretty))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-rate', nargs='?', default=0.1, type=float,
                        help="interval between data samples (sec)")
    parser.add_argument('--batch-size', nargs='?', default=10, type=int,
                        help="data samples per stream request")
    parser.add_argument('--waveform', nargs='?', default='sine', type=str,
                        help="synthetic data waveform (one of 'sine', 'square', 'triangle')")
    parser.add_argument('--amp', nargs='?', default=1.0, type=float,
                        help="synthetic data amplitude")
    parser.add_argument('--freq', nargs='?', default=0.33, type=float,
                        help="synthetic data frequency (Hz)")
    parser.add_argument('--phase', nargs='?', default=0.0, type=float,
                        help="synthetic data phase offset (rad)")
    parser.add_argument('--noise', nargs='?', default=0.1, type=float,
                        help="sigma of added Gaussian noise ")
    parser.add_argument('--anomaly-prob', nargs='?', default=1 / 1200, type=float,
                        help="baseline probability of anomaly occuring at any given sample")
    parser.add_argument('--reset', action='store_true',
                        help="if set, reset sensor at start of script")
    args = parser.parse_args()
    main()
