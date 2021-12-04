import logging
import typing as t

from .. import GearToolkitContext

log = logging.getLogger(__name__)


def add_qc_info(
    context: GearToolkitContext,
    file_: t.Union[t.Dict, str],
    name: str = "",
    version: str = "",
    job_id: str = None,
    **kwargs: t.Any,
) -> t.Dict:
    """Add QC information into existing file info.

    Given file.info:

    .. code-block:: python

        'info': {
            ...
        }

    Add qc information for a gear that has run on the file.
    For example, if splitter v0.2.0 ran on the file we might
    want to add the following qc:

    .. code-block:: python

        info: {
            ...,
            'qc': {
                'splitter': {
                    'filename': 'example_archive.dicom.zip',
                    'gear_info': {
                        'name': 'splitter',
                        'version': '0.2.0',
                        'config': {
                            'inputs':{
                                'parent': {
                                    'type': 'acquisition',
                                    'id': <acquisition_id>
                                },
                                'version': 1,
                                'file_id': <file_id>,
                                'file_name': <file_name>
                            },
                            'config': {
                                'debug': True
                            }
                        }
                    },
                    'created_files': [
                        'example_archive.dicom.zip',
                        'example_archive_Localizer.dicom.zip'
                    ]
                }
            }
        }

    This could be done by calling ``add_qc_info``:

    .. code-block:: python

        qc = add_qc_info(
            context,
            'some_input.dicom.zip',
            'splitter',
            fw_gear_splitter.__version__,
            None,
            created_files=[
                'example_archive.dicom.zip',
                'example_archive_Localizer.dicom.zip'
        ])

    Args:
        context (flywheel_gear_toolkit.GearToolkitContext): A GearToolkitContext instance.
        file_ (t.Union[t.Dict, str]): One of:
            - A filename (str)
            - A config.json input object (t.Dict)
            - A flywheel.FileEntry returned from the SDK (t.Dict)
        name (str): Gear name. If empty tries to pull from manifest. Default "".
        version (str): Gear version. If empty tries to pull from manifest. Default "".
        job_id (str): id of job running gear on file_. If None and this is an analysis gear, tries to pull
            from destination container.
        **kwargs (t.Any): Optional keywords to add to qc dict.

    Returns:
        t.Dict: Updated QC info.
    """

    if isinstance(file_, str):
        info = {}
        filename = file_
    elif "object" in file_:
        # file_ passed in from config.json
        info = file_.get("object", {}).get("info", {})
        filename = file_.get("location", {}).get("name")
    elif "info" in file_:
        # file_ passing in from SDK.
        info = file_.get("info", {})
        filename = file_.get("name")
    else:
        raise ValueError(
            f"Expected file_ to be dictionary or string, got {type(file_)}"
        )

    qc = {}
    if "qc" not in info:
        info["qc"] = qc
    else:
        qc = info["qc"]
    # overwrite qc.<gear-name> with current qc value

    gear_inputs = {}
    for input_name, file_entry in context.config_json.get("inputs", {}).items():
        if file_entry["base"] != "file":
            continue
        obj = file_entry.get("object", {})
        gear_inputs[input_name] = {
            "parent": file_entry.get("hierarchy"),
            "file_id": obj.get("file_id", ""),
            "version": obj.get("version", ""),
            "file_name": file_entry.get("location", {}).get("name", ""),
        }

    # destination container to check for gear name, version, job_id
    destination_container = context.get_destination_container().reload()

    if job_id:
        pass
    # elif output of gear is an analysis container, try to get it from there
    elif destination_container.container_type == "analysis":
        job_id = destination_container.get("job", {}).get("id")
        if not (job_id):
            log.warning("Could not determine job id.")

    if name == "":
        try:
            name = context.manifest["name"]
        except Exception as e:
            raise ValueError("Could not determine gear name from manifest.") from e

    if version == "":
        try:
            version = context.manifest["version"]
        except Exception as e:
            raise ValueError("Could not determine gear version from manifest") from e

    qc.update(
        {
            name: {
                "filename": filename,
                "gear_info": {
                    "name": name,
                    "version": version,
                    "job_id": job_id,
                    "config": {"inputs": gear_inputs, "config": context.config},
                },
                **kwargs,
            }
        }
    )
    info["qc"] = qc

    return info


