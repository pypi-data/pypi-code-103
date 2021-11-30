from monite.services.file_saver.v1.enums import AllowedFileTypes, AllowedRegions
from monite.shared.schemas import MessageResponse


def test_msg_response():
    resp = MessageResponse.validate({"message": "ok"})
    assert isinstance(resp.dict(), dict)


def test_ftype_enum():
    assert AllowedFileTypes.payables == "payables"
    assert AllowedFileTypes.ocr_files == "ocr-files"
    assert AllowedFileTypes.receipts == "receipts"
    assert AllowedFileTypes.userpics == "userpics"


def test_region_enum():
    assert AllowedRegions.eu_central_1 == "eu-central-1"
