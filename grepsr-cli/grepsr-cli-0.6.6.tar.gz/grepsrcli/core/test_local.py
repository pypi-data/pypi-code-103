from os import path, system
from .message_log import Log
from .config import load_config


class TestLocal:
    def __init__(self, type, plugin_name, base_path):
        self.type = type
        self.plugin_name = plugin_name
        self.base_path = base_path

        self.tmp_path = path.expanduser('~') + '/.grepsr/tmp/'
        self.config = load_config('config.yml')
        self.type_config = self.config[type]

        self.test_script()

    def test_script(self):
        if self.type == "php":
            if "env" in self.type_config:
                if self.type_config['env']:
                    self.test_script_php(env=True)
                else:
                    self.test_script_php(env=False)
            else:
                self.test_script_php(env=False)
        elif self.type == "php_next":
            self.test_script_php_next()

    def test_script_php(self, env=False):

        if env == True:
            env_vars = [
                f'-e {env_var}={self.type_config["env"][env_var]}' for env_var in self.type_config["env"].keys()]
            command = f'''docker run -t -i --network="host" --rm -v {self.base_path}:/home/grepsr/vortex-plugins/{path.basename(self.base_path)} -v {self.tmp_path}:/tmp -e APP_ENV={self.config['app_env']}  {" ".join(env_vars)} {self.type_config['sdk_image']} -s {self.plugin_name}'''

        else:
            command = f'''docker run -t -i --network="host" --rm  \
                    -v {self.base_path}:/home/grepsr/vortex-plugins/{path.basename(self.base_path)}  \
                    -v {self.tmp_path}:/tmp  \
                    -e APP_ENV={self.config['app_env']}  \
                    {self.type_config['sdk_image']} -s {self.plugin_name}'''

        system(command)

    def test_script_php_next(self):

        command = f'''docker run -t -i --network="host" --rm \
                     -v {self.base_path}:/home/grepsr/vortex-backend-next/scraper-plugins \
                     -v {self.tmp_path}:/tmp \
                     -e APP_ENV={self.config['app_env']} \
                     {self.type_config['sdk_image']} -s {self.plugin_name} '''

        system(command)