def add_gear_info(
    context: GearToolkitContext,
    file_: t.Union[t.Dict, str],
    name: str = "",
    version: str = "",
    job_id: str = None,
    **kwargs: t.Any,
) -> t.Dict:

    """Add gear information into existing file info.

    Given file.info:

    .. code-block:: python

        'info': {
            ...
        }

    Add gear information for a gear that has run on the file.
    For example, if splitter v0.2.0 ran on the file we might
    want to add the following gears:

    .. code-block:: python

        info: {
            ...,
            'gears': {
                'splitter': {
                    'gear_info': {
                        'name': 'splitter',
                        'version': '0.2.0',
                        'config': {
                            'inputs':{
                                'parent': {
                                    'type': 'acquisition',
                                    'id': <acquisition_id>
                                },
                                'version': 1,
                                'file_id': <file_id>,
                                'file_name': <file_name>
                            },
                            'config': {
                                'debug': True
                            }
                        }
                    },
                    'created_files': [
                        'example_archive.dicom.zip',
                        'example_archive_Localizer.dicom.zip'
                    ]
                }
            }
        }

    This could be done by calling ``add_gear_info``:

    .. code-block:: python

        gear = add_gear_info(
            context=context,
            file='some_input.dicom.zip',
            name='splitter',
            version=fw_gear_splitter.__version__,
            job_id=None,
            created_files=[
                'example_archive.dicom.zip',
                'example_archive_Localizer.dicom.zip'
        ])

    Args:
        context (flywheel_gear_toolkit.GearToolkitContext): A GearToolkitContext instance.
        file_ (t.Union[t.Dict, str]): One of:
            - A filename (str)
            - A config.json input object (t.Dict)
            - A flywheel.FileEntry returned from the SDK (t.Dict)
        name (str): Gear name. If empty tries to pull from manifest. Default "".
        version (str): Gear version. If empty tries to pull from manifest. Default "".
        job_id (str): id of job running gear on file_. If None and this is an analysis gear, tries to pull
            from destination container.
        **kwargs (t.Any): Optional keywords to add to gears dict.

    Returns:
        t.Dict: Updated gears info.
    """

    if isinstance(file_, str):
        info = {}
    elif "object" in file_:
        # file_ passed in from config.json
        info = file_.get("object", {}).get("info", {})
    elif "info" in file_:
        # file_ passing in from SDK.
        info = file_.get("info", {})
    else:
        raise ValueError(
            f"Expected file_ to be dictionary or string, got {type(file_)}"
        )

    gears = {}
    if "gears" not in info:
        info["gears"] = gears
    else:
        gears = info["gears"]
    # overwrite gears.<gear-name> with current gears value

    # destination container to check for gear name, version, job_id
    destination_container = context.get_destination_container().reload()

    if name == "":
        try:
            name = context.manifest["name"]
        except Exception as e:
            raise ValueError("Could not determine gear name from manifest") from e

    if version == "":
        try:
            version = context.manifest["version"]
        except Exception as e:
            raise ValueError("Could not determine gear version from manifest") from e

    if job_id:
        pass
    # elif output of gear is an analysis container, try to get it from there
    elif destination_container.container_type == "analysis":
        job_id = destination_container.get("job", {}).get("id")
        if not (job_id):
            log.warning("Could not determine job id.")

    gear_inputs = {}
    for input_name, file_entry in context.config_json.get("inputs", {}).items():
        if file_entry["base"] != "file":
            continue
        obj = file_entry.get("object", {})
        gear_inputs[input_name] = {
            "parent": file_entry.get("hierarchy"),
            "file_id": obj.get("file_id", ""),
            "version": obj.get("version", ""),
            "file_name": file_entry.get("location", {}).get("name", ""),
        }

    gears.update(
        {
            name: {
                "gear_info": {
                    "name": name,
                    "version": version,
                    "job_id": job_id,
                    "config": {"inputs": gear_inputs, "config": context.config},
                },
                **kwargs,
            }
        }
    )

    info["gears"] = gears

    return info
