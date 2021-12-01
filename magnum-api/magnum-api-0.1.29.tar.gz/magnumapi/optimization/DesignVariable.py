import math
from typing import Union
from enum import Enum, auto

import numpy as np


class DesignVariable:
    """ A DesignVariable class for optimization purposes
    """

    def __init__(self,
                 xl: Union[int, float],
                 xu: Union[int, float],
                 variable: str,
                 layer: int,
                 bcs: str) -> None:
        """ A DesignVariable constructor

        :param xl: lower limit of a design variable
        :param xu: upper limit of a design variable
        :param variable: name of a design variable
        :param layer: layer index; this brakes the compatibility with ROXIE
        :param bcs: block index, range of indices (with -) or no block indication for global variables
        """
        self.xl = xl
        self.xu = xu
        self.variable = variable
        self.layer = layer
        try:
            bcs = str(int(bcs))
        except ValueError:
            bcs = str(bcs)
        self.bcs = bcs

    def get_variable_names(self) -> list:
        """ Method returning a design variable name. There are three output types
        - if bcs string is empty, then the variable name is returned - for global design variables
        - if bcs string contains a dash, then the range of indices is considered
        - if bcs string contains a number, then the variable:bcs name is returned
        - otherwise, an AttributeError is raised

        :return: a list of strings with variable names
        """
        design_variable_type = self.get_variable_type()
        if design_variable_type == DesignVariableType.GLOBAL_VARIABLE:
            return [self.variable]
        elif design_variable_type == DesignVariableType.LAYER_VARIABLE:
            return ["%s:%s:" % (self.variable, self.layer)]
        elif design_variable_type == DesignVariableType.MULTI_TURN_VARIABLE:
            return self._convert_range_of_blocks_into_list()
        elif design_variable_type == DesignVariableType.TURN_VARIABLE:
            return ["%s:%s:%s" % (self.variable, int(self.layer), self.bcs)]
        else:
            raise AttributeError('The design variable has incorrect block index value: %s.' % self.bcs)

    def _convert_range_of_blocks_into_list(self) -> list:
        bcs_ranges = self.bcs.split('-')
        if len(bcs_ranges) != 2:
            raise AttributeError('The block index range definition %s is wrong. Only one hyphen is allowed.' % self.bcs)

        if not bcs_ranges[0].isnumeric():
            raise AttributeError('The lower block index range %s is not a number.' % bcs_ranges[0])

        if not bcs_ranges[1].isnumeric():
            raise AttributeError('The upper block index range %s is not a number.' % bcs_ranges[1])

        lower = int(bcs_ranges[0])
        upper = int(bcs_ranges[1])

        if lower > upper:
            raise AttributeError('The lower index %d is greater than the upper one %d.' % (lower, upper))

        return ['%s:%s:%d' % (self.variable, self.layer, block) for block in range(lower, upper + 1)]

    def get_variable_type(self) -> "DesignVariableType":
        """ Method returning a design variable type: GLOBAL_VARIABLE, LAYER_VARIABLE, MULTI_TURN_VARIABLE, TURN_VARIABLE

        :return: a DesignVariabletype instance
        """
        if (self.bcs == '' or self.bcs == 'nan') and \
                (self.layer == '' or self.layer == 'nan' or math.isnan(self.layer)):
            return DesignVariableType.GLOBAL_VARIABLE
        elif self.bcs == 'nan' or self.bcs == '':
            return DesignVariableType.LAYER_VARIABLE
        elif '-' in self.bcs:
            return DesignVariableType.MULTI_TURN_VARIABLE
        elif self.bcs.isnumeric():
            return DesignVariableType.TURN_VARIABLE
        else:
            raise AttributeError('The design variable has incorrect block index value: %s.' % self.bcs)


class DesignVariableType(Enum):
    GLOBAL_VARIABLE = auto()
    LAYER_VARIABLE = auto()
    MULTI_TURN_VARIABLE = auto()
    TURN_VARIABLE = auto()

