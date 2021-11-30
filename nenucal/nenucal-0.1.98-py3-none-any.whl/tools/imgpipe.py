#!/usr/bin/env python

import os
import sys
import fnmatch
from collections import defaultdict

import toml
import click

from nenucal import tasks, datahandler, msutils, __version__
from nenucal.settings import Settings, ImgSettings

from libpipe import worker


t_file = click.Path(exists=True, dir_okay=False)
t_dir = click.Path(exists=True, file_okay=False)

WSCLEAN_BIN = 'wsclean'


def build_wsclean_cmd(s, ms_in):
    cmd = [WSCLEAN_BIN]
    img_dir = f'{ms_in}/images'
    for key, value in s.items():
        if key == 'name':
            value = f'{img_dir}/{value}'

        if key == 'channels-out':
            n_channels = len(msutils.get_ms_freqs(ms_in)[0])
            if value == 'all':
                value = n_channels
            elif str(value).startswith('every'):
                value = n_channels // int(value[5:])

        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        if isinstance(value, bool):
            cmd.append(f'-{key}')
        else:
            cmd.append(f'-{key} {value}')

    return ' '.join(cmd)


@click.command()
@click.version_option(__version__)
@click.argument('config_file', type=click.Path(exists=True, dir_okay=False))
@click.argument('ms_ins_or_obs_ids', nargs=-1, required=True)
@click.option('--combine', '-c', help='Combine all MS to produce one image (for each SW when applicable).', is_flag=True)
def main(config_file, ms_ins_or_obs_ids, combine):
    ''' Calibration pipeline

        \b
        CONFIG_FILE: Configuration file
        MS_INS_OR_OBS_IDS: Measurement sets to process or OBS_IDS in case you have set data_handler in CONFIG_FILE
    '''
    try:
        s = ImgSettings.load_with_defaults(config_file, check_args=False)
    except toml.TomlDecodeError as e:
        print(f'Error parsing configuration: {e}')
        sys.exit(1)
    
    ms_ins = defaultdict(list)

    if 'data_handler' in s and "config_file" in s["data_handler"] and s["data_handler"]["config_file"]:
        print(f'Using {s["data_handler"]["config_file"]} data handler configuration')
        dh = datahandler.DataHandler.from_file(s['data_handler']['config_file'])
        level = s['data_handler']['data_level']
        for obs_id_str in ms_ins_or_obs_ids:
            obs_ids, sws = dh.get_obs_ids_and_spectral_windows(obs_id_str)
            for sw in sws:
                for obs_id in obs_ids:
                    ms_ins[sw].append(dh.get_ms_path(obs_id, level, sw)[0])
    else:
        ms_ins['SW0'] = ms_ins_or_obs_ids

    w = worker.get_worker_pool('Imaging', nodes=s.worker.nodes, env_file=s.worker.env_file, 
                               max_concurrent=s.worker.max_concurrent, debug=s.worker.debug, 
                               dry_run=s.worker.dry_run)

    for sw in ms_ins.keys():
        if combine:
            base_cmd = build_wsclean_cmd(s.wsclean, ms_ins[sw][-1])
            host = s.get_target_host(ms_ins[sw][-1])
            cmd = f'{base_cmd} {" ".join(ms_ins[sw])}'
            w.add(cmd, run_on_host=host)
        else:
            for ms in ms_ins[sw]:
                base_cmd = build_wsclean_cmd(s.wsclean, ms)
                host = s.get_target_host(ms)
                cmd = f'{base_cmd} {ms}'
                w.add(cmd, run_on_host=host)

    w.execute()

    print('All done !')


if __name__ == '__main__':
    main()

