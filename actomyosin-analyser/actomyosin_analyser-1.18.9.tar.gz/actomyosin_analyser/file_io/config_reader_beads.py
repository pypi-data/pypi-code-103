import json
import numpy as np


class ConfigReaderBeads:

    param_array_dtype = [('assembly_rate', float),
                         ('box_x', float), ('box_y', float), ('box_z', float),
                         ('disassembly_rate', float),
                         ('k_bend', float), ('k_stretch', float),
                         ('n_beads', int),
                         ('n_steps', int),
                         ('nucleation_rate', float),
                         ('time_step', float)]

    old_param_array_dtype = [('assembly_rate', float),
                             ('box_x', float), ('box_y', float), ('box_z', float),
                             ('disassembly_rate', float),
                             ('k_bend', float), ('k_stretch', float),
                             ('n_beads', int),
                             ('n_steps', int),
                             ('nucleation_rate', float),
                             ('random_step_size', float),
                             ('segment_length', float)]
    
    def __init__(self, fname):        
        with open(fname, "rt") as f:
            self.json = json.load(f)

    def get_number_of_time_steps(self):        
        return self.json["n_steps"]

    def get_box_size(self) -> np.ndarray:
        size_x = self.json["box_size"]["x"]
        size_y = self.json["box_size"]["y"]
        size_z = self.json["box_size"]["z"]
        return np.array([size_x, size_y, size_z])

    def get_bead_diameter(self):
        if 'bead_diameter' in self.json:
            return self.json['bead_diameter']
        return 1.0

    def get_time_step(self):
        if 'time_step' in self.json:
            return self.json['time_step']
        return 1.0

    def get_temperature(self):
        return self.json['temperature']
    
    def get_random_step_size(self):
        return self.json['random_step_size']

    def get_k_stretch(self):
        return self.json['k_stretch']

    def get_k_bend(self):
        return self.json['k_bend']

    def get_segment_length(self):
        return self.json['segment_length']

    def config_to_param_array(self, old_dtype=False) -> np.ndarray:
        if not old_dtype:
            return np.array((self.json['assembly_rate'],
                             self.json['box_size']['x'],
                             self.json['box_size']['y'],
                             self.json['box_size']['z'],
                             self.json['disassembly_rate'],
                             self.json['k_bend'],
                             self.json['k_stretch'],
                             self.json['n_beads'],
                             self.json['n_steps'],
                             self.json['nucleation_rate'],
                             self.json['time_step']),
                            dtype=self.param_array_dtype)
        return np.array((self.json['assembly_rate'],
                         self.json['box_size']['x'],
                         self.json['box_size']['y'],
                         self.json['box_size']['z'],
                         self.json['disassembly_rate'],
                         self.json['k_bend'],
                         self.json['k_stretch'],
                         self.json['n_beads'],
                         self.json['n_steps'],
                         self.json['nucleation_rate'],
                         self.json['random_step_size'],
                         self.json['segment_length']),
                        dtype=self.old_param_array_dtype)
