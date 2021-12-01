from typing import Optional, Dict, List, Union, Any, Tuple

from typing_extensions import TypedDict

Handling = Tuple[bool, Any]

class InjectionsDesc(TypedDict):
  standard: Dict
  inline: Dict


class TemplateArgs(TypedDict, total=False):
  flat_inlines: Dict
  values: Dict


class InputOption(TypedDict, total=False):
  id: str
  title: str


class ActionStatusDict(TypedDict, total=False):
  id: Optional[str]
  title: str
  info: Optional[str]
  status: str
  sub_items: List['ActionStatusDict']
  data: Dict
  error: Dict
  error_id: str
  logs: List[str]


class TimeseriesDataPoint(TypedDict):
  timestamp: str
  value: float


class PortForwardSpec(TypedDict):
  namespace: str
  pod_name: str
  pod_port: int


class EndpointDict(TypedDict):
  url: Optional[str]
  type: Optional[str]


class ReleaseDict(TypedDict):
  id: str
  version: str
  type: str
  ktea_type: Optional[str]
  ktea_uri: Optional[str]
  note: str
  space: Optional[str]


class JobStatusPart(TypedDict):
  name: str
  status: str
  pct: Optional[int]


class JobStatus(TypedDict):
  parts: List[JobStatusPart]
  logs: List[str]


class PredEval(TypedDict, total=False):
  predicate_id: str
  name: str
  met: bool
  reason: Optional[str]
  tone: str


class ExitStatuses(TypedDict, total=False):
  positive: List[PredEval]
  negative: List[PredEval]


class CommitOutcome(TypedDict, total=False):
  status: str
  reason: Optional[str]
  logs: List[str]


class K8sResSig(TypedDict):
  kind: str
  name: str


class K8sResMeta(TypedDict):
  namespace: str
  name: str


class K8sResDict(TypedDict):
  kind: str
  metadata: K8sResMeta


class KteaDict(TypedDict, total=False):
  type: str
  uri: Any
  args: Optional[str]
  version: str


class KamaDict(TypedDict, total=False):
  type: str
  uri: str
  version: str


class KamafileBackup(TypedDict, total=False):
  _id: str
  name: str
  trigger: str
  data: Dict
  timestamp: str


class ActionOutcome(TypedDict):
  cls_name: str
  id: str
  charge: str
  data: Dict


class StepActionKwargs(TypedDict):
  inline_assigns: Dict
  chart_assigns: Dict
  state_assigns: Dict


class KAO(TypedDict):
  """
  'Kubectl Apply Outcome' accronym.
  """
  api_group: Optional[str]
  kind: str
  name: str
  verb: Optional[str]
  error: Optional[str]


class ErrorCapture(TypedDict, total=False):
  vid: str
  event_vid: Optional[str]
  type: str
  reason: str
  fatal: bool
  logs: List[str]
  is_original: bool
  extras: Dict[str, Any]
  synced: bool
  occurred_at: str


class Artifact(TypedDict):
  type: str
  id: str


class UserResQuery(TypedDict, total=False):
  resource_kinds: List[str]
  problem_level: Optional[str]
  col_ids: Optional[List[str]]
  max_cols: Optional[int]


class EventCapture(TypedDict):
  """
  Somewhat awkwardly general struct for an Action execution result.
  Awkward because fields like connected_artifacts only make sense
  if the action was a checkup.
  """
  vid: str
  parent_vid: Optional[str]
  type: str
  name: str
  status: str
  logs: List[str]
  initiator_kind: Optional[str]
  initiator_id: Optional[str]
  connected_artifacts: List[Artifact]
  occurred_at: str


class SnapshotMetric(TypedDict):
  type: str
  data: Union[Dict, List]


class NamespacedSnapshot(TypedDict):
  namespace: str
  resources: List
  metrics: List[SnapshotMetric]


class Snapshot(TypedDict):
  namespaced_snapshots: List[NamespacedSnapshot]


class SimpleSeriesSummary(TypedDict):
  series: List[TimeseriesDataPoint]
  humanized_series: List[Dict]
  direction: str
  good_direction: str
  summary_value: str


class ConcernAttrMeta(TypedDict, total=False):
  label: str
  title: str


ConcernRowAttrs = List[ConcernAttrMeta]


class PodStatusSummary(TypedDict):
  ternary_status: str
  pod_name: str
  phase: str

# class PodStatusesSummary(TypedDict)


KAOs = List[KAO]
KoD = Union[str, dict]
KDLoS = Union[str, dict]


class Reconstructor(TypedDict):
  view_spec_ref: KoD
  view_helper_ref: KoD
  seed: Dict
