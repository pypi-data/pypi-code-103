from typing import List, Optional

from kama_sdk.core.core.config_man import config_man, IS_PROTOTYPE_KEY, INSTALL_ID_KEY, KTEA_CONFIG_KEY
from kama_sdk.core.core.plugin_type_defs import PluginManifest, SlimPluginManifest
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.utils.logging import lwar


class PluginsManager:
  _slim_manifests: List[SlimPluginManifest]

  def __init__(self):
    self._slim_manifests = []

  def get_plugin_ids(self) -> List[str]:
    return [m['id'] for m in self._slim_manifests]

  def write_kamafile_entry(self, plugin_id: str):
    if manifest := self.get_manifest(plugin_id):
      if ktea_config := manifest.get('prototype_mode_ktea'):
        config_man.write_space({
          INSTALL_ID_KEY: '',
          IS_PROTOTYPE_KEY: True,
          KTEA_CONFIG_KEY: ktea_config
        }, space=plugin_id)
      else:
        msg = f"could not create entry as {plugin_id} has no prototype config"
        lwar(msg)

  def get_manifest(self, plugin_id: str) -> Optional[SlimPluginManifest]:
    finder = lambda meta: meta['id'] == plugin_id
    return next(filter(finder, self._slim_manifests), None)

  def get_registered_plugin_ids(self) -> List[str]:
    def is_registered(_id: str) -> bool:
      return config_man.get_install_token(space=_id) is not None
    return list(filter(is_registered, self.get_plugin_ids()))

  def register_manifest(self, manifest: PluginManifest):
    plugin_id = manifest['id']
    version = manifest.get('version')

    app_identifier = manifest.get('app_identifier')
    org_identifier = manifest.get('publisher_identifier')

    model_descriptors = manifest.get('model_descriptors', [])
    model_classes = manifest.get('model_classes', [])
    asset_paths = manifest.get('asset_paths', [])

    models_manager.add_any_descriptors(model_descriptors, plugin_id)
    models_manager.add_models(model_classes)
    models_manager.add_asset_dir_paths(asset_paths)

    self._slim_manifests.append(SlimPluginManifest(
      id=plugin_id,
      app_identifier=app_identifier,
      publisher_identifier=org_identifier,
      version=version,
      prototype_mode_ktea=manifest.get('prototype_mode_ktea')
    ))

  def register(self, **kwargs):
    if manifest := kwargs.get('manifest'):
      self.register_manifest(manifest)
    else:
      lwar("neither 'manifest' or 'module_name' in kwargs")


plugins_manager = PluginsManager()
