import json
import io

from abc import ABC, abstractmethod
from flask import send_file

# TODO: move render classes
class AbstractRenderer(ABC):
  @abstractmethod
  def render(data):
    pass

class JsonRenderer(AbstractRenderer):
  @classmethod
  def render(cls, data):
    return json.dumps(data)

class FileRenderer(AbstractRenderer):
  @classmethod
  def render(cls, binary, filename='file', content_type=None, downloadable=False):
    return send_file(
      binary,
      mimetype=content_type,
      as_attachment=downloadable,
      download_name=filename,
    )

class PilImageRenderer(FileRenderer):
  @classmethod
  def render(cls, image, content_format=None, **kwargs):
    image.format = content_format or 'JPEG'

    if 'content_type' not in kwargs:
      kwargs['content_type'] = image.get_format_mimetype() or 'image/jpeg'

    bytes_io = io.BytesIO()
    image.save(bytes_io, image.format)
    bytes_io.seek(0)

    return super().render(bytes_io, **kwargs)

class NaogiModel(ABC):
  def __init__(self):
    super()
    self.model = None

  @abstractmethod
  def predict(self):
    pass

  @abstractmethod
  def load_model(self):
    pass

  @abstractmethod
  def prepare(self):
    pass

  def renderer(self):
    return JsonRenderer

  def render_options_dict(self):
    return dict()

  def _render(self, result):
    return self.renderer().render(result, **self.render_options_dict())
