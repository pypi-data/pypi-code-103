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
  def render(cls, image, _format='JPEG', **kwargs):
    bytes_io = io.BytesIO()
    image.save(bytes_io, _format)
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
