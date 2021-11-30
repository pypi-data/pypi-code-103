from typing import Dict, List, Optional

from kama_sdk.core.core import config_man as cman_module
from kama_sdk.core.core.config_man import USER_VARS_LVL, VNDR_INJ_VARS_LVL, DEF_VARS_LVL, config_man, \
  MANIFEST_VAR_LEVEL_KEYS
from kama_sdk.model.input import input_serializer
from kama_sdk.model.variable.manifest_variable import ManifestVariable
from kama_sdk.model.variable.manifest_variable_dependency import ManifestVariableDependencyInstance, \
  ManifestVariableDependency
from kama_sdk.model.variable.manifest_variable_dependency_instance import EFFECT_PREVENTS_READ
from kama_sdk.model.variable.variable_category import VariableCategory
from kama_sdk.serializers import common_serializers
from kama_sdk.utils import utils

MVDI = ManifestVariableDependencyInstance
MVD = ManifestVariableDependency


def serialize_category(category: VariableCategory) -> Optional[Dict]:
  if category:
    return {
      **common_serializers.ser_meta(category),
      'graphic_type': category.get_graphic_type(),
      'graphic': category.get_graphic()
    }
  else:
    return None


def standard(variable: ManifestVariable, **kwargs):
  return dict(
    id=variable.get_id(),
    flat_key=variable.get_flat_key(),
    title=variable.get_title(),
    is_user_writable=variable.is_user_writable(),
    info=variable.get_info(),
    category=serialize_category(variable.get_category()),
    value=variable.get_current_value(**kwargs),
    assignments=ser_assignments(variable),
    is_valid=variable.is_currently_valid(),
    config_space=variable.get_config_space()
  )


def ser_assignments(variable: ManifestVariable) -> List[Dict]:

  def level2bundle(index: int) -> Dict:
    level_name = MANIFEST_VAR_LEVEL_KEYS[index]
    source: Dict = config_man.read_typed_entry(level_name, **{
      cman_module.SPACE_KW: variable.get_config_space()
    })

    flat_source = utils.deep2flat(source)
    is_present = variable.get_flat_key() in flat_source.keys()
    value = flat_source.get(variable.get_flat_key())

    return {
      'level_name': level_name,
      'level_number': index,
      'value': value,
      'is_present': is_present
    }

  return list(map(level2bundle, range(len(MANIFEST_VAR_LEVEL_KEYS))))


def ser_dep_inst(dep_inst: MVDI, other_var: ManifestVariable) -> Dict:
  info = dep_inst.get_title() or dep_inst.get_info()
  return {
    'title': info,
    'info': info,
    'other_variable': {
      'id': other_var.get_id(),
      'space': other_var.get_space_id()
    },
    'effect': dep_inst.get_effect(),
    'is_active': dep_inst.is_active()
  }


def ser_dependency(direction: str, dep: MVD) -> List[Dict]:
  instances = dep.generate_synthetic_child_instances()

  results = []

  for instance in instances:
    if direction == 'in':
      other_var = instance.get_from_variable()
    else:
      other_var = instance.get_to_variable()

    results.append(ser_dep_inst(instance, other_var))

  is_duplicate = lambda b: utils.deep_get(b, 'other_variable.id')
  return list(utils.unique(results, predicate=is_duplicate))


def ser_dependencies(direction, dependencies: List[MVD]) -> List[Dict]:
  nested = [ser_dependency(direction, d) for d in dependencies]
  return utils.flatten(nested)


def has_active_read_prevention(dicts: List[Dict]):
  def predicate(ser: Dict) -> bool:
    is_read_prevent = ser.get('effect') == EFFECT_PREVENTS_READ
    is_active = ser.get('is_active')
    return is_read_prevent and is_active
  return next(filter(predicate, dicts), None) is not None


def ser_predicates(variable: ManifestVariable) -> Dict:
  predicates = variable.get_health_predicates()
  serialized = list(map(common_serializers.ser_meta, predicates))
  return {'health_predicates': serialized}


def full(variable: ManifestVariable) -> Dict:
  out_deps = ManifestVariableDependency.list_for_variable(variable, 'out')
  in_deps = ManifestVariableDependency.list_for_variable(variable, 'in')

  serd_out_deps = ser_dependencies('out', out_deps)
  serd_in_deps = ser_dependencies('in', in_deps)

  return {
    **standard(variable),
    **input_serializer.in_variable(variable.get_input_model()),
    **ser_predicates(variable),
    'incoming_dependencies': serd_in_deps,
    'outgoing_dependencies': serd_out_deps,
    'is_preventing_read': has_active_read_prevention(serd_out_deps),
    'is_read_blocked': has_active_read_prevention(serd_in_deps)
  }
