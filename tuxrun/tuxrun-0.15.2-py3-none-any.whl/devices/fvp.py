# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from typing import Dict, List, Optional

from tuxrun import templates
from tuxrun.devices import Device
from tuxrun.exceptions import InvalidArgument


class FVPDevice(Device):
    mandatory = ["mcp_fw", "mcp_romfw", "rootfs", "scp_fw", "scp_romfw", "uefi"]

    prompts: List[str] = []
    auto_login: Dict[str, str] = {}
    boot_timeout = 20
    support_tests = False
    rootfs: Optional[str] = None

    def validate(
        self,
        mcp_fw,
        mcp_romfw,
        rootfs,
        scp_fw,
        scp_romfw,
        parameters,
        tests,
        uefi,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for k in kwargs if kwargs[k]]
        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for fvp devices: {', '.join(invalid_args)}"
            )

        args = locals()
        missing_args = ["--" + k for k in self.mandatory if not args[k]]
        if len(missing_args) > 0:
            raise InvalidArgument(
                f"Missing option(s) for fvp devices: {', '.join(missing_args)}"
            )

        if tests and not self.support_tests:
            raise InvalidArgument("Tests are not supported on this device")

        if self.rootfs and rootfs:
            raise InvalidArgument("Invalid option for this fvp device: --rootfs")

        for test in tests:
            test.validate(device=self, parameters=parameters, **kwargs)

    def definition(self, **kwargs):
        kwargs = kwargs.copy()

        # Options that can *not* be updated
        kwargs["prompts"] = self.prompts.copy()
        kwargs["auto_login"] = self.auto_login.copy()
        kwargs["support_tests"] = self.support_tests

        kwargs["rootfs"] = self.rootfs if self.rootfs else kwargs.get("rootfs")
        kwargs["boot_timeout"] = self.boot_timeout

        # render the template
        tests = [
            t.render(
                tmpdir=kwargs["tmpdir"],
                parameters=kwargs["parameters"],
            )
            for t in kwargs["tests"]
        ]
        return (
            templates.jobs().get_template("fvp.yaml.jinja2").render(**kwargs)
            + "\n"
            + "".join(tests)
        )

    def device_dict(self, context):
        return templates.devices().get_template("fvp.yaml.jinja2").render(**context)


class FVPMorelloAndroid(FVPDevice):
    name = "fvp-morello-android"

    prompts = ["console:/ "]
    support_tests = True


class FVPMorelloBusybox(FVPDevice):
    name = "fvp-morello-busybox"

    prompts = ["/ # "]
    support_tests = False


class FVPMorelloOE(FVPDevice):
    name = "fvp-morello-oe"

    prompts = ["root@morello-fvp:~# "]
    support_tests = True


class FVPMorelloUbuntu(FVPDevice):
    name = "fvp-morello-ubuntu"

    mandatory = ["mcp_fw", "mcp_romfw", "scp_fw", "scp_romfw", "uefi"]

    prompts = ["morello@morello-server:"]
    auto_login = {
        "login_prompt": "morello-server login:",
        "username": "morello",
        "password_prompt": "Password:",
        "password": "morello",
    }
    boot_timeout = 60
    rootfs = "https://storage.tuxboot.com/fvp-morello-ubuntu/ubuntu.satadisk.xz"
