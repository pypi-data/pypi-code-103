# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 13:52:55 2019

@author: chris.kerklaan

# one can import threedigrid easily from here
# module only loads if threedigrid is present
"""

from importlib import util

HAS_THREEDIGRID = util.find_spec("threedigrid")


if HAS_THREEDIGRID:
    from threedigrid.admin.gridresultadmin import GridH5ResultAdmin
    from threedigrid.admin.gridadmin import GridH5Admin

    class Grid:
        def __init__(self, results_folder):
            self.h5_file_path = results_folder + "/gridadmin.h5"
            self.netcdf_file_path = results_folder + "/results_3di.nc"
            self.gr = GridH5ResultAdmin(self.h5_file_path, self.netcdf_file_path)
            self.ga = GridH5Admin(self.h5_file_path)

            self.start_time = 0
            self.end_time = self.gr.nodes.timestamps[-1]

        def level(self, grid_ids=[], model_ids=[], start_time=0, end_time=None):
            if not end_time:
                self.end_time = end_time

            if type(grid_ids) == int:
                return list(
                    self.gr.nodes.filter(id=grid_ids)
                    .timeseries(start_time, self.end_time)
                    .s1.flatten()
                )

            if type(model_ids) == int:
                return list(self.gr.nodes.filter(content_pk=grid_ids).s1.flatten())

            output_dict = {}
            if len(grid_ids) > 0:
                for grid_id in grid_ids:
                    output_dict[grid_id] = list(
                        self.gr.nodes.filter(id=grid_id).s1.flatten()
                    )

            if len(model_ids) > 0:
                for model_id in model_ids:
                    output_dict[model_id] = list(
                        self.gr.nodes.filter(content_pk=model_id).s1.flatten()
                    )

            return output_dict
