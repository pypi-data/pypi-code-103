# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from typing import List

from tuxrun import templates
from tuxrun.devices import Device
from tuxrun.exceptions import InvalidArgument


def notnone(value, fallback):
    if value is None:
        return fallback
    return value


class QemuDevice(Device):
    arch: str = ""
    lava_arch: str = ""
    machine: str = ""
    cpu: str = ""
    memory: str = ""

    guestfs_interface: str = ""
    extra_options: List[str] = []
    extra_options_tests: List[str] = []

    console: str = ""
    rootfs_dev: str = ""
    rootfs_arg: str = ""

    dtb: str = ""
    bios: str = ""
    kernel: str = ""
    rootfs: str = ""

    def validate(
        self,
        bios,
        boot_args,
        command,
        dtb,
        kernel,
        modules,
        overlays,
        partition,
        rootfs,
        tests,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for k in kwargs if kwargs[k]]

        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for qemu devices: {', '.join(invalid_args)}"
            )

        if bios and self.name != "qemu-riscv64":
            raise InvalidArgument(
                "argument --bios is only valid for qemu-riscv64 device"
            )
        if boot_args and '"' in boot_args:
            raise InvalidArgument('argument --boot-args should not contains "')
        if dtb and self.name != "qemu-armv5":
            raise InvalidArgument("argument --dtb is only valid for qemu-armv5 device")
        if modules and not modules.endswith(".tar.xz"):
            raise InvalidArgument("argument --modules should be a .tar.xz")

        for test in tests:
            test.validate(device=self, **kwargs)

    def definition(self, **kwargs):
        kwargs = kwargs.copy()

        # Options that can *not* be updated
        kwargs["arch"] = self.arch
        kwargs["lava_arch"] = self.lava_arch
        kwargs["machine"] = self.machine
        kwargs["cpu"] = self.cpu
        kwargs["memory"] = self.memory
        kwargs["guestfs_interface"] = self.guestfs_interface
        kwargs["extra_options"] = self.extra_options.copy()
        if kwargs["tests"]:
            kwargs["extra_options"].extend(self.extra_options_tests.copy())
        kwargs["console"] = self.console
        kwargs["rootfs_dev"] = self.rootfs_dev
        kwargs["rootfs_arg"] = self.rootfs_arg

        # Options that can be updated
        kwargs["bios"] = notnone(kwargs.get("bios"), self.bios)
        kwargs["dtb"] = notnone(kwargs.get("dtb"), self.dtb)
        kwargs["kernel"] = notnone(kwargs.get("kernel"), self.kernel)
        kwargs["rootfs"] = notnone(kwargs.get("rootfs"), self.rootfs)

        # Computed values
        kernel = kwargs.get("kernel")
        kernel_compression = ""
        if kernel.endswith(".gz"):
            kernel_compression = "gz"
        if kernel.endswith(".xz"):
            kernel_compression = "xz"
        kwargs["kernel_compression"] = kernel_compression

        # render the template
        tests = [
            t.render(
                arch=kwargs["arch"],
                command=kwargs["command"],
                test_definitions=kwargs["test_definitions"],
            )
            for t in kwargs["tests"]
        ]
        return (
            templates.jobs().get_template("qemu.yaml.jinja2").render(**kwargs)
            + "\n"
            + "".join(tests)
        )

    def device_dict(self, context):
        return templates.devices().get_template("qemu.yaml.jinja2").render(**context)


class QemuArm64(QemuDevice):
    name = "qemu-arm64"

    arch = "arm64"
    lava_arch = "arm64"
    machine = "virt,gic-version=3"
    cpu = "cortex-a57"

    guestfs_interface = "virtio"
    extra_options = ["-smp 2"]

    console = "ttyAMA0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = "-drive file={rootfs},if=none,format=raw,id=hd0 -device virtio-blk-device,drive=hd0"

    kernel = "https://storage.tuxboot.com/arm64/Image"
    rootfs = "https://storage.tuxboot.com/arm64/rootfs.ext4.zst"


class QemuArmv5(QemuDevice):
    name = "qemu-armv5"

    arch = "armv5"
    lava_arch = "arm"
    machine = "versatilepb"
    cpu = "arm926"

    guestfs_interface = "scsi"
    memory = "256M"

    console = "ttyAMA0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=scsi,format=raw"

    dtb = "https://storage.tuxboot.com/armv5/versatile-pb.dtb"
    kernel = "https://storage.tuxboot.com/armv5/zImage"
    rootfs = "https://storage.tuxboot.com/armv5/rootfs.ext4.zst"


class QemuArmv7(QemuDevice):
    name = "qemu-armv7"

    arch = "armv7"
    lava_arch = "arm"
    machine = "virt,gic-version=3"
    cpu = "cortex-a15"

    guestfs_interface = "none"
    extra_options = ["-smp 2"]
    extra_options_tests = ["-device virtio-blk-device,drive=lavatest"]

    console = "ttyAMA0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = "-drive file={rootfs},if=none,format=raw,id=hd0 -device virtio-blk-device,drive=hd0"

    kernel = "https://storage.tuxboot.com/armv7/zImage"
    rootfs = "https://storage.tuxboot.com/armv7/rootfs.ext4.zst"


