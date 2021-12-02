from swimlane_platform.lib import names, env_manager
from swimlane_platform.lib.debug_decorators import info_function_start_finish, debug_function_args
from swimlane_platform.lib.docker_manager import DockerManager
from swimlane_platform.shared_steps import enable_turbine
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
from os import path
import semver


class UpgradeFrom1043To1050rc1(UpgradeStep):
    FROM = semver.parse_version_info('10.4.3')  # type: semver.VersionInfo
    TO = semver.parse_version_info('10.5.0-rc1')  # type: semver.VersionInfo

    @info_function_start_finish('Upgrade From 10.4.3 To 10.5.0-rc1')
    def process(self):
        # type: () -> None
        enable_turbine.run(self.config)
        self.upgrade_image_versions(names.INSTALL_DIR, self.config.args.dev)
        self.remove_reports_volume()
        self.add_env_vars(names.INSTALL_DIR)

    @debug_function_args
    def upgrade_image_versions(self, install_dir, dev):
        # type: (str, bool) -> None
        """
        Updates image versions

        :param dev: If the images will be pulled from development repository.
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        docker_compose = self.upgrade_standard_images(self.config.args.dev, names.INSTALL_DIR)
        docker_compose.save()

    @debug_function_args
    def add_env_vars(self, install_dir):
        # type: (str, bool) -> None
        """
        Adds the new env variables to the api and tasks env files
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        # Modify env files.
        secrets_dir = path.join(install_dir, names.SECRETS_SUB_FOLDER)
        env_files = [names.API_ENV_FILE, names.TASKS_ENV_FILE]
        for file_path in (path.join(secrets_dir, file_name) for file_name in env_files):
            env_file = env_manager.read_dict(file_path)
            new_env_file = dict((key, value) for key, value in env_file.items())            
            new_env_file['SWIMLANE_FeatureManagement__RecordPage'] = 'false'
            new_env_file['SWIMLANE_Python3Version'] = '3.7.12'
            env_manager.write_dict(file_path, new_env_file)

    @debug_function_args
    def remove_reports_volume(self):
        # type: (str) -> None
        """
        Removes the reports volume so it can be rebuilt by the application
        """
        docker_manager = DockerManager(self.logger)
        docker_manager.volume_remove('swimlane_reports')
