import subprocess
from typing import Dict, List

import yaml

from kama_sdk.core.core.types import K8sResDict, KteaDict

from kama_sdk.core.ktea.ktea_client import KteaClient

tmp_vars_path = '/tmp/necwiz-tmp-values.yaml'


class LocalExecKteaClient(KteaClient):
  def load_default_values(self) -> Dict[str, str]:
    raw = exec_cmd(self.ktea_config, f"show values . {self.any_cmd_args()}")
    return yaml.load(raw, Loader=yaml.FullLoader)

  def load_preset(self, name: str) -> Dict[str, str]:
    raw = exec_cmd(self.ktea_config, f"show preset {name} {self.any_cmd_args()}")
    return yaml.load(raw, Loader=yaml.FullLoader)

  def template_manifest(self, values) -> List[K8sResDict]:
    write_values_to_tmpfile(values)
    cmd_args = self.template_cmd_args(tmp_vars_path)
    raw = exec_cmd(self.ktea_config, f"template {cmd_args}")
    return list(yaml.load_all(raw, Loader=yaml.FullLoader))


def write_values_to_tmpfile(values: Dict):
  file_content = yaml.dump(values)
  with open(tmp_vars_path, 'w') as file:
    file.write(file_content)


def exec_cmd(ktea: KteaDict, cmd):
  uri, ver = ktea['uri'], ktea.get('version')
  exec_name = f"{uri}:{ver}" if ver else uri
  full_cmd = f"{exec_name} {cmd}".split(" ")
  output = subprocess.check_output(full_cmd).decode('utf-8')
  return output
