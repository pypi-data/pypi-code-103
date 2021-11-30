import os
from pathlib import Path

import pytest

from tuxrun.devices import Device
from tuxrun.devices.qemu import QemuArmv5
from tuxrun.devices.fvp import FVPMorelloAndroid
from tuxrun.exceptions import InvalidArgument
from tuxrun.tests import Test


BASE = (Path(__file__) / "..").resolve()


def test_select():
    assert Device.select("qemu-armv5") == QemuArmv5
    assert Device.select("fvp-morello-android") == FVPMorelloAndroid

    with pytest.raises(InvalidArgument):
        Device.select("Hello")


FVP_MORELLO_ANDROID = {
    "tests": [],
    "mcp_fw": "mcp_fw.bin",
    "mcp_romfw": "mcp_romfw.bin",
    "rootfs": "android-nano.img.xz",
    "scp_fw": "scp_fw.bin",
    "scp_romfw": "scp_romfw.bin",
    "uefi": "uefi.bin",
}


@pytest.mark.parametrize(
    "device,args,timeouts,filename",
    [
        (
            "qemu-arm64",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-arm64.yaml",
        ),
        (
            "qemu-arm64",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {"deploy": 4, "boot": 12},
            "qemu-arm64-timeouts.yaml",
        ),
        (
            "qemu-arm64",
            {
                "command": "",
                "tests": [Test.select("ltp-fcntl-locktests")(timeout=None)],
                "tux_boot_args": "",
                "overlays": [],
                "test_definitions": "testdef.tar.zst",
            },
            {},
            "qemu-arm64-ltp-fcntl-locktests.yaml",
        ),
        (
            "qemu-armv5",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-armv5.yaml",
        ),
        (
            "qemu-armv5",
            {
                "command": "",
                "tests": [Test.select("ltp-fs_bind")(timeout=None)],
                "tux_boot_args": "",
                "overlays": [],
                "test_definitions": "testdef.tar.zst",
            },
            {},
            "qemu-armv5-ltp-fs_bind.yaml",
        ),
        (
            "qemu-armv7",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-armv7.yaml",
        ),
        (
            "qemu-armv7",
            {
                "command": "",
                "tests": [
                    Test.select("ltp-fs_perms_simple")(timeout=4),
                    Test.select("ltp-fsx")(timeout=3),
                    Test.select("ltp-nptl")(timeout=None),
                ],
                "tux_boot_args": "",
                "overlays": [],
                "test_definitions": "testdef.tar.zst",
            },
            {},
            "qemu-armv7-ltp-timeouts.yaml",
        ),
        (
            "qemu-armv7",
            {"tests": [], "tux_boot_args": "", "overlays": [], "kernel": "zImage.xz"},
            {},
            "qemu-armv7-kernel-xz.yaml",
        ),
        (
            "qemu-i386",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-i386.yaml",
        ),
        (
            "qemu-i386",
            {
                "command": "",
                "tests": [Test.select("kunit")(timeout=None)],
                "tux_boot_args": "",
                "overlays": [],
                "test_definitions": "testdef.tar.zst",
            },
            {},
            "qemu-i386-kunit.yaml",
        ),
        (
            "qemu-i386",
            {"tests": [], "tux_boot_args": "", "overlays": [], "kernel": "bzImage.gz"},
            {},
            "qemu-i386-kernel-gz.yaml",
        ),
        (
            "qemu-mips32",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-mips32.yaml",
        ),
        (
            "qemu-mips32",
            {
                "tests": [Test.select("command")(timeout=None)],
                "tux_boot_args": "",
                "overlays": [],
                "command": "cat /proc/cpuinfo",
                "test_definitions": "testdef.tar.zst",
            },
            {},
            "qemu-mips32-command.yaml",
        ),
        (
            "qemu-mips32el",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-mips32el.yaml",
        ),
        (
            "qemu-mips64",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-mips64.yaml",
        ),
        (
            "qemu-mips64",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-mips64el.yaml",
        ),
        (
            "qemu-ppc32",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-ppc32.yaml",
        ),
        (
            "qemu-ppc64",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-ppc64.yaml",
        ),
        (
            "qemu-ppc64le",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-ppc64le.yaml",
        ),
        (
            "qemu-riscv64",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-riscv64.yaml",
        ),
        (
            "qemu-sparc64",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-sparc64.yaml",
        ),
        (
            "qemu-x86_64",
            {"tests": [], "tux_boot_args": "", "overlays": []},
            {},
            "qemu-x86_64.yaml",
        ),
        (
            "fvp-morello-android",
            FVP_MORELLO_ANDROID,
            {},
            "fvp-morello-android.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("binder")(timeout=None)],
                "parameters": {"USERDATA": "userdata.tar.xz"},
            },
            {},
            "fvp-morello-android-binder.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("bionic")(timeout=None)],
                "parameters": {"USERDATA": "userdata.tar.xz"},
            },
            {},
            "fvp-morello-android-bionic.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("bionic")(timeout=None)],
                "parameters": {
                    "BIONIC_TEST_TYPE": "dynamic",
                    "GTEST_FILTER": "hello",
                    "USERDATA": "userdata.tar.xz",
                },
            },
            {},
            "fvp-morello-android-bionic-params.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("boringssl")(timeout=None)],
                "parameters": {"SYSTEM_URL": "system.tar.xz"},
            },
            {},
            "fvp-morello-android-boringssl.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("boringssl")(timeout=4212)],
                "parameters": {"SYSTEM_URL": "system.tar.xz"},
            },
            {},
            "fvp-morello-android-boringssl-timeouts.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("compartment")(timeout=None)],
                "parameters": {"USERDATA": "userdata.tar.xz"},
            },
            {},
            "fvp-morello-android-compartment.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("device-tree")(timeout=None)],
                "parameters": {},
            },
            {},
            "fvp-morello-android-device-tree.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("dvfs")(timeout=None)],
                "parameters": {},
            },
            {},
            "fvp-morello-android-dvfs.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("libjpeg-turbo")(timeout=None)],
                "parameters": {
                    "SYSTEM_URL": "system.tar.xz",
                    "LIBJPEG_TURBO_URL": "libjpeg.tar.xz",
                },
            },
            {},
            "fvp-morello-android-libjpeg-turbo.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("libpdfium")(timeout=None)],
                "parameters": {
                    "SYSTEM_URL": "system.tar.xz",
                    "PDFIUM_URL": "pdfium.tar.xz",
                },
            },
            {},
            "fvp-morello-android-libpdfium.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("libpng")(timeout=None)],
                "parameters": {"SYSTEM_URL": "system.tar.xz", "PNG_URL": "png.tar.xz"},
            },
            {},
            "fvp-morello-android-libpng.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("lldb")(timeout=None)],
                "parameters": {"LLDB_URL": "lldb.tar.xz", "TC_URL": "toolchain.tar.xz"},
            },
            {},
            "fvp-morello-android-lldb.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("logd")(timeout=None)],
                "parameters": {"USERDATA": "userdata.tar.xz"},
            },
            {},
            "fvp-morello-android-logd.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("multicore")(timeout=None)],
                "parameters": {},
            },
            {},
            "fvp-morello-android-multicore.yaml",
        ),
        (
            "fvp-morello-android",
            {
                **FVP_MORELLO_ANDROID,
                "tests": [Test.select("zlib")(timeout=None)],
                "parameters": {"SYSTEM_URL": "system.tar.xz"},
            },
            {},
            "fvp-morello-android-zlib.yaml",
        ),
        (
            "fvp-morello-busybox",
            {
                "tests": [],
                "mcp_fw": "mcp_fw.bin",
                "mcp_romfw": "mcp_romfw.bin",
                "rootfs": "busybox.img.xz",
                "scp_fw": "scp_fw.bin",
                "scp_romfw": "scp_romfw.bin",
                "uefi": "uefi.bin",
            },
            {},
            "fvp-morello-busybox.yaml",
        ),
        (
            "fvp-morello-oe",
            {
                "tests": [],
                "mcp_fw": "mcp_fw.bin",
                "mcp_romfw": "mcp_romfw.bin",
                "rootfs": "core-image-minimal-morello-fvp.wic",
                "scp_fw": "scp_fw.bin",
                "scp_romfw": "scp_romfw.bin",
                "uefi": "uefi.bin",
            },
            {},
            "fvp-morello-oe.yaml",
        ),
        (
            "fvp-morello-ubuntu",
            {
                "tests": [],
                "mcp_fw": "mcp_fw.bin",
                "mcp_romfw": "mcp_romfw.bin",
                "scp_fw": "scp_fw.bin",
                "scp_romfw": "scp_romfw.bin",
                "uefi": "uefi.bin",
            },
            {},
            "fvp-morello-ubuntu.yaml",
        ),
    ],
)
def test_definition(device, args, timeouts, filename):
    if os.environ.get("TUXRUN_RENDER"):
        obj = Device.select(device)()
        (BASE / "refs" / "definitions" / filename).write_text(
            Device.select(device)().definition(
                device=obj,
                container=None,
                tests_timeout=sum(t.timeout for t in args["tests"]),
                timeouts=timeouts,
                tmpdir=Path("/tmp/tuxrun-ci"),
                **args
            )
        )
    obj = Device.select(device)()
    assert Device.select(device)().definition(
        device=obj,
        container=None,
        tests_timeout=sum(t.timeout for t in args["tests"]),
        timeouts=timeouts,
        tmpdir=Path("/tmp/tuxrun-ci"),
        **args
    ) == (BASE / "refs" / "definitions" / filename).read_text(encoding="utf-8")
