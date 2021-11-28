import hashlib
import os
import urllib
import warnings
from typing import Any, Union, List
from pkg_resources import packaging
from pathlib import Path

import torch
import pandas as pd
from PIL import Image
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from tqdm.auto import tqdm

from .model import build_model
from .simple_tokenizer import SimpleTokenizer as _Tokenizer

try:
	from torchvision.transforms import InterpolationMode
	BICUBIC = InterpolationMode.BICUBIC
except ImportError:
	BICUBIC = Image.BICUBIC

if packaging.version.parse(torch.__version__) < packaging.version.parse("1.7.1"):
	warnings.warn("PyTorch version 1.7.1 or higher is recommended")

__all__ = ["available_models", "load", "tokenize", "CLIP", "multiclassify"]
_tokenizer = _Tokenizer()

_MODELS = {
    "RN50":
        "https://openaipublic.azureedge.net/clip/models/afeb0e10f9e5a86da6080e35cf09123aca3b358a0c3e3b6c78a7b63bc04b6762/RN50.pt",
    "RN101":
        "https://openaipublic.azureedge.net/clip/models/8fa8567bab74a42d41c5915025a8e4538c3bdbe8804a470a72f30b0d94fab599/RN101.pt",
    "RN50x4":
        "https://openaipublic.azureedge.net/clip/models/7e526bd135e493cef0776de27d5f42653e6b4c8bf9e0f653bb11773263205fdd/RN50x4.pt",
    "RN50x16":
        "https://openaipublic.azureedge.net/clip/models/52378b407f34354e150460fe41077663dd5b39c54cd0bfd2b27167a4a06ec9aa/RN50x16.pt",
    "ViT-B/32":
        "https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt",
    "ViT-B/16":
        "https://openaipublic.azureedge.net/clip/models/5806e77cd80f8b59890b7e101eabd078d9fb84e6937f9e85e4ecb61988df416f/ViT-B-16.pt",
}


def _download(url: str, root: str):
	os.makedirs(root, exist_ok=True)
	filename = os.path.basename(url)

	expected_sha256 = url.split("/")[-2]
	download_target = os.path.join(root, filename)

	if os.path.exists(download_target) and not os.path.isfile(download_target):
		raise RuntimeError(f"{download_target} exists and is not a regular file")

	if os.path.isfile(download_target):
		if hashlib.sha256(open(download_target, "rb").read()).hexdigest() == expected_sha256:
			return download_target
		else:
			warnings.warn(
			    f"{download_target} exists, but the SHA256 checksum does not match; re-downloading the file"
			)

	with urllib.request.urlopen(url) as source, open(download_target, "wb") as output:
		with tqdm(total=int(source.info().get("Content-Length")),
		          ncols=80,
		          unit='iB',
		          unit_scale=True,
		          unit_divisor=1024) as loop:
			while True:
				buffer = source.read(8192)
				if not buffer:
					break

				output.write(buffer)
				loop.update(len(buffer))

	if hashlib.sha256(open(download_target, "rb").read()).hexdigest() != expected_sha256:
		raise RuntimeError(f"Model has been downloaded but the SHA256 checksum does not not match")

	return download_target


def _convert_image_to_rgb(image):
	return image.convert("RGB")


def _transform(n_px):
	return Compose([
	    Resize(n_px, interpolation=BICUBIC),
	    CenterCrop(n_px),
	    _convert_image_to_rgb,
	    ToTensor(),
	    Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
	])


def available_models() -> List[str]:
	"""Returns the names of available CLIP models"""
	return list(_MODELS.keys())


def load(name: str,
         device: Union[str, torch.device] = "cuda" if torch.cuda.is_available() else "cpu",
         jit: bool = False,
         download_root: str = None):
	"""Load a CLIP model

    Parameters
    ----------
    name : str
        A model name listed by `clip.available_models()`, or the path to a model checkpoint containing the state_dict

    device : Union[str, torch.device]
        The device to put the loaded model

    jit : bool
        Whether to load the optimized JIT model or more hackable non-JIT model (default).

    download_root: str
        path to download the model files; by default, it uses "~/.cache/clip"

    Returns
    -------
    model : torch.nn.Module
        The CLIP model

    preprocess : Callable[[PIL.Image], torch.Tensor]
        A torchvision transform that converts a PIL image into a tensor that the returned model can take as its input
    """
	if name in _MODELS:
		model_path = _download(_MODELS[name], download_root or os.path.expanduser("~/.cache/clip"))
	elif os.path.isfile(name):
		model_path = name
	else:
		raise RuntimeError(f"Model {name} not found; available models = {available_models()}")

	try:
		# loading JIT archive
		model = torch.jit.load(model_path, map_location=device if jit else "cpu").eval()
		state_dict = None
	except RuntimeError:
		# loading saved state dict
		if jit:
			warnings.warn(f"File {model_path} is not a JIT archive. Loading as a state dict instead")
			jit = False
		state_dict = torch.load(model_path, map_location="cpu")

	if not jit:
		model = build_model(state_dict or model.state_dict()).to(device)
		if str(device) == "cpu":
			model.float()
		return model, _transform(model.visual.input_resolution)

	# patch the device names
	device_holder = torch.jit.trace(lambda: torch.ones([]).to(torch.device(device)),
	                                example_inputs=[])
	device_node = [
	    n for n in device_holder.graph.findAllNodes("prim::Constant") if "Device" in repr(n)
	][-1]

	def patch_device(module):
		try:
			graphs = [module.graph] if hasattr(module, "graph") else []
		except RuntimeError:
			graphs = []

		if hasattr(module, "forward1"):
			graphs.append(module.forward1.graph)

		for graph in graphs:
			for node in graph.findAllNodes("prim::Constant"):
				if "value" in node.attributeNames() and str(node["value"]).startswith("cuda"):
					node.copyAttributes(device_node)

	model.apply(patch_device)
	patch_device(model.encode_image)
	patch_device(model.encode_text)

	# patch dtype to float32 on CPU
	if str(device) == "cpu":
		float_holder = torch.jit.trace(lambda: torch.ones([]).float(), example_inputs=[])
		float_input = list(float_holder.graph.findNode("aten::to").inputs())[1]
		float_node = float_input.node()

		def patch_float(module):
			try:
				graphs = [module.graph] if hasattr(module, "graph") else []
			except RuntimeError:
				graphs = []

			if hasattr(module, "forward1"):
				graphs.append(module.forward1.graph)

			for graph in graphs:
				for node in graph.findAllNodes("aten::to"):
					inputs = list(node.inputs())
					for i in [1, 2]:  # dtype can be the second or third argument to aten::to()
						if inputs[i].node()["value"] == 5:
							inputs[i].node().copyAttributes(float_node)

		model.apply(patch_float)
		patch_float(model.encode_image)
		patch_float(model.encode_text)

		model.float()

	return model, _transform(model.input_resolution.item())


