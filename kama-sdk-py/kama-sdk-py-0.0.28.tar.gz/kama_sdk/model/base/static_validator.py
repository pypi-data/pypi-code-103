from typing import Any, List, Optional, Dict

import yaml
from termcolor import colored, cprint
from typing_extensions import TypedDict

from kama_sdk.model.base import mc
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.utils.logging import lwar


class Violation(TypedDict):
  severity: str
  id: Optional[str]
  type: str
  message: Optional[str]
  desc: Optional[Dict]


def run_all():
  try:
    violations = []
    violations.extend(perform_top_level_validations())
    render_violations(violations)
  except Exception as e:
    lwar(f"static check failed: {str(e)}")


def render_violations(violations: List[Violation]):
  if len(violations) > 0:
    cprint(f"\n{'*' * 53}", 'magenta')
    cprint(f"                  {len(violations)} PROBLEMS FOUND", attrs=['bold'])
    cprint(f"{'*' * 53}\n", 'magenta')
    for violation in violations:
      render_violation(violation)
    print("")


def render_violation(violation: Violation):
  _id = violation['id']
  severity = violation['severity']
  message = violation['message']
  _type = violation['type']
  desc = violation['desc']

  color = "red" if severity == 'error' else 'magenta'

  cprint(f"\n{severity.upper()} {_type}", color, attrs=['bold'])

  if desc:
    cprint("For")
    cprint(f"{yaml.dump(desc, indent=5)}")
  else:
    print(f"For {colored(_id, attrs=['underline'])}")

  if message:
    cprint(message, color)

def descriptor_id_refs(descriptor: Any) -> List[str]:
  id_refs = []
  if type(descriptor) == dict:
    for sub_tree in descriptor.values():
      new_refs = descriptor_id_refs(sub_tree)
      id_refs.extend(new_refs)
  elif type(descriptor) == list:
    for item in descriptor:
      new_refs = descriptor_id_refs(item)
      id_refs.extend(new_refs)
  elif type(descriptor) == str:
    if descriptor.startswith(mc.ID_REFERENCE_PREFIX):
      if "${" not in descriptor:
        id_refs.append(descriptor)
    elif descriptor.startswith(mc.KIND_REFERENCE_PREFIX):
      id_refs.append(descriptor)
  return id_refs


def perform_top_level_validations() -> List[Violation]:
  violations: List[Violation] = []
  descriptors = models_manager.get_descriptors()
  for descriptor in descriptors:
    if ref_violation := ensure_top_level_to_child_refs(descriptor):
      violations.append(ref_violation)

    if id_violation := ensure_top_level_id_present(descriptor):
      violations.append(id_violation)

    if kind_violation := ensure_kind_class_exists(descriptor):
      violations.append(kind_violation)

  return violations


def ensure_top_level_to_child_refs(descriptor: Dict) -> Optional[Violation]:
  refs = descriptor_id_refs(descriptor)
  for ref in refs:
    can_handle = True
    referee = None

    un_prefixed_ref = ref.split("::")[-1]
    if ref.startswith(mc.ID_REFERENCE_PREFIX):
      referee = models_manager.find_any_config_by_id(un_prefixed_ref)
    elif ref.startswith(mc.KIND_REFERENCE_PREFIX):
      referee = models_manager.find_any_class_by_name(un_prefixed_ref)
    else:
      can_handle = False

    if can_handle and not referee:
      return Violation(
        severity='error',
        id=descriptor.get('id'),
        type='Broken reference',
        message=f"Target --> {un_prefixed_ref} not found",
        desc=None
      )


def ensure_top_level_id_present(descriptor: Dict) -> Optional[Violation]:
  _id = descriptor.get('id')
  if not _id:
    return Violation(
      severity='error',
      id=None,
      type="Missing top-level property 'id'",
      message=None,
      desc=descriptor
    )


def ensure_kind_class_exists(descriptor: Dict) -> Optional[Violation]:
  if kind := descriptor.get('kind'):
    if not models_manager.find_any_class_by_name(kind):
      return Violation(
        severity='error',
        type='No class for kind',
        id=descriptor.get('id'),
        message=f"Expected '{kind}' to exist but it does not",
        desc=None if descriptor.get('id') else descriptor
      )
  else:
    return Violation(
      severity='error',
      type="Missing top-level property 'kind'",
      id=descriptor.get('id'),
      message=None,
      desc=None if descriptor.get('id') else descriptor
    )


def ensure_single_publisher_definitions():
  pass


def ensure_inherit_id_refs():
  pass


def ensure_kind_refs():
  pass
