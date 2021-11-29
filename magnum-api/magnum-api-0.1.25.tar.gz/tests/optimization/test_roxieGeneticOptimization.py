import random
from copy import deepcopy
from unittest import TestCase

import pandas as pd
import numpy as np

from magnumapi.geometry.GeometryChange import GeometryChange
from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.cadata.CableDatabase import CableDatabase
from magnumapi.geometry.SlottedGeometry import SlottedRelativeCosThetaGeometry
from magnumapi.optimization.DesignVariable import GeneticDesignVariable
from magnumapi.optimization.GeneticOptimization import GeneticOptimization, RoxieGeneticOptimization
from tests.resource_files import create_resources_file_path

json_file_path = create_resources_file_path('resources/optimization/config.json')
csv_file_path = create_resources_file_path('resources/optimization/optim_input_enlarged.csv')
optimization_cfg = GeneticOptimization.initialize_config(json_file_path)

json_path = create_resources_file_path('resources/geometry/roxie/16T/16T_rel.json')
cadata_path = create_resources_file_path('resources/geometry/roxie/16T/roxieold_2.cadata')
cadata = CableDatabase.read_cadata(cadata_path)
geometry = GeometryFactory.init_with_json(json_path, cadata)


class TestRoxieGeneticOptimization(TestCase):

    def setUp(self) -> None:
        self.gen_opt = RoxieGeneticOptimization(config=optimization_cfg,
                                                design_variables_df=pd.read_csv(csv_file_path),
                                                geometry=geometry,
                                                model_input_path='',
                                                is_script_executed=True,
                                                output_subdirectory_dir='')

    def test_initialize_population(self):
        # arrange
        np.random.seed(0)

        # act
        pop = self.gen_opt.initialize_population_old()

        # assert
        pop_ref = [0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0,
                   1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0,
                   0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0,
                   0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1]

        self.assertListEqual(pop_ref, pop[0])

    def test_decode_chromosome(self):
        # arrange
        np.random.seed(0)

        # act
        pop = self.gen_opt.initialize_population_old()
        chromosome = self.gen_opt.decode_individual_old(pop[0])

        # assert
        chromosome_ref = {'phi_r:1:2': 5.953125, 'phi_r:1:3': 9.78125, 'phi_r:1:4': 4.75, 'phi_r:2:2': 5.40625,
                          'phi_r:2:3': 6.28125, 'phi_r:3:2': 7.703125, 'phi_r:3:3': 5.734375, 'phi_r:4:2': 6.390625,
                          'alpha_r:1:2': 3.59375, 'alpha_r:1:3': 6.40625, 'alpha_r:1:4': 6.5625, 'alpha_r:2:2': 0.46875,
                          'alpha_r:2:3': 0.9375, 'alpha_r:3:2': 5.78125, 'alpha_r:3:3': 9.6875, 'alpha_r:4:2': 7.8125,
                          'nco:1:1': 3, 'nco:1:2': 2, 'nco:1:3': 1, 'nco:1:4': 0, 'nco:2:1': 6, 'nco:2:2': 9,
                          'nco:2:3': 0, 'nco:3:1': 14, 'nco:3:2': 9, 'nco:3:3': 3, 'nco:4:1': 30, 'nco:4:2': 12}

        self.assertDictEqual(chromosome_ref, chromosome)

    def test_decode_chromosome_with_global_parameter(self):
        # arrange
        np.random.seed(0)
        csv_global_file_path = create_resources_file_path('resources/optimization/optim_input_enlarged_with_global.csv')
        df = pd.read_csv(csv_global_file_path)
        self.gen_opt.design_variables = RoxieGeneticOptimization.initialize_design_variables(df)

        # act
        pop = self.gen_opt.initialize_population_old()
        chromosome = self.gen_opt.decode_individual_old(pop[0])

        # assert
        chromosome_ref = {'phi_r:1:2': 5.953125, 'phi_r:1:3': 9.78125, 'phi_r:1:4': 4.75, 'phi_r:2:2': 5.40625,
                          'phi_r:2:3': 6.28125, 'phi_r:3:2': 5.734375, 'phi_r:4:2': 6.390625, 'alpha_r:1:2': 3.59375,
                          'alpha_r:1:3': 6.40625, 'alpha_r:1:4': 6.5625, 'alpha_r:2:2': 0.46875, 'alpha_r:2:3': 0.9375,
                          'alpha_r:3:2': 9.6875, 'alpha_r:4:2': 7.8125, 'nco:1:1': 3, 'nco:1:2': 2, 'nco:1:3': 1,
                          'nco:1:4': 0, 'nco:2:1': 6, 'nco:2:2': 9, 'nco:2:3': 0, 'nco:3:1': 14, 'nco:3:2': 9,
                          'nco:3:3': 3, 'nco:4:1': 30, 'nco:4:2': 12, 'R_EE': 1.2109375}

        self.assertDictEqual(chromosome_ref, chromosome)

    def test_decode_chromosome_with_global_parameter_multi_index(self):
        # arrange
        np.random.seed(0)
        path_str = 'resources/optimization/optim_input_enlarged_with_global_multi_index.csv'
        csv_global_file_path = create_resources_file_path(path_str)
        df = pd.read_csv(csv_global_file_path)
        self.gen_opt.design_variables = RoxieGeneticOptimization.initialize_design_variables(df)

        # act
        pop = self.gen_opt.initialize_population_old()
        chromosome = self.gen_opt.decode_individual_old(pop[0])

        # assert
        chromosome_ref = {'phi_r:1:2': 5.953125, 'phi_r:1:3': 9.78125, 'phi_r:1:4': 4.75, 'phi_r:2:2': 5.40625,
                          'phi_r:2:3': 6.28125, 'phi_r:3:2': 7.703125, 'phi_r:3:3': 5.734375, 'phi_r:4:2': 6.390625,
                          'alpha_r:1:2': 3.59375, 'alpha_r:1:3': 6.40625, 'alpha_r:1:4': 6.5625, 'alpha_r:2:2': 0.46875,
                          'alpha_r:2:3': 0.9375, 'alpha_r:3:2': 5.78125, 'alpha_r:3:3': 9.6875, 'alpha_r:4:2': 7.8125,
                          'nco:1:1': 3, 'nco:1:2': 2, 'nco:1:3': 1, 'nco:1:4': 0, 'nco:2:1': 6, 'nco:2:2': 9,
                          'nco:2:3': 0, 'nco:3:1': 14, 'nco:3:2': 9, 'nco:3:3': 3, 'nco:4:1': 30, 'nco:4:2': 12,
                          'R_EE': 1.2109375, 'current:-:1': 12257.8125, 'current:-:2': 12257.8125,
                          'current:-:3': 12257.8125, 'current:-:4': 12257.8125, 'current:-:5': 12257.8125,
                          'current:-:6': 12257.8125, 'current:-:7': 12257.8125, 'current:-:8': 12257.8125,
                          'current:-:9': 12257.8125, 'current:-:10': 12257.8125, 'current:-:11': 12257.8125,
                          'current:-:12': 12257.8125}

        self.assertDictEqual(chromosome_ref, chromosome)

    def test_update_parameters(self):
        # arrange
        np.random.seed(0)

        # act
        pop = self.gen_opt.initialize_population_old()
        chromosome = self.gen_opt.decode_individual_old(pop[0])
        block_layer_defs = self.gen_opt.update_model_parameters(chromosome).to_dict()

        # assert
        block_defs_ref = {'block_defs': [
            {'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 3, 'type': 1, 'current': 13500,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 2, 'radius': 25.0, 'alpha_r': 3.59375, 'phi_r': 5.953125, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 3, 'radius': 25.0, 'alpha_r': 6.40625, 'phi_r': 9.78125, 'nco': 1, 'type': 1, 'current': 13500,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 5, 'radius': 39.0, 'alpha_r': 0.0, 'phi_r': 0.36728, 'nco': 6, 'type': 1, 'current': 13500,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 6, 'radius': 39.0, 'alpha_r': 0.46875, 'phi_r': 5.40625, 'nco': 9, 'type': 1, 'current': 13500,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 8, 'radius': 53.0, 'alpha_r': 0, 'phi_r': 0.27026, 'nco': 14, 'type': 1, 'current': 13500,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 9, 'radius': 53.0, 'alpha_r': 5.78125, 'phi_r': 7.703125, 'nco': 9, 'type': 1, 'current': 13500,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 10, 'radius': 53.0, 'alpha_r': 9.6875, 'phi_r': 5.734375, 'nco': 3, 'type': 1, 'current': 13500,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 11, 'radius': 67.45, 'alpha_r': 0, 'phi_r': 0.21236, 'nco': 30, 'type': 1, 'current': 13500,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 12, 'radius': 67.45, 'alpha_r': 7.8125, 'phi_r': 6.390625, 'nco': 12, 'type': 1, 'current': 13500,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}],
            'layer_defs': [{'no': 1, 'symm': 1, 'typexy': 1, 'blocks': [1, 2, 3, 4]},
                           {'no': 2, 'symm': 1, 'typexy': 1, 'blocks': [5, 6, 7]},
                           {'no': 3, 'symm': 1, 'typexy': 1, 'blocks': [8, 9, 10]},
                           {'no': 3, 'symm': 1, 'typexy': 1, 'blocks': [11, 12]}]}

        assert block_defs_ref['block_defs'] == block_layer_defs['block_defs']

    def test_update_parameters_multi_index(self):
        # arrange
        np.random.seed(0)
        path_str = 'resources/optimization/optim_input_enlarged_with_global_multi_index.csv'
        csv_global_file_path = create_resources_file_path(path_str)
        df = pd.read_csv(csv_global_file_path)
        self.gen_opt.design_variables = RoxieGeneticOptimization.initialize_design_variables(df)

        # act
        pop = self.gen_opt.initialize_population_old()
        chromosome = self.gen_opt.decode_individual_old(pop[0])
        block_layer_defs = self.gen_opt.update_model_parameters(chromosome).to_dict()

        # assert
        block_defs_ref = [
            {'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 3, 'type': 1, 'current': 12257.8125,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 2, 'radius': 25.0, 'alpha_r': 3.59375, 'phi_r': 5.953125, 'nco': 2, 'type': 1, 'current': 12257.8125,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 3, 'radius': 25.0, 'alpha_r': 6.40625, 'phi_r': 9.78125, 'nco': 1, 'type': 1, 'current': 12257.8125,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 5, 'radius': 39.0, 'alpha_r': 0.0, 'phi_r': 0.36728, 'nco': 6, 'type': 1, 'current': 12257.8125,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 6, 'radius': 39.0, 'alpha_r': 0.46875, 'phi_r': 5.40625, 'nco': 9, 'type': 1, 'current': 12257.8125,
             'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 8, 'radius': 53.0, 'alpha_r': 0, 'phi_r': 0.27026, 'nco': 14, 'type': 1, 'current': 12257.8125,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 9, 'radius': 53.0, 'alpha_r': 5.78125, 'phi_r': 7.703125, 'nco': 9, 'type': 1, 'current': 12257.8125,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 10, 'radius': 53.0, 'alpha_r': 9.6875, 'phi_r': 5.734375, 'nco': 3, 'type': 1, 'current': 12257.8125,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 11, 'radius': 67.45, 'alpha_r': 0, 'phi_r': 0.21236, 'nco': 30, 'type': 1, 'current': 12257.8125,
             'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 12, 'radius': 67.45, 'alpha_r': 7.8125, 'phi_r': 6.390625, 'nco': 12, 'type': 1,
             'current': 12257.8125, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]

        self.assertListEqual(block_defs_ref, block_layer_defs['block_defs'])

    def test_correct_missing_blocks_in_block_and_layer_definitions(self):
        # arrange
        chromosome = {'nco_r:1:1': 2,
                      'nco_r:1:2': -3}
        json_path = create_resources_file_path('resources/geometry/roxie/16T/16T_rel.json')
        cadata_path = create_resources_file_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)
        geometry = GeometryFactory.init_with_json(json_path, cadata)

        # act
        # # update number of turns per block_index
        geometry = GeometryChange.update_nco_r(geometry, chromosome)

        assert len(geometry.blocks) == 11
        assert geometry.layer_defs[0].blocks == [1, 3, 4]
        assert geometry.layer_defs[1].blocks == [5, 6, 7]
        assert geometry.layer_defs[2].blocks == [8, 9, 10]
        assert geometry.layer_defs[3].blocks == [11, 12]

    def test_update_targeted_optimization_input_geometry(self):
        np.random.seed(1)

        # act
        path_str = 'resources/optimization/optim_input_enlarged_targeted_optimization.csv'
        csv_global_file_path = create_resources_file_path(path_str)
        df = pd.read_csv(csv_global_file_path)
        self.gen_opt.design_variables = RoxieGeneticOptimization.initialize_design_variables(df)
        pop = self.gen_opt.initialize_population_old()
        chromosome = self.gen_opt.decode_individual_old(pop[0])

        # read an input file with geometry definition
        cadata_path = create_resources_file_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)
        json_ref_path = create_resources_file_path('resources/geometry/roxie/16T/16T_rel.json')

        # initialize relative geometry
        geometry_rel = GeometryFactory.init_with_json(json_ref_path, cadata)

        # update phi_r
        geometry_rel = GeometryChange.update_phi_r(geometry_rel, chromosome)

        # update nco_r
        geometry_rel = GeometryChange.update_nco_r(geometry_rel, chromosome)

        # extract absolute geometry
        geometry_abs = geometry_rel.to_abs_geometry()

        # correct block radiality
        geometry_abs = GeometryChange.calculate_radial_alpha(geometry_abs)

        # extract relative geometry
        geometry_rel = geometry_abs.to_rel_geometry()

        # update alpha_rad_r with
        geometry_rel = GeometryChange.update_alpha_radial(geometry_rel, chromosome)

        # assert that the number of turns per layer is the same
        assert 13 == sum([block.block_def.nco for block in geometry_rel.blocks[:4]])
        assert 19 == sum([block.block_def.nco for block in geometry_rel.blocks[4:7]])
        assert 29 == sum([block.block_def.nco for block in geometry_rel.blocks[7:10]])
        assert 39 == sum([block.block_def.nco for block in geometry_rel.blocks[10:]])

    def test_update_model_parameters_targeted(self):
        np.random.seed(1)

        # act
        path_str = 'resources/optimization/optim_input_enlarged_targeted_optimization.csv'
        csv_global_file_path = create_resources_file_path(path_str)
        df = pd.read_csv(csv_global_file_path)
        self.gen_opt.design_variables = RoxieGeneticOptimization.initialize_design_variables(df)
        pop = self.gen_opt.initialize_population_old()
        chromosome = self.gen_opt.decode_individual_old(pop[0])
        geometry_rel = self.gen_opt.update_model_parameters_targeted(chromosome)

        # assert that the number of turns per layer is the same
        assert 13 == sum([block.block_def.nco for block in geometry_rel.blocks[:4]])
        assert 19 == sum([block.block_def.nco for block in geometry_rel.blocks[4:7]])
        assert 29 == sum([block.block_def.nco for block in geometry_rel.blocks[7:10]])
        assert 39 == sum([block.block_def.nco for block in geometry_rel.blocks[10:]])

    def test_update_model_parameters_targeted_error(self):
        np.random.seed(1)

        # act
        path_str = 'resources/optimization/optim_input_enlarged_targeted_optimization.csv'
        csv_global_file_path = create_resources_file_path(path_str)
        df = pd.read_csv(csv_global_file_path)
        self.gen_opt.design_variables = RoxieGeneticOptimization.initialize_design_variables(df)
        pop = [[1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1,
                1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1,
                0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1,
                0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0]]

        chromosome = self.gen_opt.decode_individual_old(pop[0])
        geometry_rel = self.gen_opt.update_model_parameters_targeted(chromosome)

        # assert that the number of turns per layer is the same
        assert 13 == sum([block.block_def.nco for block in geometry_rel.blocks[:3]])
        assert 19 == sum([block.block_def.nco for block in geometry_rel.blocks[3:6]])
        assert 29 == sum([block.block_def.nco for block in geometry_rel.blocks[6:9]])
        assert 39 == sum([block.block_def.nco for block in geometry_rel.blocks[9:]])

    def test_split_list_into_chunks(self):
        # To produce a partition of t into k values:
        #
        # - Generate k-1 uniformly distributed values in the range [0, t].
        #
        # - Sort them, and add 0 at the beginning and t at the end.
        #
        # - Use the adjacent differences as the partition.
        np.random.seed(0)
        t = 30
        k = 4
        partition = RoxieGeneticOptimization.generate_number_random_partition(t, k)

        assert [13, 8, 6, 3] == partition

    def test_generate_chromosome_varying_turns_blocks(self):
        path_str = 'resources/optimization/design_variables_programmable_geometry.csv'
        csv_global_file_path = create_resources_file_path(path_str)
        df = pd.read_csv(csv_global_file_path)
        design_variables = RoxieGeneticOptimization.initialize_design_variables(df)

        chromosome = RoxieGeneticOptimization.generate_random_chromosome_programmable_geometry(design_variables)

        assert len(design_variables) - 8 == len(chromosome) // 6

    def test_decode_chromosome_varying_turns_blocks(self):
        path_str = 'resources/optimization/design_variables_programmable_geometry.csv'
        csv_global_file_path = create_resources_file_path(path_str)
        df = pd.read_csv(csv_global_file_path)
        design_variables = RoxieGeneticOptimization.initialize_design_variables(df)

        chromosome = RoxieGeneticOptimization.generate_random_chromosome_programmable_geometry(design_variables)

        self.gen_opt.design_variables = design_variables
        decoded = self.gen_opt.decode_chromosome_programmable_geometry(chromosome)

        assert decoded['spar_thickness:1:'] == design_variables[0].convert_gene_to_value(chromosome[0:6])
        assert decoded['nco:1:1'] == GeneticDesignVariable.convert_gene_to_int(chromosome[6:12])
        assert decoded['nco:1:2'] == GeneticDesignVariable.convert_gene_to_int(chromosome[12:18])
        assert decoded['nco:1:3'] == GeneticDesignVariable.convert_gene_to_int(chromosome[18:24])
        assert decoded['nco:1:4'] == GeneticDesignVariable.convert_gene_to_int(chromosome[24:30])
        assert decoded['nco:1:5'] == GeneticDesignVariable.convert_gene_to_int(chromosome[30:36])
        assert decoded['nco:1:6'] == GeneticDesignVariable.convert_gene_to_int(chromosome[36:42])
        assert decoded['phi_r:1:2'] == design_variables[9].convert_gene_to_value(chromosome[42:48])
        assert decoded['phi_r:1:3'] == design_variables[10].convert_gene_to_value(chromosome[48:54])
        assert decoded['phi_r:1:4'] == design_variables[11].convert_gene_to_value(chromosome[54:60])
        assert decoded['phi_r:1:5'] == design_variables[12].convert_gene_to_value(chromosome[60:66])
        assert decoded['phi_r:1:6'] == design_variables[13].convert_gene_to_value(chromosome[66:72])
        assert decoded['alpha_rad_r:1:2'] == design_variables[14].convert_gene_to_value(chromosome[72:78])
        assert decoded['alpha_rad_r:1:3'] == design_variables[15].convert_gene_to_value(chromosome[78:84])
        assert decoded['alpha_rad_r:1:4'] == design_variables[16].convert_gene_to_value(chromosome[84:90])
        assert decoded['alpha_rad_r:1:5'] == design_variables[17].convert_gene_to_value(chromosome[90:96])
        assert decoded['alpha_rad_r:1:6'] == design_variables[18].convert_gene_to_value(chromosome[96:102])
        assert decoded['spar_thickness:2:'] == design_variables[19].convert_gene_to_value(chromosome[102:108])
        assert decoded['nco:2:1'] == GeneticDesignVariable.convert_gene_to_int(chromosome[108:114])
        assert decoded['nco:2:2'] == GeneticDesignVariable.convert_gene_to_int(chromosome[114:120])
        assert decoded['nco:2:3'] == GeneticDesignVariable.convert_gene_to_int(chromosome[120:126])
        assert decoded['nco:2:4'] == GeneticDesignVariable.convert_gene_to_int(chromosome[126:132])
        assert decoded['nco:2:5'] == GeneticDesignVariable.convert_gene_to_int(chromosome[132:138])
        assert decoded['phi_r:2:2'] == design_variables[27].convert_gene_to_value(chromosome[138:144])
        assert decoded['phi_r:2:3'] == design_variables[28].convert_gene_to_value(chromosome[144:150])
        assert decoded['phi_r:2:4'] == design_variables[29].convert_gene_to_value(chromosome[150:156])
        assert decoded['phi_r:2:5'] == design_variables[30].convert_gene_to_value(chromosome[156:162])
        assert decoded['alpha_rad_r:2:2'] == design_variables[31].convert_gene_to_value(chromosome[162:168])
        assert decoded['alpha_rad_r:2:3'] == design_variables[32].convert_gene_to_value(chromosome[168:174])
        assert decoded['alpha_rad_r:2:4'] == design_variables[33].convert_gene_to_value(chromosome[174:180])
        assert decoded['alpha_rad_r:2:5'] == design_variables[34].convert_gene_to_value(chromosome[180:186])
        assert decoded['spar_thickness:3:'] == design_variables[35].convert_gene_to_value(chromosome[186:192])
        assert decoded['nco:3:1'] == GeneticDesignVariable.convert_gene_to_int(chromosome[192:198])
        assert decoded['nco:3:2'] == GeneticDesignVariable.convert_gene_to_int(chromosome[198:204])
        assert decoded['nco:3:3'] == GeneticDesignVariable.convert_gene_to_int(chromosome[204:210])
        assert decoded['nco:3:4'] == GeneticDesignVariable.convert_gene_to_int(chromosome[210:216])
        assert decoded['nco:3:5'] == GeneticDesignVariable.convert_gene_to_int(chromosome[216:222])
        assert decoded['phi_r:3:2'] == design_variables[43].convert_gene_to_value(chromosome[222:228])
        assert decoded['phi_r:3:3'] == design_variables[44].convert_gene_to_value(chromosome[228:234])
        assert decoded['phi_r:3:4'] == design_variables[45].convert_gene_to_value(chromosome[234:240])
        assert decoded['phi_r:3:5'] == design_variables[46].convert_gene_to_value(chromosome[240:246])
        assert decoded['alpha_rad_r:3:2'] == design_variables[47].convert_gene_to_value(chromosome[246:252])
        assert decoded['alpha_rad_r:3:3'] == design_variables[48].convert_gene_to_value(chromosome[252:258])
        assert decoded['alpha_rad_r:3:4'] == design_variables[49].convert_gene_to_value(chromosome[258:264])
        assert decoded['alpha_rad_r:3:5'] == design_variables[50].convert_gene_to_value(chromosome[264:270])
        assert decoded['spar_thickness:4:'] == design_variables[51].convert_gene_to_value(chromosome[270:276])
        assert decoded['nco:4:1'] == GeneticDesignVariable.convert_gene_to_int(chromosome[276:282])
        assert decoded['nco:4:2'] == GeneticDesignVariable.convert_gene_to_int(chromosome[282:288])
        assert decoded['nco:4:3'] == GeneticDesignVariable.convert_gene_to_int(chromosome[288:294])
        assert decoded['phi_r:4:2'] == design_variables[57].convert_gene_to_value(chromosome[294:300])
        assert decoded['phi_r:4:3'] == design_variables[58].convert_gene_to_value(chromosome[300:306])
        assert decoded['alpha_rad_r:4:2'] == design_variables[59].convert_gene_to_value(chromosome[306:312])
        assert decoded['alpha_rad_r:4:3'] == design_variables[60].convert_gene_to_value(chromosome[312:318])

    def test_update_model_varying_turns_blocks(self):
        np.random.seed(1)
        # initialize a slotted geometry_rel model
        json_path = create_resources_file_path('resources/geometry/roxie/16T/16T_rel_slotted.json')
        cadata_path = create_resources_file_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)
        geometry_rel = GeometryFactory.init_slotted_with_json(json_path, cadata)

        # initialize design variables
        path_str = 'resources/optimization/design_variables_programmable_geometry.csv'
        csv_global_file_path = create_resources_file_path(path_str)
        df = pd.read_csv(csv_global_file_path)
        design_variables = RoxieGeneticOptimization.initialize_design_variables(df)

        chromosome = RoxieGeneticOptimization.generate_random_chromosome_programmable_geometry(design_variables)

        self.gen_opt.design_variables = design_variables
        decoded = self.gen_opt.decode_chromosome_programmable_geometry(chromosome)

        self.gen_opt.geometry = geometry_rel
        geometry_rel = self.gen_opt.update_model_parameters_programmable_geometry(decoded)

        # assert updated spar_thickness
        assert geometry_rel.layer_defs[0].spar_thickness == decoded['spar_thickness:1:']
        assert geometry_rel.layer_defs[1].spar_thickness == decoded['spar_thickness:2:']
        assert geometry_rel.layer_defs[2].spar_thickness == decoded['spar_thickness:3:']
        assert geometry_rel.layer_defs[3].spar_thickness == decoded['spar_thickness:4:']

        # assert nco blocks
        assert geometry_rel.blocks[0].block_def.nco == decoded['nco:1:1']
        assert geometry_rel.blocks[1].block_def.nco == decoded['nco:1:2']
        assert geometry_rel.blocks[2].block_def.nco == decoded['nco:1:3']
        assert abs(geometry_rel.blocks[0].block_def.phi_r - 1.038258941873985) < 1e-6
        assert abs(geometry_rel.blocks[1].block_def.phi_r - 2.076404240564713) < 1e-6
        assert abs(geometry_rel.blocks[2].block_def.phi_r - 4.920094195468366) < 1e-6
        assert geometry_rel.layer_defs[0].blocks == [1, 2, 3]

        assert geometry_rel.blocks[3].block_def.nco == decoded['nco:2:1']
        assert geometry_rel.blocks[4].block_def.nco == decoded['nco:2:2']
        assert geometry_rel.blocks[5].block_def.nco == decoded['nco:2:3']
        assert geometry_rel.blocks[6].block_def.nco == decoded['nco:2:4']
        assert abs(geometry_rel.blocks[3].block_def.phi_r - 0.6815002146175938) < 1e-6
        assert abs(geometry_rel.blocks[4].block_def.phi_r - 2.6875) < 1e-6
        assert abs(geometry_rel.blocks[5].block_def.phi_r - 4.7175114201345) < 1e-6
        assert abs(geometry_rel.blocks[6].block_def.phi_r - 2.9930119533340758) < 1e-6
        assert geometry_rel.layer_defs[1].blocks == [4, 5, 6, 7]

        assert geometry_rel.blocks[7].block_def.nco == decoded['nco:3:1']
        assert geometry_rel.blocks[8].block_def.nco == decoded['nco:3:2']
        assert geometry_rel.blocks[9].block_def.nco == decoded['nco:3:3']
        assert geometry_rel.blocks[10].block_def.nco == decoded['nco:3:4']
        assert geometry_rel.blocks[11].block_def.nco == decoded['nco:3:5']
        assert abs(geometry_rel.blocks[7].block_def.phi_r - 0.5058179100635234) < 1e-6
        assert abs(geometry_rel.blocks[8].block_def.phi_r - 1.53125) < 1e-6
        assert abs(geometry_rel.blocks[9].block_def.phi_r - 3.31181105191326) < 1e-6
        assert abs(geometry_rel.blocks[10].block_def.phi_r - 1.8474473698327927) < 1e-6
        assert abs(geometry_rel.blocks[11].block_def.phi_r - 3.232528774389529) < 1e-6
        assert geometry_rel.layer_defs[2].blocks == [8, 9, 10, 11, 12]

        assert geometry_rel.blocks[12].block_def.nco == decoded['nco:4:1']
        assert geometry_rel.blocks[13].block_def.nco == decoded['nco:4:2']
        assert geometry_rel.blocks[14].block_def.nco == decoded['nco:4:3']
        assert abs(geometry_rel.blocks[12].block_def.phi_r - 0.3922719871732055) < 1e-6
        assert abs(geometry_rel.blocks[13].block_def.phi_r - 2.84375) < 1e-6
        assert abs(geometry_rel.blocks[14].block_def.phi_r - 1.98580819079271) < 1e-6
        assert geometry_rel.layer_defs[3].blocks == [13, 14, 15]