def tokenize(texts: Union[str, List[str]],
             context_length: int = 77,
             truncate: bool = False) -> torch.LongTensor:
	"""
    Returns the tokenized representation of given input string(s)

    Parameters
    ----------
    texts : Union[str, List[str]]
        An input string or a list of input strings to tokenize

    context_length : int
        The context length to use; all CLIP models use 77 as the context length

    truncate: bool
        Whether to truncate the text in case its encoding is longer than the context length

    Returns
    -------
    A two-dimensional tensor containing the resulting tokens, shape = [number of input strings, context_length]
    """
	if isinstance(texts, str):
		texts = [texts]

	sot_token = _tokenizer.encoder["<|startoftext|>"]
	eot_token = _tokenizer.encoder["<|endoftext|>"]
	all_tokens = [[sot_token] + _tokenizer.encode(text) + [eot_token] for text in texts]
	result = torch.zeros(len(all_tokens), context_length, dtype=torch.long)

	for i, tokens in enumerate(all_tokens):
		if len(tokens) > context_length:
			if truncate:
				tokens = tokens[:context_length]
				tokens[-1] = eot_token
			else:
				raise RuntimeError(f"Input {texts[i]} is too long for context length {context_length}")
		result[i, :len(tokens)] = torch.tensor(tokens)

	return result


class CLIP:
	"""CLIP class allowing for incredibly simple interaction."""

	def __init__(self, model_name: str = "ViT-B/16", jit: bool = False):
		"""Load model.

		Args:
			model_name (str): Name of CLIP model to use
			jit (bool): Selection of just-in-time model
		"""
		self.device = "cuda" if torch.cuda.is_available() else "cpu"
		self.model, self.preprocess = load(model_name, self.device, jit=jit)

	def process_image(self, path: Union[str, Path]):
		"""Process and encode image.

		Args:
			path (str | Path): Path to image

		Returns:
			torch.Tensor: Image features

		"""
		image = self.preprocess(Image.open(path)).unsqueeze(0)
		return self.model.encode_image(image)

	def process_text(self, labels: List[str]):
		"""Process and encode text labels.

		Args:
			labels (List[str]): List of potential labels by which CLIP classifies the image

		Returns:
			torch.Tensor: Text features

		"""
		labels = torch.cat([tokenize(f"a photo of a {l}") for l in labels]).to(self.device)
		return self.model.encode_text(labels)

	def classify(self, image_path: Union[str, Path], labels: List[str], top_n: int = -1) -> dict:
		"""Classify an image based on a list of labels
			
		Args:
			image_path (str | Path): Path to image to classify
			labels (List[str]): List of labels to assign probability of image contents belonging to

		Returns:
			results (dict): Labels and their associated probabilities
		"""
		# Calculate features
		with torch.no_grad():
			image_features = self.process_image(image_path)
			text_features = self.process_text(labels)

		# Get results
		image_features /= image_features.norm(dim=-1, keepdim=True)
		text_features /= text_features.norm(dim=-1, keepdim=True)
		similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

		# Return results as dictionary
		results = similarity[0].topk(len(labels) if top_n == -1 else top_n)
		return {labels[i]: probability.item() for probability, i in zip(*results)}


def multiclassify(image_paths: Union[List[str], List[Path]],
                  labels: List[str],
                  show_progress: bool = True,
                  model_name: str = "ViT-B/16",
                  jit: bool = False) -> dict:
	"""Classify a batch of images based on a single list of classifiers.

	Args:
		image_paths (List[str] | List[Path]): List of images to classify
		labels (List[str]): List of potential labels by which CLIP classifies the image
		show_progress(bool): Show progress bar
		model_name (str): Name of CLIP model to use
		jit (bool): Selection of just-in-time model

	Returns:
		results (dict): Dictionary of images and their classifications

	"""
	c = CLIP(model_name=model_name, jit=jit)
	paths = tqdm(image_paths) if show_progress else image_paths
	results = {label: [] for label in ["ImagePath", *labels]}
	for path in paths:
		path = Path(path).expanduser()
		if show_progress:
			paths.set_description(desc=path.name)
		results["ImagePath"].append(str(path))
		for label, probability in c.classify(path, labels).items():
			results[label].append(probability)
		if show_progress:
			paths.update(1)
	return pd.DataFrame(results)
