import os


def load_env():
    if os.environ.get('GBD_INIT_ENV', None):
        current_path = os.environ.get('GBD_INIT_ENV')
    else:
        current_path = os.getcwd()
    init_files = [f for f in os.listdir(current_path) if f.endswith('.ini')]
    env_vars_to_set = {}
    for init_file in sorted(init_files):
        with open(init_file, 'r') as f:
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                tmp = line.split('=')
                if len(tmp) != 2:
                    continue
                key = tmp[0].strip()
                value = tmp[1].strip()
                if '#' in value:
                    value = value.split('#')[0]
                    value = value.strip()
                env_vars_to_set[key] = value
    for key, value in env_vars_to_set.items():
        os.environ[key] = value

load_env()