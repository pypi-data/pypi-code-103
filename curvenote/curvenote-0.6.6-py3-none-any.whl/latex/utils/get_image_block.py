import logging
import os

import requests

from curvenote.latex.utils.imagemagick import convert_gif

from ...client import Session
from ...models import BlockFormat, BlockVersion
from .links import oxa_path_to_api_url
from .localize_images import ImageFormats


def get_image_block(
    session: Session,
    assets_folder: str,
    oxa_path: str,
    local_path: str,
    fmt: BlockFormat,
):
    url = oxa_path_to_api_url(session.api_url, oxa_path, fmt)
    logging.info("fetching image block from %s", url)
    image_block = session.get_model(url, BlockVersion)
    if not image_block:
        raise ValueError(f"Could not fetch image block {url}")

    # download from links.download (signed) to local path
    if not image_block.links.download:
        raise ValueError(f"Block kind {image_block.kind} has no download link")

    resp = requests.get(image_block.links.download)
    if resp.status_code >= 400:
        raise ValueError(resp.content)

    # now that we have the block we need to update the local path in the content
    # and save the file with the correct file extension
    content_type = resp.headers.get("content-type")
    if content_type not in ImageFormats:
        raise ValueError(f"Unsupported image content type {content_type}")

    ext = ImageFormats[content_type]
    local_path_with_extension = f"{local_path}.{ext}"
    logging.info("Writing %s", local_path_with_extension)
    with open(os.path.join(assets_folder, local_path_with_extension), "wb+") as file:
        file.write(resp.content)

    if content_type == "image/gif":
        logging.info("Found image/gif converting to image/png")
        # convert to png, leave gif file in place but return the png path for use in content
        local_path_with_extension = convert_gif(
            assets_folder, local_path_with_extension
        )
        logging.info("Updated local path: %s" % local_path_with_extension)
        # either calls will raise exception on error causing file to be skipped

    return image_block, local_path_with_extension
