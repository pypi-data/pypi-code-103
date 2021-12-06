import os

from galleries.annotations_parsers.gallery_annots_parsers import GalleryAnnotationsParser


class FileNameSepParser(GalleryAnnotationsParser):
	"""
	Parser para obtener anotaciones a partir del nombre de las imágenes.
	El nombre del fichero es dividido con un separador y cada elemento obtenido es una anotación.
	Ejemplo:
		fp = FileNameSepParser(('label', 'age', 'sex'), sep='_')
		annots = fp('C:/dir/Fulano_32_M.jpg')

	annots va a ser igual a:
	{ 'label': 'Fulano', 'age': '32', 'sex': 'M' }
	"""

	def __init__(self, annot_names=None, sep='-'):
		self.annot_names = annot_names or []
		self.sep = sep

	def __call__(self, img_path: str) -> dict:
		return self.get_annotations_by_image_index(img_path)

	def get_annotations_by_image_index(self, img_index: str) -> dict:
		_, file = os.path.split(img_index)
		filename, _ = os.path.splitext(file)
		tokens = self._split_tokens(filename)
		annots = {}
		annots.keys()
		for i, token in enumerate(tokens):
			if i == len(self.annot_names):
				break
			annot_name = self.annot_names[i]
			annots[annot_name] = token
		return annots

	def _split_tokens(self, filename: str):
		if len(self.sep) == 1:
			return filename.split(sep=self.sep)
		else:
			tokens = []
			string = filename
			for separator in self.sep:
				token, string = string.split(separator, 1)
				tokens.append(token)
			return tokens