import importlib
import sys
import pathlib
import json

if pathlib.Path('./ourkvm/__init__.py').absolute().exists():
	spec = importlib.util.spec_from_file_location("ourkvm", "./ourkvm/__init__.py")
	ourkvm = importlib.util.module_from_spec(spec)
	sys.modules["ourkvm"] = ourkvm
	spec.loader.exec_module(sys.modules["ourkvm"])
else:
	import ourkvm

if ourkvm.storage['arguments'].machine_name:
	base_hardware = ourkvm.DupeDict()
	base_hardware["cpu"] = ourkvm.storage['arguments'].cpu
	base_hardware["enable-kvm"] = True
	base_hardware["machine"] = "q35,accel=kvm"
	base_hardware["device"] = "intel-iommu"
	base_hardware["m"] = ourkvm.storage['arguments'].memory

	if ourkvm.storage['arguments'].bios is False:
		base_hardware["drive"] = f"if=pflash,format=raw,readonly=on,file={ourkvm.storage['arguments'].uefi_code}"
		base_hardware["drive"] = f"if=pflash,format=raw,readonly=on,file={ourkvm.storage['arguments'].uefi_vars}"

	pcie_buses = ourkvm.DupeDict() # There's already a default pcie.0 bus builtin to qemu.
	pcie_root_ports = ourkvm.DupeDict()
	pcie_slave_buses = ourkvm.DupeDict()
	pcie_slave_devices = ourkvm.DupeDict()

	name = ourkvm.storage['arguments'].machine_name
	scsi_index = 0
	boot_index = 0

	if ourkvm.storage['arguments'].harddrives:
		for drive_index, drive_spec in enumerate(ourkvm.storage['arguments'].harddrives.split(',')):
			if ':' not in drive_spec:
				drive_spec += ':20G'

			image_name, size = drive_spec.split(':',1)
			image_format = pathlib.Path(image_name).suffix[1:]
			image_path = pathlib.Path(image_name).expanduser().absolute()

			if not image_path.exists():
				if (output := ourkvm.qemu_img(f"create -f {image_format} {image_path} {size}")).exit_code != 0:
					raise SystemError(f"Could not create test image {image_path}: {output}")

			pcie_root_ports["device"] = f"virtio-scsi-pci,bus=pcie.0,id=scsi{scsi_index}"
			pcie_slave_buses["device"] = f"scsi-hd,drive=hdd{drive_index},bus=scsi{scsi_index}.0,id=scsi{scsi_index}.0,bootindex={boot_index}"
			pcie_slave_devices["drive"] = f"file={image_path},if=none,format={image_format},discard=unmap,aio=native,cache=none,id=hdd{drive_index}"

			scsi_index += 1
			boot_index += 1

	if ourkvm.storage['arguments'].cdroms:
		for drive_index, image_name in enumerate(ourkvm.storage['arguments'].cdroms.split(',')):
			image_path = pathlib.Path(image_name).expanduser().absolute()

			if not image_path.exists():
				raise ourkvm.ResourceNotFound(f"Could not locate ISO image {image_path}")

			pcie_root_ports["device"] = f"virtio-scsi-pci,bus=pcie.0,id=scsi{scsi_index}"
			pcie_slave_buses["device"] = f"scsi-cd,drive=cdrom{drive_index},bus=scsi{scsi_index}.0,id=scsi{scsi_index}.0,bootindex={boot_index}"
			pcie_slave_devices["drive"] = f"file={image_path},media=cdrom,if=none,format=raw,cache=none,id=cdrom{drive_index}"

			scsi_index += 1
			boot_index += 1

	ourkvm.verify_qemu_resources(name, base_hardware, pcie_buses, pcie_root_ports, pcie_slave_buses, pcie_slave_devices)
	qemu_string = ourkvm.create_qemu_string(name, base_hardware, pcie_buses, pcie_root_ports, pcie_slave_buses, pcie_slave_devices)

	if ourkvm.storage['arguments'].service:
		service_path = pathlib.Path(ourkvm.storage['arguments'].service).expanduser().absolute()
		qemu_config_path = pathlib.Path(f"{ourkvm.storage['arguments'].config}/{name}.cfg").expanduser().absolute()

		if not qemu_config_path.parent.exists():
			qemu_config_path.parent.mkdir(parents=True)

		if service_path.exists() and not ourkvm.storage['arguments'].force:
			raise ourkvm.ResourceError(f"A service file for the machine {name} already exists: {service_path}")
		elif service_path.exists():
			# Because write_qemu_service_file() creates it
			service_path.unlink()

		if qemu_config_path.exists() and not ourkvm.storage['arguments'].force:
			raise ourkvm.ResourceError(f"A environment configuration file for the machine {name} already exists: {qemu_config_path}")

		with qemu_config_path.open('w') as config:
			config.write(json.dumps([], cls=ourkvm.JSON))

		ourkvm.write_qemu_service_file(service_path, name, qemu_config_path, qemu_string)
	else:
		print(f"qemu-system-x86_64" + qemu_string)