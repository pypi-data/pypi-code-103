# Copyright 2019 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Periodically run by skill manager to update skills and post the manifest."""
import json
import os
from os.path import join, isfile

import xdg.BaseDirectory
from json_database import JsonStorage

from mycroft.api import DeviceApi, is_paired
from mycroft.configuration import Configuration, BASE_FOLDER
from mycroft.skills.skill_loader import get_skill_directories
from mycroft.util.log import LOG


class SeleneDeviceSkills(JsonStorage):
    """dict subclass with save/load support
    This dictionary contains the metadata expected by selene backend
    This data is used to populate entries in selene skill settings page
    It is only uploaded if enabled in mycroft.conf and device is paired
    """

    def __init__(self, api=None):
        path = os.path.join(xdg.BaseDirectory.save_data_path(BASE_FOLDER), 'skills.json')
        super().__init__(path)
        if "skills" not in self:
            self["skills"] = {}
        self.api = api or DeviceApi()

    def device_skill_state_hash(self):
        return hash(json.dumps(self, sort_keys=True))

    def add_skill(self, skill_id):
        if self.api.identity.uuid:
            skill_gid = f'@{self.api.identity.uuid}|{skill_id}'
        else:
            skill_gid = f'@|{skill_id}'
        skill = {
            "name": skill_id,
            "origin": "non-msm",
            "beta": True,
            "status": 'active',
            "installed": 0,
            "updated": 0,
            "installation": 'installed',
            "skill_gid": skill_gid
        }
        self["skills"].append(skill)

    def get_skill_state(self, skill_id):
        """Find a skill entry in the device skill state and returns it."""
        for skill_state in self.get('skills', []):
            if skill_state.get('name') == skill_id:
                return skill_state
        return {}

    def scan_skills(self):
        for directory in get_skill_directories():
            for skill_id in os.listdir(directory):
                skill_init = join(directory, skill_id, "__init__.py")
                if isfile(skill_init):
                    self.add_skill(skill_id)
        self.store()


class SkillUpdater:
    """Class facilitating skill update / install actions.

    Arguments
        bus (MessageBusClient): Optional bus emitter Used to communicate
                                with the mycroft core system and handle
                                commands.
    """
    _msm = None

    def __init__(self, bus=None):
        self.selene_skills = SeleneDeviceSkills()
        self.post_manifest(True)
        if bus:
            LOG.warning("bus argument has been deprecated\n"
                        "it will be removed in version 0.0.3")
        self.installed_skills = set()

    @property
    def installed_skills_file_path(self):
        """Property representing the path of the installed skills file."""
        return self.selene_skills.path

    def default_skill_names(self) -> tuple:
        """Property representing the default skills expected to be installed"""
        # TODO remove 0.0.3
        LOG.warning("msm has been deprecated\n"
                    "skill install/update is no longer handled by ovos-core\n"
                    "self.default_skill_names property will be removed in version 0.0.3")
        return ()

    def update_skills(self, quick=False):
        """Invoke MSM to install default skills and/or update installed skills

        Args:
            quick (bool): Expedite the download by running with more threads?
        """
        # TODO remove 0.0.3
        LOG.warning("msm has been deprecated\n"
                    "skill install/update is no longer handled by ovos-core\n"
                    "self.update_skills will be removed in version 0.0.3")
        return True

    def handle_not_connected(self):
        """Notifications of the device not being connected to the internet"""
        # TODO remove 0.0.3
        LOG.warning("msm has been deprecated\n"
                    "skill install/update is no longer handled by ovos-core\n"
                    "no update will be scheduled")

    def post_manifest(self, reload_skills_manifest=False):
        """Post the manifest of the device's skills to the backend."""
        upload_allowed = Configuration.get()['skills'].get('upload_skill_manifest')
        if upload_allowed and is_paired():
            if reload_skills_manifest:
                self.selene_skills.clear()
                self.selene_skills.scan_skills()
            try:
                device_api = DeviceApi()
                device_api.upload_skills_data(self.selene_skills)
            except Exception:
                LOG.error('Could not upload skill manifest')

    def install_or_update(self, skill):
        """Install missing defaults and update existing skills"""
        # TODO remove 0.0.3
        LOG.warning("msm has been deprecated\n"
                    "skill install/update is no longer handled by ovos-core\n"
                    f"{skill} will not be changed")

    def defaults_installed(self):
        """Check if all default skills are installed.

        Returns:
            True if all default skills are installed, else False.
        """
        # TODO remove 0.0.3
        LOG.warning("msm has been deprecated\n"
                    "skill install/update is no longer handled by ovos-core\n"
                    "self.defaults_installed will be removed in version 0.0.3")
        return True
