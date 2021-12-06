import os

from galleries.annotations_parsers.gallery_annots_parsers import GalleryAnnotationsParser


class FolderParser(GalleryAnnotationsParser):
	"""
	Parser para obtener anotaciones a partir del directorio de las imágenes.
	Las anotaciones se obtienen El nombre del fichero es dividido con un separador y cada elemento obtenido es una anotación.
	Ejemplo 1:
		fp = FolderParser((('label', 'age', 'sex'), sep='_'))
		annots = fp('C:/Fulano_32_M/img1.jpg')

	annots va a ser igual a:
	{ 'label': 'Fulano', 'age': '32', 'sex': 'M' }

	Ejemplo 2:
		fp = FolderParser([(('label', 'age', 'sex'), sep='_'), (('video')])
		annots = fp('C:/Video1/Fulano_32_M/img1.jpg')

	annots va a ser igual a:
	{ 'label': 'Fulano', 'age': '32', 'sex': 'M', 'video': 'Video1' }
	"""

	def __init__(self, annot_names=None, sep='-'):
		self.annot_names = annot_names or []
		self.sep = sep

	def __call__(self, img_path: str) -> dict:
		return self.get_annotations_by_image_index(img_path)

	def get_annotations_by_image_index(self, img_index: str) -> dict:
		_, file = os.path.split(img_index)
		filename, _ = os.path.splitext(file)
		tokens = filename.split(sep=self.sep)
		annots = {}
		annots.keys()
		for i, token in enumerate(tokens):
			if i == len(self.annot_names):
				break
			annot_name = self.annot_names[i]
			annots[annot_name] = token
		return annots