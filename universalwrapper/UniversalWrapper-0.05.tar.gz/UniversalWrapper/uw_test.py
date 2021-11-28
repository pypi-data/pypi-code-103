from universal_wrapper import UniversalWrapper as uw

class Lxc(uw):
    def __init__(self):
        self.cmd = 'lxc'
        self.divider = ' '

    def input_modifier(self, command):
        print('$ ' + command)
        return command

    def output_modifier(self, output):
        for line in output:
            print(line)
        return None

lxc=uw('lxc')
breakpoint()
