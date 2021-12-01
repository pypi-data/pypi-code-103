def default_model_classes():
  from kama_sdk.model.supplier.base.misc_suppliers import FormattedDateSupplier
  from kama_sdk.model.variable.manifest_variable import ManifestVariable
  from kama_sdk.model.input.generic_input import GenericInput
  from kama_sdk.model.supplier.ext.misc.latest_vendor_injection_supplier import LatestVendorInjectionSupplier
  from kama_sdk.model.input.slider_input import SliderInput
  from kama_sdk.model.operation.operation import Operation
  from kama_sdk.model.operation.step import Step
  from kama_sdk.model.operation.field import Field
  from kama_sdk.model.variable.generic_variable import GenericVariable
  from kama_sdk.model.k8s.resource_selector import ResourceSelector
  from kama_sdk.model.action.base.multi_action import MultiAction
  from kama_sdk.model.input.checkboxes_input import CheckboxesInput
  from kama_sdk.model.input.checkboxes_input import CheckboxInput
  from kama_sdk.model.predicate.multi_predicate import MultiPredicate
  from kama_sdk.model.supplier.base.supplier import Supplier
  from kama_sdk.model.supplier.ext.misc.http_data_supplier import HttpDataSupplier
  from kama_sdk.model.supplier.ext.biz.resources_supplier import ResourcesSupplier
  from kama_sdk.model.input.checkboxes_input import SelectInput
  from kama_sdk.model.input.checkboxes_input import LargeSelectInput
  from kama_sdk.model.supplier.ext.misc.random_string_supplier import RandomStringSupplier
  from kama_sdk.model.supplier.ext.biz.config_supplier import ConfigSupplier
  from kama_sdk.model.action.base.action import Action
  from kama_sdk.model.humanizer.quantity_humanizer import QuantityHumanizer
  from kama_sdk.model.humanizer.cores_humanizer import CoresHumanizer
  from kama_sdk.model.humanizer.bytes_humanizer import BytesHumanizer
  from kama_sdk.model.action.ext.manifest.await_kaos_settled_action import AwaitKaosSettledAction
  from kama_sdk.model.action.ext.manifest.await_predicates_settled_action import AwaitPredicatesSettledAction
  from kama_sdk.model.action.ext.manifest.kubectl_apply_action import KubectlApplyAction
  from kama_sdk.model.action.ext.manifest.template_manifest_action import TemplateManifestAction
  from kama_sdk.model.action.ext.misc.run_predicates_action import RunPredicateAction
  from kama_sdk.model.action.ext.misc.run_predicates_action import RunPredicatesAction

  from kama_sdk.model.action.ext.misc.wait_action import WaitAction
  from kama_sdk.model.action.ext.k8s.delete_resources_action import DeleteResourceAction
  from kama_sdk.model.action.ext.k8s.delete_resources_action import DeleteResourcesAction
  from kama_sdk.model.action.ext.manifest.kubectl_dry_run_action import KubectlDryRunAction
  from kama_sdk.model.action.ext.misc.create_backup_action import CreateBackupAction
  from kama_sdk.model.supplier.base.switch import Switch
  from kama_sdk.model.action.ext.update.fetch_latest_injection_action import FetchLatestInjectionsAction
  from kama_sdk.model.predicate.common_predicates import TruePredicate
  from kama_sdk.model.predicate.common_predicates import FalsePredicate
  from kama_sdk.model.predicate.common_predicates import RandomPredicate
  from kama_sdk.model.predicate.predicate import Predicate
  from kama_sdk.model.supplier.base.misc_suppliers import SumSupplier
  from kama_sdk.model.supplier.base.misc_suppliers import MergeSupplier
  from kama_sdk.model.supplier.base.misc_suppliers import ListFlattener
  from kama_sdk.model.supplier.base.misc_suppliers import ListPluck
  from kama_sdk.model.supplier.base.misc_suppliers import IfThenElseSupplier
  from kama_sdk.model.supplier.ext.misc.redactor import Redactor
  from kama_sdk.model.supplier.ext.vis.series_summary_supplier import SeriesSummarySupplier
  from kama_sdk.model.supplier.ext.vis.pod_statuses_supplier import PodStatusSummariesSupplier
  from kama_sdk.model.supplier.base.misc_suppliers import ListFilterSupplier

  from kama_sdk.model.supplier.base.misc_suppliers import UnsetSupplier
  from kama_sdk.model.supplier.ext.misc.port_forward_spec_supplier import PortForwardSpecSupplier
  from kama_sdk.model.supplier.ext.vis.quantity_humanization_supplier import QuantityHumanizationSupplier
  from kama_sdk.model.supplier.ext.vis.percentage_supplier import PercentageSupplier

  from kama_sdk.model.supplier.ext.biz.image_src_supplier import ImageSrcSupplier
  from kama_sdk.model.variable.variable_category import VariableCategory
  from kama_sdk.model.input.checkboxes_input import OnOffInput
  from kama_sdk.model.supplier.ext.biz.multi_kind_resource_selector import MultiKindResourceSelector
  from kama_sdk.model.supplier.ext.misc.fresh_defaults_supplier import FreshDefaultsSupplier
  from kama_sdk.model.supplier.ext.vis.timeseries_aggregation_supplier import TimeseriesAggregationSupplier
  from kama_sdk.model.supplier.ext.misc.vars2attr_adapters import Vars2AttrAdaptersSupplier
  from kama_sdk.model.supplier.base.consts_supplier import Consts
  from kama_sdk.model.predicate.resource_count_predicate import ResourceCountPredicate
  from kama_sdk.model.variable.manifest_variable_dependency import ManifestVariableDependency
  from kama_sdk.model.variable.preset import Preset
  from kama_sdk.model.supplier.ext.biz.config_supplier import MergedVarsSupplier
  from kama_sdk.model.supplier.ext.biz.config_supplier import DefaultVariablesSupplier
  from kama_sdk.model.supplier.ext.misc.pod_shell_exec_supplier import PodShellExecOutputSupplier
  from kama_sdk.model.action.ext.k8s.pod_shell_exec_action import PodShellExecAction
  from kama_sdk.model.supplier.base.misc_suppliers import JoinSupplier
  from kama_sdk.model.supplier.ext.misc.site_access_node import SiteAccessNode
  from kama_sdk.model.supplier.ext.misc.site_access_node import SimpleIngressSiteAccessNode
  from kama_sdk.model.supplier.ext.misc.site_access_node import SimpleServiceSiteAccessNode
  from kama_sdk.model.supplier.ext.misc.site_access_node import BestSiteEndpointSupplier
  from kama_sdk.model.supplier.ext.misc.site_access_node import SiteAccessNodesSerializer
  from kama_sdk.model.error.action_error_remediation_option import ActionErrorRemediationOption
  from kama_sdk.model.supplier.ext.biz.config_supplier import PresetAssignmentsSupplier
  from kama_sdk.model.supplier.base.special_suppliers import DelayedInflateSupplier
  from kama_sdk.model.supplier.base.special_suppliers import SelfSupplier
  from kama_sdk.model.supplier.base.special_suppliers import ParentSupplier
  from kama_sdk.model.predicate.format_predicate import FormatPredicate
  from kama_sdk.model.supplier.ext.biz.config_supplier import NamespaceSupplier
  from kama_sdk.model.action.ext.update.fetch_release_action import FetchReleaseAction
  from kama_sdk.model.action.ext.update.commit_ktea_from_release_action import CommitKteaFromReleaseAction
  from kama_sdk.model.action.ext.manifest.write_manifest_vars_action import WriteManifestVarsAction
  from kama_sdk.model.action.ext.manifest.patch_manifest_vars_action import PatchManifestVarsAction
  from kama_sdk.model.action.ext.manifest.unset_manifest_vars_action import UnsetManifestVarsAction
  from kama_sdk.model.base.model import Model
  from kama_sdk.model.action.base.circuit_breaker import CircuitBreaker
  from kama_sdk.model.action.ext.k8s.patch_resource_action import PatchResourceAction
  from kama_sdk.model.view.view_spec import ViewSpec
  from kama_sdk.model.view.column_spec import ColumnSpec
  from kama_sdk.model.view.grid_view_spec import GridViewSpec
  from kama_sdk.model.view.table_view_spec import TableViewSpec
  from kama_sdk.model.supplier.ext.vis.resource_usage_supplier import ResourceUsageSupplier
  from kama_sdk.model.input.view_spec_select_input import ViewSpecSelectInput
  from kama_sdk.model.k8s.resource_group import ResourceGroup

  from kama_sdk.model.supplier.ext.misc.site_access_node import AccessNodeSerializer
  from kama_sdk.model.view.view_group import ViewGroup
  from kama_sdk.model.supplier.ext.vis.unit_conversion_supplier import UnitConverter
  from kama_sdk.model.k8s.variable_category import ResourceCategory
  return [
    Model,

    Operation,
    AccessNodeSerializer,
    Step,
    Field,

    VariableCategory,
    GenericVariable,
    ManifestVariable,
    ManifestVariableDependency,
    ResourceSelector,
    ResourceGroup,
    MultiKindResourceSelector,
    Preset,

    GenericInput,
    SliderInput,
    SelectInput,
    LargeSelectInput,
    CheckboxesInput,
    CheckboxInput,
    OnOffInput,
    ViewSpecSelectInput,

    Predicate,
    FormatPredicate,
    MultiPredicate,
    TruePredicate,
    FalsePredicate,
    RandomPredicate,
    ActionErrorRemediationOption,
    ResourceCategory,

    Supplier,
    Consts,
    SelfSupplier,
    ParentSupplier,
    DelayedInflateSupplier,
    Vars2AttrAdaptersSupplier,
    FormattedDateSupplier,
    MergedVarsSupplier,
    NamespaceSupplier,
    DefaultVariablesSupplier,
    ResourceCountPredicate,
    Switch,
    UnitConverter,
    PodShellExecOutputSupplier,
    MergeSupplier,
    UnsetSupplier,
    HttpDataSupplier,
    ResourcesSupplier,
    FreshDefaultsSupplier,
    RandomStringSupplier,
    ConfigSupplier,
    SumSupplier,
    LatestVendorInjectionSupplier,
    ListFlattener,
    ListFilterSupplier,
    ListPluck,
    IfThenElseSupplier,
    Redactor,
    ResourceUsageSupplier,

    ImageSrcSupplier,
    QuantityHumanizationSupplier,
    PercentageSupplier,
    JoinSupplier,
    PortForwardSpecSupplier,
    PresetAssignmentsSupplier,
    TimeseriesAggregationSupplier,

    SeriesSummarySupplier,
    PodStatusSummariesSupplier,

    SiteAccessNode,
    SimpleIngressSiteAccessNode,
    SimpleServiceSiteAccessNode,
    BestSiteEndpointSupplier,
    SiteAccessNodesSerializer,

    Action,
    MultiAction,
    CircuitBreaker,
    RunPredicateAction,
    RunPredicatesAction,
    WaitAction,

    FetchLatestInjectionsAction,
    AwaitKaosSettledAction,
    AwaitPredicatesSettledAction,

    DeleteResourceAction,
    PatchResourceAction,
    DeleteResourcesAction,
    KubectlDryRunAction,
    CreateBackupAction,
    PodShellExecAction,

    KubectlApplyAction,
    TemplateManifestAction,
    FetchReleaseAction,
    CommitKteaFromReleaseAction,

    PatchManifestVarsAction,
    WriteManifestVarsAction,
    UnsetManifestVarsAction,

    ViewSpec,
    ViewGroup,
    ColumnSpec,
    GridViewSpec,
    TableViewSpec,

    QuantityHumanizer,
    BytesHumanizer,
    CoresHumanizer
  ]
