import fnmatch
from collections import defaultdict

import toml

from libpipe import attrmap


class DataHandler(object):

    def __init__(self, spectral_windows, data_level, obs_ids, remote_hosts, l1_to_l2_config, nodes_distribution):
        self.spectral_windows = spectral_windows
        self.data_level = data_level
        self.obs_ids = obs_ids
        self.remote_hosts = remote_hosts
        self.l1_to_l2_config = l1_to_l2_config
        self.nodes_distribution = nodes_distribution
        self.sw_index = dict(zip(self.get_spectral_windows(), range(len(self.get_spectral_windows()))))

    @staticmethod
    def from_file(filename):
        s = toml.load(filename, _dict=defaultdict)
        for n in ['obs_ids', 'spectral_windows', 'data_level_path']:
            assert n in s, f'{n} need to be defined in {filename}'

        return DataHandler(s['spectral_windows'], s['data_level_path'], s['obs_ids'],
                           s.get('remote_hosts', dict()), s.get('l1_to_l2_config', dict()),
                           s.get('nodes_distribution', dict()))

    def get_obs_ids(self, obs_id_match=None):
        all_obs_ids = self.obs_ids.keys()
        if obs_id_match is None:
            return all_obs_ids
        return attrmap.OrderedSet(obs_id for k in obs_id_match.split(',') for obs_id in fnmatch.filter(all_obs_ids, k))

    def get_nodes_distribution(self):
        return self.nodes_distribution

    def get_obs_ids_and_spectral_windows(self, obs_id_sw_match):
        if ":" in obs_id_sw_match:
            obs_id_sw_match, sws_str = obs_id_sw_match.split(':')
            sws = fnmatch.filter(self.get_spectral_windows(), sws_str)
        else:
            sws = self.get_spectral_windows()

        return self.get_obs_ids(obs_id_sw_match), sws

    def get_sbs(self, sw):
        sb_l, sb_r = self.spectral_windows[sw]
        return range(int(sb_l), int(sb_r) + 1)

    def get_all_hosts(self):
        return [*set(n for l in self.obs_ids.values() for n in l)]

    def get_remote_hosts(self):
        return self.remote_hosts.keys()

    def get_remote_host(self, remote_host):
        assert remote_host in self.remote_hosts, f'{remote_host} needs to be defined'
        return self.remote_hosts[remote_host]['host']

    def get_remote_level(self, remote_host):
        assert remote_host in self.remote_hosts, f'{remote_host} needs to be defined'
        return self.remote_hosts[remote_host]['level']

    def get_remote_password_file(self, remote_host):
        assert remote_host in self.remote_hosts, f'{remote_host} needs to be defined'

        return self.remote_hosts[remote_host]['password_file']

    def get_remote_data_path(self, remote_host):
        assert remote_host in self.remote_hosts, f'{remote_host} needs to be defined'

        return self.remote_hosts[remote_host]['data_path']

    def get_l1_to_l2_config(self, l2_level):
        assert l2_level in self.l1_to_l2_config, f'{l2_level} needs to be defined'

        return self.l1_to_l2_config[l2_level]['dppp_config']

    def get_levels(self):
        return self.data_level.keys()

    def get_spectral_windows(self):
        return self.spectral_windows.keys()

    def get_node(self, obs_id, sw):
        return self.obs_ids[obs_id][self.sw_index[sw]]

    def get_dir_path(self, obs_id, level, sw):
        node = self.get_node(obs_id, sw)
        return f'{self.data_level[level].replace("%NODE%", node)}/{obs_id}/'

    def get_ms_path(self, obs_id, level, sw):
        dir_path = self.get_dir_path(obs_id, level, sw)

        if level.lower().startswith('l1'):
            return [f'{dir_path}/SB{sb}.MS' for sb in self.get_sbs(sw)]
        return [f'{dir_path}/{sw}.MS']

    def get_all_ms_path(self, obs_ids, levels, sws):
        for obs_id in obs_ids:
            for level in levels:
                for sw in sws:
                    yield from self.get_ms_path(obs_id, level, sw)
