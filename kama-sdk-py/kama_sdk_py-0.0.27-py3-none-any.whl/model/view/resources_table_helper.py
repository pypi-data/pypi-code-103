from typing import List, Dict

from k8kat.res.base.kat_res import KatRes

from kama_sdk.core.core.types import UserResQuery
from kama_sdk.model.k8s.resource_selector import RES_KIND_KEY, ResourceSelector
from kama_sdk.model.view.column_spec import ColumnSpec


def kinds2sorted_col_specs(res_kinds: List[str]) -> List[ColumnSpec]:
  models = ColumnSpec.inflate_all()
  matching_cols = [c for c in models if c.matches_resource_kinds(res_kinds)]
  return sorted(matching_cols, key=ColumnSpec.get_desired_index)


def find_weakest_col_spec(col_specs: List[ColumnSpec]) -> int:
  lowest_weight, victim_index = 1_000, 0
  for i, col_spec in enumerate(col_specs):
    if col_spec.get_desired_weight() <= lowest_weight:
      lowest_weight = col_spec.get_desired_weight()
      victim_index = i
  return victim_index


def prune_cols(query: UserResQuery, col_specs: List[ColumnSpec]) -> List[ColumnSpec]:
  max_num = query.get('max_cols') or DEFAULT_MAX_COLS
  while len(col_specs) > max_num:
    victim_index = find_weakest_col_spec(col_specs)
    col_specs.pop(victim_index)
  return col_specs


def get_column_ids(query: UserResQuery) -> List[str]:
  if explicit := query.get('col_ids'):
    final_col_ids = explicit
  else:
    all_cols = kinds2sorted_col_specs(query['resource_kinds'])
    pruned_cols = prune_cols(query, all_cols)
    final_col_ids = [col.get_id() for col in pruned_cols]
  return final_col_ids


def query_resources(query: UserResQuery) -> List[KatRes]:
  result = []
  for kind in query['resource_kinds']:
    selector = ResourceSelector({RES_KIND_KEY: kind})
    all_in_kind = selector.query_cluster()
    result.extend(all_in_kind)
  return result


def compute_frames(query: UserResQuery, kat_reses: List[KatRes]) -> List[Dict]:
  col_ids = get_column_ids(query)
  frames = []
  for kat_res in kat_reses:
    frame = {}
    for col_id in col_ids:
      col_spec = ColumnSpec.inflate(col_id)
      view_spec_model = col_spec.get_primed_view_spec(kat_res)
      resolved_view_spec = view_spec_model.compute_spec()
      frame[col_id] = resolved_view_spec
    frames.append(frame)
  return frames


RES_LABEL = "resource_kinds"
DEFAULT_MAX_COLS = 5
