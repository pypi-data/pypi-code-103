import abc


class GalleryAnnotationsParser(abc.ABC):

	@abc.abstractmethod
	def get_annotations_by_image_index(self, img_index: str) -> dict:
		pass
