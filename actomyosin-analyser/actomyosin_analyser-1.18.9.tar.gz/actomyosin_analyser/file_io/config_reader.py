import json


class ConfigReader:

    def __init__(self, fname):

        f = open(fname, "rt")
        self.json = json.load(f)

    def get_number_of_time_steps(self):        
        return self.json["n_time_steps"]
        

    def get_force_constants_actin(self):
        bend = self.json["force_constants"]["actin"]["bend"]               
        random_force_factor = self.json["force_constants"]["actin"]["random_force_factor"]
        resting_length = self.json["force_constants"]["actin"]["resting_length"]     
        stretch = self.json["force_constants"]["actin"]["stretch"]
        return (bend, random_force_factor, resting_length, stretch)

    def get_force_constants_van_der_waals(self):
        cut_off = self.json["force_constants"]["van_der_waals"]["cut_off"]
        distance_factor = self.json["force_constants"]["van_der_waals"]["distance_factor"]
        return (cut_off, distance_factor)

    def get_actin_properties(self):
        dt_by_drag_coefficient = self.json["actin_properties"]["dt_by_drag_coefficient"]     
        return dt_by_drag_coefficient

    def get_box_sizes(self):
        size_x = self.json["box"]["size_x"]
        size_y = self.json["box"]["size_y"]
        size_z = self.json["box"]["size_z"]
        return(size_x, size_y, size_z)
