from multiprocessing import Queue
from pathlib import Path
import sys
from threading import Thread
import time
import traceback
from typing import Optional, Union

from .utils import (
    _get_archive_checksum,
    _get_or_create_resource_archive,
    generate_random_name,
)
from ..interfaces import Mirror
from ..interfaces.resource import (
    Algorithm,
    Resource,
    ResourceState,
    ResourceUploader,
    ResourceVisibility,
    SyncResourceUploader,
)
from ..storage.db import DB
from ..utils import logger
from ..utils.errors import (
    AnyLearnException,
    AnyLearnMissingParamException,
    AnyLearnNotSupportedException,
)


DEFAULT_TRAIN_PARAMS = "[{\"name\":\"dataset\",\"type\":\"dataset\",\"suggest\":1}]"
DEFAULT_EVAL_PARAMS = "[{\"name\":\"dataset\",\"type\":\"dataset\",\"suggest\":1},\
                        {\"name\":\"model_path\",\"alias\":\"\",\"description\":\"\",\"type\":\"model\",\"suggest\":1}]"


def sync_algorithm(
    id: Optional[str]=None,
    name: Optional[str]=None,
    dir_path: Optional[Union[str, Path]]=None,
    archive_path: Optional[str]=None,
    entrypoint_training: Optional[str]=None,
    output_training: Optional[str]=None,
    entrypoint_evaluation: Optional[str]=None,
    output_evaluation: Optional[str]=None,
    mirror_name: Optional[str]="QUICKSTART",
    uploader: Optional[ResourceUploader]=None,
    polling: Union[float, int]=5,
) -> Algorithm:
    try:
        algo = Algorithm(id=id, load_detail=True)
        algo.mirror_id =_get_quickstart_mirror(mirror_name).id
        # Eval things will be deprecated soon, ignored here
        algo.entrypoint_training = entrypoint_training
        algo.output_training = output_training
        algo.save()
        algo.get_detail()
        return algo
    except:
        algo, archive, upload = _sync_local_algorithm(
            name=name,
            dir_path=dir_path,
            archive_path=archive_path,
            entrypoint_training=entrypoint_training,
            output_training=output_training,
            entrypoint_evaluation=entrypoint_evaluation,
            output_evaluation=output_evaluation,
            mirror_name=mirror_name,
        )
        if archive and upload:
            _upload_algorithm(
                algorithm=algo,
                algorithm_archive=archive,
                uploader=uploader,
                polling=polling,
            )
        return algo


def _sync_local_algorithm(
    name: Optional[str]=None,
    dir_path: Optional[Union[str, Path]]=None,
    archive_path: Optional[str]=None,
    entrypoint_training: Optional[str]=None,
    output_training: Optional[str]=None,
    entrypoint_evaluation: Optional[str]=None,
    output_evaluation: Optional[str]=None,
    mirror_name: Optional[str]="QUICKSTART",
):
    if not any([dir_path, archive_path]):
        raise AnyLearnMissingParamException((
            "None of ['dir_path', 'archive_path'] "
            "is specified."
        ))
    if not name:
        name = f"ALGO_{generate_random_name()}"
    if dir_path is not None and output_training is not None:
        output_training_path = Path(output_training)
        output_training_path_ok = (
            not output_training_path.is_absolute()
            and '..' not in output_training_path.parts
        )
        if output_training_path_ok:
            output_training_path_joined = dir_path / output_training_path
            output_training_path_ok &= (
                not output_training_path_joined.exists()
                or (
                    not output_training_path_joined.is_symlink()
                    and output_training_path_joined.is_dir()
                    and len([*output_training_path_joined.iterdir()]) == 0
                )
            )
        if not output_training_path_ok:
            raise AnyLearnException(
                f'Invalid output path. A relative path without ".." required, '
                f'and that path must be pointing at nothing or an empty '
                f'directory (symlink not allowed). Got '
                f'"{output_training_path}".'
            )
    if dir_path and Path(dir_path).exists():
        _check_algo_minimum_requirements(dir_path)
    archive_path = _get_or_create_resource_archive(
        name=name,
        dir_path=dir_path,
        archive_path=archive_path
    )
    checksum = _get_archive_checksum(archive_path)
    mirror = _get_quickstart_mirror(mirror_name)
    algo, upload = _get_or_create_raw_algorithm(
        name=name,
        checksum=checksum,
        mirror=mirror,
    )
    # Set execution metadata
    algo.mirror_id = mirror.id
    algo.entrypoint_training = entrypoint_training
    algo.output_training = output_training
    algo.entrypoint_evaluation = entrypoint_evaluation
    algo.output_evaluation = output_evaluation
    # Existing/new algo needs respectively create/update towards remote
    algo.save()
    return algo, archive_path, upload


