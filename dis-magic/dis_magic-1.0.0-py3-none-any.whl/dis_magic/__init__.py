from dis import dis as print_dis

from IPython.core.magic import register_line_cell_magic


def load_ipython_extension(_ipython):
    @register_line_cell_magic
    def dis(line, cell=None):
        if cell is not None:
            print_dis(cell)
            _ipython.ex(cell)
        else:
            print_dis(line)
            _ipython.ex(line)