class Qemui386(QemuDevice):
    name = "qemu-i386"

    arch = "i386"
    lava_arch = "i386"
    machine = "q35"
    cpu = "coreduo"

    extra_options = ["-smp 2"]

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/i386/bzImage"
    rootfs = "https://storage.tuxboot.com/i386/rootfs.ext4.zst"


class QemuMips32(QemuDevice):
    name = "qemu-mips32"

    arch = "mips32"
    lava_arch = "mips"
    machine = "malta"
    cpu = "mips32r6-generic"

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/mips32/vmlinux"
    rootfs = "https://storage.tuxboot.com/mips32/rootfs.ext4.zst"


class QemuMips32EL(QemuDevice):
    name = "qemu-mips32el"

    arch = "mips32el"
    lava_arch = "mipsel"
    machine = "malta"
    cpu = "mips32r6-generic"

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/mips32el/vmlinux"
    rootfs = "https://storage.tuxboot.com/mips32el/rootfs.ext4.zst"


class QemuMips64(QemuDevice):
    name = "qemu-mips64"

    arch = "mips64"
    lava_arch = "mips64"
    machine = "malta"

    console = "ttyS0"
    rootfs_dev = "/dev/hda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/mips64/vmlinux"
    rootfs = "https://storage.tuxboot.com/mips64/rootfs.ext4.zst"


class QemuMips64EL(QemuDevice):
    name = "qemu-mips64el"

    arch = "mips64el"
    lava_arch = "mips64el"
    machine = "malta"

    console = "ttyS0"
    rootfs_dev = "/dev/hda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/mips64el/vmlinux"
    rootfs = "https://storage.tuxboot.com/mips64el/rootfs.ext4.zst"


class QemuPPC32(QemuDevice):
    name = "qemu-ppc32"

    arch = "ppc32"
    lava_arch = "ppc"
    machine = "ppce500"
    cpu = "e500mc"

    guestfs_interface = "virtio"

    console = "ttyS0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = "-drive file={rootfs},format=raw,if=virtio"

    kernel = "https://storage.tuxboot.com/ppc32/uImage"
    rootfs = "https://storage.tuxboot.com/ppc32/rootfs.ext4.zst"


class QemuPPC64(QemuDevice):
    name = "qemu-ppc64"

    arch = "ppc64"
    lava_arch = "ppc64"
    machine = "pseries"
    cpu = "POWER8"

    guestfs_interface = "scsi,index=1"
    extra_options = ["-smp 2"]

    console = "hvc0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},format=raw,if=scsi,index=0"

    kernel = "https://storage.tuxboot.com/ppc64/vmlinux"
    rootfs = "https://storage.tuxboot.com/ppc64/rootfs.ext4.zst"


class QemuPPC64LE(QemuDevice):
    name = "qemu-ppc64le"

    arch = "ppc64le"
    lava_arch = "ppc64le"
    machine = "pseries"
    cpu = "POWER8"

    guestfs_interface = "scsi,index=1"
    extra_options = ["-smp 2"]

    console = "hvc0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},format=raw,if=scsi,index=0"

    kernel = "https://storage.tuxboot.com/ppc64le/vmlinux"
    rootfs = "https://storage.tuxboot.com/ppc64le/rootfs.ext4.zst"


class QemuRiscV64(QemuDevice):
    name = "qemu-riscv64"

    arch = "riscv64"
    lava_arch = "riscv64"
    machine = "virt"
    cpu = "rv64"

    guestfs_interface = "virtio"
    extra_options = ["-smp 2"]

    console = "ttyS0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = (
        "-drive file={rootfs},format=raw,id=hd0 -device virtio-blk-device,drive=hd0"
    )

    bios = "https://storage.tuxboot.com/riscv64/fw_jump.elf"
    kernel = "https://storage.tuxboot.com/riscv64/Image"
    rootfs = "https://storage.tuxboot.com/riscv64/rootfs.ext4.zst"


class QemuSPARC64(QemuDevice):
    name = "qemu-sparc64"

    arch = "sparc64"
    lava_arch = "sparc64"
    machine = "sun4u"

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/sparc64/vmlinux"
    rootfs = "https://storage.tuxboot.com/sparc64/rootfs.ext4.zst"


class QemuX86_64(QemuDevice):
    name = "qemu-x86_64"

    arch = "x86_64"
    lava_arch = "x86_64"
    machine = "q35"
    cpu = "Nehalem"

    extra_options = ["-smp 2"]

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/x86_64/bzImage"
    rootfs = "https://storage.tuxboot.com/x86_64/rootfs.ext4.zst"
