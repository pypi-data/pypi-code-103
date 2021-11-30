import os
from typing import List, Dict, Type

from cert_manager_plugin.consts import PLUGIN_ID
from kama_sdk.core.core.plugin_type_defs import PluginManifest
from kama_sdk.model.base.model import Model
from kama_sdk.utils.descriptor_utils import load_dir_yamls


def get_manifest():
  return PluginManifest(
    id=PLUGIN_ID,
    publisher_identifier='nmachine',
    app_identifier='cert-manager-plugin',
    model_descriptors=gather_model_descriptors(),
    asset_paths=[assets_path],
    model_classes=gather_custom_models(),
    virtual_kteas=[]
  )


def gather_custom_models() -> List[Type[Model]]:
  return [
  ]

def gather_model_descriptors() -> List[Dict]:
  return load_dir_yamls(descriptors_path, recursive=True)


root_dir = os.path.dirname(os.path.abspath(__file__))
descriptors_path = f'{root_dir}/descriptors'
assets_path = f'{root_dir}/assets'
