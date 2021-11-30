import pytest

from monite.services.file_saver.schemas import (
    FileInfoResponse,
    FileSchema,
    PreviewSchema,
)


@pytest.mark.asyncio
def test_file_schemas():
    preview_scheme = PreviewSchema(url="https://google.com", width=640, height=480)

    file_scheme = FileSchema(
        file_type="some str",
        name="some str",
        region="some str",
        md5="some str",
        mimetype="some str",
        url="some str",
        size=1024,
        previews=[preview_scheme],
    )

    scheme = FileInfoResponse(data=file_scheme)

    assert isinstance(preview_scheme.dict(), dict)
    assert isinstance(file_scheme.dict(), dict)
    assert isinstance(scheme.dict(), dict)