class GeneticDesignVariable(DesignVariable):
    """ A DesignVariable class for genetic optimization purpose

    """

    def __init__(self,
                 xl: Union[int, float],
                 xu: Union[int, float],
                 variable: str,
                 layer: int,
                 bcs: str,
                 variable_type: str,
                 bits: int) -> None:
        """ A GeneticDesignVariable constructor

        :param xl: lower limit of a design variable
        :param xu: upper limit of a design variable
        :param variable: name of a design variable
        :param bcs: block index, range of indices (with -) or no block indication for global variables
        :param variable_type: variable type (int, float) used to determine the gene to value conversion type
        :param bits: the number of bits to represent a design variable
        """
        if variable_type == 'int':
            super().__init__(int(xl), int(xu), variable, layer, bcs)
        else:
            super().__init__(float(xl), float(xu), variable, layer, bcs)
        self.bits = bits
        self.variable_type = variable_type

    def generate_random_gene(self) -> list:
        """ Method generating a random gene for int and float design variables

        :return:
        """
        gene = list(np.random.randint(0, 2, self.bits))
        if self.variable_type == 'float':
            return gene
        elif self.variable_type == 'int':
            gene_int = GeneticDesignVariable.convert_gene_to_int(gene)
            if gene_int > (self.xu - self.xl):
                gene_temp = GeneticDesignVariable.convert_int_to_gene(self.xu - self.xl, self.bits)
                return (self.bits - len(gene_temp)) * [0] + gene_temp
            else:
                return gene
        else:
            raise AttributeError('The variable type %s should be either int or float.' % self.variable_type)

    def convert_gene_to_value(self, gene: list) -> Union[int, float]:
        """ Method converting a gene to design variable value (either int or float):
        - for int, the value is given as lower limit + gene integer value; in case of an overflow, the upper limit is
        considered
        - for float, the value is given as the lower limit + gene integer value multiplied by variable range and divided
        by the number of binary combinations

        :param gene: a list of bits representing a design variable
        :return: numeric value of a gene
        """
        gene_int = GeneticDesignVariable.convert_gene_to_int(gene)

        # convert to value
        if self.variable_type == 'int':
            return min(int(self.xl + gene_int), int(self.xu))
        else:
            return self.xl + gene_int * (self.xu - self.xl) / 2 ** self.bits

    @staticmethod
    def convert_gene_to_int(gene: list) -> int:
        """ Static method converting a gene as a list into an integer

        :param gene: a list of bits representing a gene
        :return: an integer value of a gene
        """
        # convert chromosome to a string of chars
        gene_chars = ''.join([str(s) for s in gene])

        # convert string to integer
        return int(gene_chars, 2)

    @staticmethod
    def convert_int_to_gene(n: int, nbits: int) -> list:
        """ Static method converting an integer to a gene

        :param n: an integer value of a gene
        :param nbits: number of bits in binary representation
        :return: a list of bits representing a gene
        """
        bitstring = [n >> i & 1 for i in range(n.bit_length() - 1, -1, -1)]
        if len(bitstring) < nbits:
            bitstring = [0] * (nbits - len(bitstring)) + bitstring
        return bitstring

class CockpitGeneticDesignVariable(GeneticDesignVariable):

    def __init__(self, gen_dv: "GeneticDesignVariable") -> None:
        super().__init__(**gen_dv.__dict__)
        self.logger_column = self.get_minimal_logger_column_name()
        self.variable_name = self.get_variable_name_for_widget_bar_plot()

    def get_minimal_logger_column_name(self) -> str:
        design_variable_type = self.get_variable_type()
        if design_variable_type == DesignVariableType.GLOBAL_VARIABLE:
            return self.variable
        elif design_variable_type == DesignVariableType.LAYER_VARIABLE:
            return "%s:%s:" % (self.variable, int(self.layer))
        elif design_variable_type == DesignVariableType.MULTI_TURN_VARIABLE:
            return '%s:%s:%s' % (self.variable, self.layer, self.bcs.split('-')[0])
        elif design_variable_type == DesignVariableType.TURN_VARIABLE:
            return '%s:%s:%s' % (self.variable, self.layer, self.bcs)
        else:
            raise AttributeError('The design variable has incorrect block index value: %s.' % self.bcs)

    def get_variable_name_for_widget_bar_plot(self) -> str:
        design_variable_type = self.get_variable_type()
        if design_variable_type == DesignVariableType.GLOBAL_VARIABLE:
            return self.variable
        elif design_variable_type == DesignVariableType.LAYER_VARIABLE:
            return "%s:%s:" % (self.variable, int(self.layer))
        elif design_variable_type == DesignVariableType.MULTI_TURN_VARIABLE:
            return '%s:%s:%s' % (self.variable, self.layer, self.bcs)
        elif design_variable_type == DesignVariableType.TURN_VARIABLE:
            return '%s:%s:%s' % (self.variable, int(self.layer), self.bcs)
        else:
            raise AttributeError('The design variable has incorrect block index value: %s.' % self.bcs)

    def get_hover_text(self, value):
        if self.variable_type == 'float':
            return 'value: %.3f, range: [%.3f, %.3f]' % (value, self.xl, self.xu)
        else:
            return 'value: %d, range: [%d, %d]' % (value, self.xl, self.xu)

    def get_fraction(self, value):
        if self.xu == self.xl:
            return float('nan')
        else:
            return (value - self.xl) / (self.xu - self.xl)
