from kama_sdk.model.supplier.base.supplier import Supplier


class ImageSrcSupplier(Supplier):

  def _compute(self) -> str:
    hint: str = self.get_source_data()
    final = hint.lower().strip()
    parts = final.split("/")

    if parts[0] not in types:
      parts.append('services')

    if parts[-1] not in sizes:
      parts.append('medium')

    if not parts[-1].endswith(".png"):
      parts[-1] = f"{parts[-1]}.png"

    slug_end = "/".join(parts)

    return f"{base}/{slug_end}"


TYPE_KEY = 'type'
base = "https://storage.googleapis.com/nectar-mosaic-public/images/kama"
sizes = ['small', 'medium', 'large']
types = ['services', 'kubernetes']
