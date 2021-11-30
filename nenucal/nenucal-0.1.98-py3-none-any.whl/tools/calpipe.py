#!/usr/bin/env python

import os
import sys
import fnmatch

import toml
import click

from nenucal import tasks
from nenucal import datahandler
from nenucal import __version__
from nenucal.settings import Settings

t_file = click.Path(exists=True, dir_okay=False)
t_dir = click.Path(exists=True, file_okay=False)

tasks_help = '\n'.join([f'  {name.ljust(17)}{desc}' for name, desc in tasks.get_all_tasks_descriptions().items()])


@click.command()
@click.version_option(__version__)
@click.argument('config_file', type=click.Path(exists=True, dir_okay=False))
@click.argument('ms_ins_or_obs_ids', nargs=-1, required=True)
def main(config_file, ms_ins_or_obs_ids):
    ''' Calibration pipeline

        \b
        CONFIG_FILE: Configuration file
        MS_INS_OR_OBS_IDS: Measurement sets to process or OBS_IDS in case you have set data_handler in CONFIG_FILE
    '''
    try:
        s = Settings.load_with_defaults(config_file, with_type_keyword=True, check_args=False)
    except toml.TomlDecodeError as e:
        print(f'Error parsing configuration: {e}')
        sys.exit(1)

    s_default = Settings.get_defaults()

    if 'steps' not in s:
        print(f'Error: a "steps" list is required in {config_file}')
        sys.exit(1)

    if 'worker' not in s:
        s['worker'] = s_default['worker']
        # print(f'Error: a "worker" section is required in {config_file}')
        # sys.exit(1)

    if 'sky_model' not in s:
        s['sky_model'] = s_default['sky_model']
        # print(f'Error: a "sky_model" section is required in {config_file}')
        # sys.exit(1)

    if 'data_handler' in s and "config_file" in s["data_handler"] and s["data_handler"]["config_file"]:
        print(f'Using {s["data_handler"]["config_file"]} data handler configuration')
        dh = datahandler.DataHandler.from_file(s['data_handler']['config_file'])
        level = s['data_handler']['data_level']
        ms_ins = []
        for obs_id_str in ms_ins_or_obs_ids:
            obs_ids, sws = dh.get_obs_ids_and_spectral_windows(obs_id_str)
            ms_ins.extend(dh.get_all_ms_path(obs_ids, [level], sws))
    else:
        ms_ins = ms_ins_or_obs_ids

    all_tasks = tasks.get_all_tasks()

    for step in s.steps:
        if step not in s.keys():
            print(f'Error: step {step} is not known in {config_file}')
            sys.exit(1)
        if not ('type' in s[step].keys() and s[step].type in all_tasks) and step not in all_tasks:
            print(f'Error: type not given or unknown for step {step} in {config_file}')
            print(f'Possible type: {",".join(all_tasks)}')
            sys.exit(1)

    for step in s.steps:
        if 'type' in s[step].keys() and s[step].type in all_tasks:
            t = s[step].type
        elif step in all_tasks:
            t = step

        ms_ins = all_tasks[t](s[step], s.worker, s.sky_model).run(ms_ins)

        if not ms_ins:
            print('\nError: no MS to process.')
            sys.exit(1)