def _check_algo_minimum_requirements(algorithm_dir):
    algo_path = Path(algorithm_dir)
    if not (algo_path / "requirements.txt").exists():
        raise AnyLearnException(("Missing 'requirements.txt' "
                                 "in algorithm folder"))


def _get_or_create_raw_algorithm(
    name: str,
    checksum: str,
    mirror: Mirror,
) -> Optional[Algorithm]:
    to_upload = True
    algo = _get_algorithm_by_name(name)
    if not algo:
        # Exact checksum matching: skip upload
        to_upload = False
        algo = _get_algorithm_by_checksum(checksum)
        if not algo:
            to_upload = True
            algo = _create_new_algorithm(name=name, mirror=mirror)
    return algo, to_upload


def _get_algorithm_by_name(name) -> Optional[Algorithm]:
    try:
        return Algorithm.get_user_custom_algorithm_by_name(name=name)
    except:
        return None


def _get_algorithm_by_checksum(checksum) -> Optional[Algorithm]:
    local_id = DB().find_local_algorithm_by_checksum(checksum=checksum)
    try:
        return Algorithm(id=local_id, load_detail=True)
    except:
        logger.warning(
            f"Local algorithm ({local_id}) "
            "has been deleted remotely, "
            "forced to re-registering algorithm."
        )
        DB().delete_local_algorithm(id=local_id)
        return None


def _create_new_algorithm(name: str, mirror: Mirror) -> Algorithm:
    algo = Algorithm(
        name=name,
        description="SDK_QUICKSTART",
        visibility=ResourceVisibility.PRIVATE,
        filename=f"{name}.zip",
        is_zipfile=True,
        mirror_id=mirror.id,
        train_params=DEFAULT_TRAIN_PARAMS,
        evaluate_params=DEFAULT_EVAL_PARAMS,
        follows_anylearn_norm=False,
    )
    return algo


def _get_quickstart_mirror(name: str) -> Mirror:
    mirrors = Mirror.get_list()
    try:
        return next(m for m in mirrors if m.name == name)
    except:
        raise AnyLearnNotSupportedException((
            f"Container for `{name}` is not supported by "
            "the connected backend."
        ))


def _upload_algorithm(algorithm: Algorithm,
                      algorithm_archive: str,
                      uploader: Optional[ResourceUploader]=None,
                      polling: Union[float, int]=5):
    if not uploader:
        uploader = SyncResourceUploader()
    q = Queue()
    t_algorithm = Thread(
        target=__do_upload,
        args=[q],
        kwargs={
            'resource_id': algorithm.id,
            'file_path': algorithm_archive,
            'uploader': uploader,
        }
    )
    logger.info(f"Uploading algorithm {algorithm.name}...")
    t_algorithm.start()
    err = q.get()
    t_algorithm.join()
    if err:
        ex_type, ex_value, tb_str = err
        message = f"{str(ex_value)} (in subprocess)\n{tb_str}"
        raise ex_type(message)
    algorithm.state = None
    finished = [ResourceState.ERROR, ResourceState.READY]
    while algorithm.state not in finished:
        time.sleep(polling)
        algorithm.get_detail()
    if algorithm.state == ResourceState.ERROR:
        raise AnyLearnException("Error occured when uploading algorithm")
    logger.info("Successfully uploaded algorithm")


def __do_upload(q: Queue, *args, **kwargs):
    try:
        Resource.upload_file(*args, **kwargs)
        err = None
    except:
        ex_type, ex_value, tb = sys.exc_info()
        err = ex_type, ex_value, ''.join(traceback.format_tb(tb))
    q.put(err)
