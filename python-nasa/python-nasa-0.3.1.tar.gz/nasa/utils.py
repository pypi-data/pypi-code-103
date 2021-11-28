from io import BytesIO
from warnings import warn
from typing import Iterable, List, Optional, Text
import requests
from tqdm.auto import tqdm
from PIL import Image
from PIL.ImageFile import ImageFile

from nasa.exceptions import NASAContentTypeNotImage
from nasa.warnings import InvalidInputWarning


def get_url_image(
    url: Text, chunk_size: int = 1024, ignore_non_image: bool = False
) -> Optional[ImageFile]:
    """Parse Response Content Image to PIL Image

    Args:
        url (Text): URL containing image
        chunk_size (int, optional): Chunk Size on downloading Image. Defaults to 1024.
        ignore_non_image (bool, optional): If True, Gave warning but return None, else raise an error. Defaults to False.

    Raises:
        NASAContentTypeNotImage: The response content type is not image.

    Returns:
        ImageFile: PIL ImageFile Object
    """
    with requests.get(url, stream=True) as response:
        content_type: Text = response.headers.get("Content-Type")
        if content_type.split("/")[0] == "image":
            content_length: int = int(response.headers.get("Content-Length", 0))
            content: bytes = bytes()
            desc: Text = f"Download Image from {response.url}"
            with tqdm(total=content_length, unit_scale=True, desc=desc) as progress:
                for c in response.iter_content(chunk_size=chunk_size):
                    progress.update(len(c))
                    content += c
            image: ImageFile = Image.open(BytesIO(content))
            return image
        elif ignore_non_image:
            message: Text = "Response Content-Type is not Image."
            warn(message, InvalidInputWarning)
            return None
        else:
            message: Text = "Response Content-Type is not Image."
            raise NASAContentTypeNotImage(message)


def get_urls_images(
    urls: Iterable[Text], chunk_size: int = 1024, ignore_non_image: bool = False
) -> List[Optional[ImageFile]]:
    """Parse response contents from list of urls to list of image

    Args:
        urls (Iterable[Text]): List of URLs containing images
        ignore_non_image (bool, optional): If True, Gave warning but return None, else raise an error. Defaults to False.

    Returns:
        List[Optional[ImageFile]]: List of PIL ImageFile Object
    """
    return [get_url_image(url, chunk_size, ignore_non_image) for url in tqdm(urls)]
