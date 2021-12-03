from .message_log import Log
from .config import load_config
from os import path, system
import subprocess
import yaml


class SDKSetup:
    config = load_config('config.yml')
    home_path = path.expanduser('~')
    config_path = path.expanduser('~/.grepsr/config.yml')

    def __init__(self, type, dryrun, sdk_image):
        self.type_dict = self.config[type]
        self.type_name = type
        self.dryrun = dryrun
        self.sdk_image = sdk_image

        self.do_setup()

    def check_path(self):
        for service_dir in self.type_dict['paths']:
            service_dir = path.expanduser(service_dir)
            if not path.exists(service_dir):
                Log.error(
                    f'Directory {service_dir} was not found')
                Log.error(
                    "Please check ~/.grepsr/config.yml to check if paths are correctly added")
                return False
        return True

    def generate_autocomplete_directory(self, docker_id, dir_name):
        for service_dir in self.type_dict['paths']:
            Log.info(
                f"Adding autocomplete modules in {service_dir}")
            command = f'''
                    rm -rf {service_dir}/.autocomplete && 
                    mkdir {service_dir}/.autocomplete
                '''

            command += f"""docker cp -L {docker_id}:/home/grepsr/{dir_name}/lib {service_dir}/.autocomplete/
            docker cp -L {docker_id}:/home/grepsr/{dir_name}/vendor {service_dir}/.autocomplete/
            """
            system(command)

    def do_setup(self):
        if self.sdk_image is not None:
            with open(self.config_path, 'w') as w:
                self.config[self.type_name]['sdk_image'] = self.sdk_image
                w.write(yaml.dump(self.config))

        if(self.check_path() == False):
            return False
        if(self.dryrun == False):
            Log.info("Logging in to AWS service")

            system(f'''export AWS_ACCESS_KEY_ID={self.config['aws_access_key_id']} &&
            export AWS_SECRET_ACCESS_KEY={self.config['aws_secret_access_key']}
            eval $(aws ecr get-login --no-include-email --region eu-central-1)''')

            Log.info("Getting the SDK")
            system(f"docker pull {self.type_dict['sdk_image']}")

        docker_id = subprocess.run(
            ['docker',  'create', self.type_dict['sdk_image']], stdout=subprocess.PIPE).stdout
        docker_id = docker_id.decode('utf-8').rstrip()

        if self.type_name == 'php':
            self.generate_autocomplete_directory(
                docker_id, 'vortex-backend')
        elif self.type_name == 'php_next':
            self.generate_autocomplete_directory(
                docker_id, 'vortex-backend-next')

        system(f'docker rm {docker_id}')
        Log.info("SDK has been installed successfully")
