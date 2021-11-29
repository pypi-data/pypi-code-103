import datetime
import json
import logging
import mimetypes
import operator
import os
import shutil
import uuid

import httpx
from fastapi import Header
from fastapi import HTTPException
from fastapi import UploadFile

from backend_library_common.models.main import FrameInfo
from backend_library_common.utils.params import MIN_FREE_DISK_SPACE


def get_top_5(frame: FrameInfo):
    top_5 = sorted(
        frame.prediction.belief.__dict__.items(), key=operator.itemgetter(1)
    )[-5:]

    top_5_list = []
    for t in top_5:
        top_5_list.append(t[1])

    return top_5_list[len(top_5_list) - 1], top_5_list


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return obj.to_json()
        elif isinstance(obj, uuid.UUID):
            return obj.hex
        elif isinstance(obj, datetime.time):
            return str(obj)
        else:
            return obj.__dict__


def check_free_disk_space(storage_path: str):
    _, _, free = shutil.disk_usage(storage_path)
    free = free // (2 ** 30)
    if free < MIN_FREE_DISK_SPACE:
        error_msg_str = "not enough free disk space (free space: {} GB)".format(free)
        logging.warning(error_msg_str)
        raise HTTPException(status_code=507, detail=error_msg_str)


def check_empty_file(save_path: str):
    if os.stat(save_path).st_size == 0:
        raise HTTPException(status_code=406, detail="file is empty")


def check_data_type(save_path: str, data: UploadFile, data_type: str):
    file_type = mimetypes.guess_type(save_path)[0]
    if file_type is not None and file_type.startswith(data_type):
        logging.debug("data is {}: {}".format(data_type, data.filename))
    else:
        os.remove(save_path)
        error_msg_str = "might not be a video file: {}".format(save_path)
        logging.warning(error_msg_str)
        raise HTTPException(status_code=406, detail=error_msg_str)


def verify_role(role: str):
    async def _verify_role(x_auth_roles: str = Header(...)):
        if x_auth_roles is None or role not in x_auth_roles.split(","):
            raise HTTPException(status_code=403, detail=f"missing role {role}")
        return x_auth_roles

    return _verify_role


async def db_response(
    prediction_id: uuid.UUID,
    db_url: str,
    db_field: str,
    db_endpoint: str,
    isfile=False,
):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{db_url}/{db_endpoint}/{str(prediction_id)}")
        if response.is_error:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        db_data = response.json()[db_field]
        if (isfile and db_data is None) or (isfile and not os.path.isfile(db_data)):
            raise HTTPException(status_code=404, detail="data not found")

    return db_data
