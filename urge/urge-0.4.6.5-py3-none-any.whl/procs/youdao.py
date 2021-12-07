import os
import json
import httpx
from httpx import Response
import typing as t
import base64
from uuid import uuid1
from functools import partial as pf

# from .. import utils
# from ..base import ProcManager
from urge import utils
from urge.base import ProcManager
from dao.config import *
from dao.models import Result
from dao.api import P
from dao.errors import ServiceError

TRANS_URL = "https://ke.study.163.com/code/textTrans"
OCR_URL = "https://ke.study.163.com/code/ocrTrans"
FREE_MAP = {
    "trans": TransConfig(api=TRANS_URL),
    "ocr": OCRConfig(api=OCR_URL),
    "receipt": OCRReceipt(api=""),
    "table": OCRTableConfig(api=""),
    "pictrans": OCRPicTrans(api=""),
}


def post_builder(name, **kwd):
    token = os.getenv("token") or os.getenv("XXX")
    # token = "tYwB%2FcQm2vlyCP1oP%2FRujV%2FPGfbkexMUPhrT%2BtOkIOmcEvbrs%2BuXh5XOk78v%2FGS9i%2B1dNra7zbXZp75%2BiyTT3LaQioa7GNhh5tXe9k%2FBFj8%3D"
    if token:
        _token = {"token": token}

        def free_post(q, *args, **kwd) -> Result:

            _config = FREE_MAP[name]
            _query = {_config.Q: q}
            _params = P(
                _type="json",
                url=_config.API,
                headers=_token,
                params={**_query, **_config.CONFIG, **kwd},
            )
            resp = httpx.post(**_params).json()
            code = int(resp["code"])
            content = resp["data"]

            return Result(Response(content=content, status_code=code))

        return free_post

    else:
        from dao.api import Api

        api = Api()

        @api(name)
        def _post(q, *args, **kwd) -> Result:

            ...

        return _post


# =============================== Translate functions ===============================


def trans_post(q: str, **kwargs) -> t.Union[Result, dict]:
    trans_post = post_builder("trans")
    res = trans_post(q)
    return {"res": res, **kwargs}


def trans_filter(res: Result, full=False):
    # There will be a problem when using token
    basic = res.result.get("basic")
    d = {}
    if basic:
        # if basic exists, q must be one word,
        basic = utils.drop(basic, keys=["us-speech", "uk-speech"])
        basic["web_dict"] = res.result.get("webdict").get("url")
        d["simple_translation"] = res.result.get("translation")[0]
        d.update(basic)
        if not full:
            d = d.get("explains")

    else:
        # else many words
        d["oneline"] = res.result["translation"]
        return d["oneline"][0]
    return d


def translate(q: str, full: bool = False):
    p = ProcManager(trans_post, pf(trans_filter, full=full))
    return p(dict(q=q))


def simple_translate(q):
    if " " in q:
        raise ValueError("Only for word")
    res = translate(q, full=True)
    return res["simple_translation"][0]


# ===============================  Pic to pic translate ===============================


def pictrans_post(b64: t.ByteString):
    post = post_builder("pictrans")
    res = post(b64)
    return res


def pictrans_write(res: Result, target: str = "./"):
    b = res.result.get("render_image")
    name = str(uuid1()).split("-")[0]
    pic_path = f"{target}{name}.png"
    base64_img_bytes = b.encode("utf-8")
    with open(pic_path, "wb") as file_to_save:
        decoded_image_data = base64.decodebytes(base64_img_bytes)
        file_to_save.write(decoded_image_data)
    return res


def pic_translate(path: str):
    p = ProcManager(pic2base64, pictrans_post, pictrans_write)
    return p(dict(path=path))


# =============================== Utils functions ===============================


def pic2base64(path: str, **kwargs):
    with open(path, "rb") as f:
        # q = base64.b64encode(f.read())
        return base64.b64encode(f.read()).decode("utf-8")
        # return q.decode('utf-8')


def base642Raw():
    ...


# ===============================  General OCR functions ===============================
def ocr_post(b64: t.ByteString):
    ocr_req = post_builder("ocr")
    res = ocr_req(b64)
    return res


def ocr_ret(res: Result, **kwargs) -> t.Optional[t.List]:
    text_list = []
    Result = res.result.get("Result")
    if Result:
        items = Result.get("regions")
        for item in items:
            for l in item["lines"]:
                text_list.append(l["text"])

        return text_list


def easy_ocr(path: str):
    p = ProcManager(pic2base64, ocr_post, ocr_ret)
    return p(dict(path=path))


# ===============================  Receipt OCR functions ===============================
def receipt_ocr_post(b64: t.ByteString):
    post = post_builder("receipt")
    res = post(b64)
    return res


def receipt_ocr_ret(res: Result):

    d = {}
    if res.err == 0:
        items = res.result.get("Result").get("items")
        for i in items:
            key = i["key"]
            value = i["value"]
            d[key] = value

    else:
        raise ServiceError(res.err)
    return d


def receipt_ocr(path: str):
    p = ProcManager(pic2base64, receipt_ocr_post, receipt_ocr_ret)
    return p(dict(path=path))


# =============================== Table(excel) OCR functions ===============================


def table_ocr_post(b64: t.ByteString):
    table_ocr = post_builder("table")
    res = table_ocr(b64)
    return res


def table_write_excel(res: Result, target: t.Text = "./"):
    tables = res.result.get("Result").get("tables")
    name = str(uuid1()).split("-")[0]
    xlsx_path = f"{target}{name}.xlsx"
    for t in tables:
        base64_img_bytes = t.encode("utf-8")
        with open(xlsx_path, "wb") as file_to_save:
            decoded_image_data = base64.decodebytes(base64_img_bytes)
            file_to_save.write(decoded_image_data)
    return res


def table_ocr(path: str):
    p = ProcManager(pic2base64, table_ocr_post, table_write_excel)
    return p(dict(path=path))


# ===============================  Deprecated ===============================
