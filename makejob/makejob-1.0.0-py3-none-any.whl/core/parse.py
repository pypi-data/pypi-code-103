import os


def parse_conf(configfile):
    with open(configfile) as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            linelist = line.strip().split()
            script = linelist[0]
            memory = linelist[1]

            thread = depend_scripts = None

            if len(linelist) == 3:
                # script memory thread
                if linelist[2].isdigit():
                    thread = linelist[2]
                # script memory depend_scripts
                else:
                    depend_scripts = linelist[2]

            # script memory depend_scripts thread
            if len(linelist) >= 4:
                depend_scripts, thread = linelist[2:4]

            yield script, memory, depend_scripts, thread


if __name__ == "__main__":
    for line in parse_conf('tests/demo.conf'):
        print(line)
