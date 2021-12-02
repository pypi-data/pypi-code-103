import time

from .. import CoreService_pb2 as pb
from .. import interactive_console
from ..credentials import CredentialsHelper
from ..data_source_wrappers import SparkDataFrame
from ..entities.feature import Feature
from ..retrieve_holder import RetrieveHolder
from ..schema import Schema
from ..utils import Utils
from .ingest_job import IngestJob
from .user import User


class FeatureSet:
    def __init__(self, stub, feature_set):
        fs = pb.FeatureSet()
        fs.CopyFrom(feature_set)
        self._feature_set = fs
        self._stub = stub

    @property
    def project(self):
        return self._feature_set.project

    @property
    def feature_set_name(self):
        return self._feature_set.feature_set_name

    @property
    def raw_data_location(self):
        return self._feature_set.raw_data_location

    @property
    def version(self):
        return self._feature_set.version

    @property
    def version_change(self):
        return self._feature_set.version_change

    @property
    def time_travel_column(self):
        return self._feature_set.time_travel_column

    @property
    def time_travel_column_format(self):
        return self._feature_set.time_travel_column_format

    @property
    def feature_set_type(self):
        return self._feature_set.feature_set_type

    @feature_set_type.setter
    def feature_set_type(self, value):
        self._feature_set.feature_set_type = value

    @property
    def description(self):
        return self._feature_set.description

    @description.setter
    def description(self, value):
        self._feature_set.description = value

    @property
    def owner(self):
        return User(self._feature_set.owner)

    @owner.setter
    def owner(self, email):
        request = pb.GetUserByMailRequest()
        request.email = email
        response = self._stub.GetUserByMail(request)
        user = response.user
        self._feature_set.owner.id = user.id
        self._feature_set.owner.name = user.name
        self._feature_set.owner.email = user.email

    @property
    def author(self):
        return User(self._feature_set.author)

    @property
    def created_date_time(self):
        return Utils.timestamp_to_string(self._feature_set.created_date_time)

    @property
    def last_update_date_time(self):
        return Utils.timestamp_to_string(self._feature_set.last_update_date_time)

    @property
    def application_name(self):
        return self._feature_set.application_name

    @application_name.setter
    def application_name(self, value):
        self._feature_set.application_name = value

    @property
    def deprecated(self):
        return self._feature_set.deprecated

    @deprecated.setter
    def deprecated(self, value):
        self._feature_set.deprecated = value

    @property
    def deprecated_date(self):
        return Utils.timestamp_to_string(self._feature_set.deprecated_date)

    @property
    def data_source_domains(self):
        return self._feature_set.data_source_domains

    @data_source_domains.setter
    def data_source_domains(self, value):
        if not isinstance(value, list):
            raise ValueError(
                "data_source_domains accepts only list of strings as a value"
            )
        self._feature_set.data_source_domains[:] = value

    @property
    def tags(self):
        return self._feature_set.tags

    @tags.setter
    def tags(self, value):
        if not isinstance(value, list):
            raise ValueError("tags accepts only list of strings as a value")
        self._feature_set.tags[:] = value

    @property
    def process_interval(self):
        return self._feature_set.process_interval

    @process_interval.setter
    def process_interval(self, value):
        self._feature_set.process_interval = value

    @property
    def process_interval_unit(self):
        return self._feature_set.process_interval_unit

    @process_interval_unit.setter
    def process_interval_unit(self, value):
        self._feature_set.process_interval_unit = value

    @property
    def flow(self):
        return self._feature_set.flow

    @flow.setter
    def flow(self, value):
        self._feature_set.flow = value

    @property
    def features(self):
        return {
            feature.name: Feature(feature) for feature in self._feature_set.features
        }

    @property
    def primary_key(self):
        return self._feature_set.primary_key

    @primary_key.setter
    def primary_key(self, value):
        self._feature_set.primary_key = value

    @property
    def secondary_key(self):
        return self._feature_set.secondary_key

    @secondary_key.setter
    def secondary_key(self, value):
        self._feature_set.secondary_key = value

    @property
    def statistics(self):
        return Statistics(self._feature_set)

    @property
    def time_to_live(self):
        return TimeToLive(self._feature_set)

    @property
    def special_data(self):
        return SpecialData(self._feature_set)

    @flow.setter
    def flow(self, value):
        self._feature_set.flow = value

    @property
    def time_travel_scope(self):
        return FeatureSetScope(self._feature_set)

    @property
    def application_id(self):
        return self._feature_set.application_id

    @application_id.setter
    def application_id(self, value):
        self._feature_set.application_id = value

    @property
    def feature_set_state(self):
        return self._feature_set.feature_set_state

    @feature_set_state.setter
    def feature_set_state(self, value):
        self._feature_set.feature_set_state = value

    @property
    def online(self):
        return Online(self._feature_set)

    @property
    def secret(self):
        return self._feature_set.secret

    @secret.setter
    def secret(self, value):
        self._feature_set.secret = value

    def create_new_version(self, schema=None, affected_features=None, reason=""):
        if schema is None and affected_features is None:
            raise ValueError(
                "Schema or affected_features must be defined. Both values are supported as well"
            )
        request = pb.CreateNewFeatureSetVersionRequest()
        request.feature_set.CopyFrom(self._feature_set)
        request.reason = reason
        if schema:
            request.schema.extend(schema.dump())
        else:
            request.schema.extend(self.get_schema().dump())
        if affected_features:
            request.affected_features.extend(affected_features)
        response = self._stub.CreateNewFeatureSetVersion(request)
        return FeatureSet(self._stub, response.feature_set)

    def update_metadata(self):
        request = pb.UpdateFeatureSetMetadataRequest()
        request.feature_set.CopyFrom(self._feature_set)
        response = self._stub.UpdateFeatureSetMetadata(request)
        self._feature_set = response.feature_set
        return self

    def delete(self, wait_for_completion=False):
        request = pb.DeleteFeatureSetRequest()
        request.feature_set.CopyFrom(self._feature_set)
        self._stub.DeleteFeatureSet(request)
        exists_request = pb.FeatureSetExistsRequest()
        exists_request.project_id = self._feature_set.project_id
        exists_request.feature_set_id = self._feature_set.id
        if wait_for_completion:
            while self._stub.FeatureSetExists(exists_request).exists:
                time.sleep(1)
                print(
                    "Waiting for feature set '{}' deletion".format(
                        self._feature_set.feature_set_name
                    )
                )

    def add_owners(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Owner)

    def add_editors(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Editor)

    def add_consumers(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Consumer)

    def add_sensitive_consumers(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.SensitiveConsumer)

    def remove_owners(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Owner)

    def remove_editors(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Editor)

    def remove_consumers(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Consumer)

    def remove_sensitive_consumers(self, user_emails):
        return self._remove_permissions(
            user_emails, pb.PermissionType.SensitiveConsumer
        )

    def get_active_jobs(self, job_type=pb.JobType.Unknown):
        from ..collections.jobs import Jobs  # Lazy import to avoid circular reference

        request = pb.ListJobsRequest(active=True)
        request.feature_set.CopyFrom(self._feature_set)
        request.job_type = job_type
        resp = self._stub.ListJobs(request)
        return [Jobs.create_job(self._stub, job_proto) for job_proto in resp.jobs]

    def _add_permissions(self, user_emails, permission):
        request = pb.FeatureSetPermissionRequest()
        request.feature_set.CopyFrom(self._feature_set)
        request.user_emails.extend(user_emails)
        request.permission = permission
        self._stub.AddFeatureSetPermission(request)
        return self

    def _remove_permissions(self, user_emails, permission):
        request = pb.FeatureSetPermissionRequest()
        request.feature_set.CopyFrom(self._feature_set)
        request.user_emails.extend(user_emails)
        request.permission = permission
        self._stub.RemoveFeatureSetPermission(request)
        return self

    def ingest_async(
        self,
        source,
        new_version_on_schema_change=False,
        start_date_time=None,
        end_date_time=None,
    ):
        from ..data_source_wrappers import get_raw_data_location

        if isinstance(source, SparkDataFrame):
            source._write_to_cache(self._stub)
            data_source = source._get_cache_location()
        else:
            data_source = get_raw_data_location(source)
        request = pb.StartIngestJobRequest()
        request.feature_set.CopyFrom(self._feature_set)
        request.new_version_on_schema_change = new_version_on_schema_change
        request.data_source.CopyFrom(data_source)
        CredentialsHelper.set_credentials(request, data_source)
        if start_date_time is not None:
            request.start_date_time = start_date_time
        if end_date_time is not None:
            request.end_date_time = end_date_time
        job_id = self._stub.StartIngestJob(request)
        return IngestJob(self._stub, job_id)

    @interactive_console.record_stats
    def ingest(
        self,
        source,
        new_version_on_schema_change=False,
        start_date_time=None,
        end_date_time=None,
    ):
        job = self.ingest_async(
            source, new_version_on_schema_change, start_date_time, end_date_time
        )
        while not job.is_done():
            job.show_progress()
            time.sleep(2)
        result = job.get_result()
        self._feature_set = result._get_feature_set()
        return result

    def revert_last_ingest(self):
        request = pb.RevertLastIngestRequest()
        request.feature_set.CopyFrom(self._feature_set)
        response = self._stub.RevertLastIngest(request)
        self._feature_set = response.feature_set
        return self

    def retrieve(self, start_date_time=None, end_date_time=None):
        return RetrieveHolder(
            self._stub, self._feature_set, start_date_time, end_date_time
        )

    def list_versions(self):
        request = pb.ListFeatureSetsVersionRequest()
        request.feature_set.CopyFrom(self._feature_set)
        response = self._stub.ListFeatureSetVersions(request)
        return [VersionDescription(version) for version in response.versions]

    def get_schema(self):
        return Schema.load(self)

    def __repr__(self):
        return Utils.pretty_print_proto(self._feature_set)


class VersionDescription:
    def __init__(self, version_description):
        self._version_description = version_description

    def __repr__(self):
        return Utils.pretty_print_proto(self._version_description)


class TimeToLive:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._ttl = self._feature_set.time_to_live

    @property
    def ttl_offline(self):
        return self._ttl.ttl_offline

    @ttl_offline.setter
    def ttl_offline(self, value):
        self._ttl.ttl_offline = value

    @property
    def ttl_offline_interval(self):
        return self._ttl.ttl_offline_interval

    @ttl_offline_interval.setter
    def ttl_offline_interval(self, value):
        self._ttl.ttl_offline_interval = value

    @property
    def ttl_online(self):
        return self._ttl.ttl_online

    @ttl_online.setter
    def ttl_online(self, value):
        self._ttl.ttl_online = value

    @property
    def ttl_online_interval(self):
        return self._ttl.ttl_online_interval

    @ttl_online_interval.setter
    def ttl_online_interval(self, value):
        self._ttl.ttl_online_interval = value

    def __repr__(self):
        return Utils.pretty_print_proto(self._ttl)


class FeatureSetScope:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._scope = self._feature_set.time_travel_scope

    @property
    def start_date_time(self):
        return Utils.timestamp_to_string(self._scope.start_date_time)

    @property
    def end_date_time(self):
        return Utils.timestamp_to_string(self._scope.end_date_time)

    def __repr__(self):
        return Utils.pretty_print_proto(self._scope)


class SpecialData:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._special_data = self._feature_set.special_data

    @property
    def spi(self):
        return self._special_data.spi

    @spi.setter
    def spi(self, value):
        self._special_data.spi = value

    @property
    def pci(self):
        return self._special_data.pci

    @pci.setter
    def pci(self, value):
        self._special_data.pci = value

    @property
    def rpi(self):
        return self._special_data.rpi

    @rpi.setter
    def rpi(self, value):
        self._special_data.rpi = value

    @property
    def demographic(self):
        return self._special_data.demographic

    @demographic.setter
    def demographic(self, value):
        self._special_data.demographic = value

    @property
    def legal(self):
        return Legal(self._feature_set)

    def __repr__(self):
        return Utils.pretty_print_proto(self._special_data)


class Statistics:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._statistics = self._feature_set.statistics

    @property
    def data_latency(self):
        return self._statistics.data_latency

    def __repr__(self):
        return Utils.pretty_print_proto(self._statistics)


class Legal:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._legal = self._feature_set.special_data.legal

    @property
    def approved(self):
        return self._legal.approved

    @approved.setter
    def approved(self, value):
        self._legal.approved = value

    @property
    def approved_date(self):
        return self._legal.approved_date

    @approved_date.setter
    def approved_date(self, value):
        self._legal.approved_date = value

    @property
    def notes(self):
        return self._legal.notes

    @notes.setter
    def notes(self, value):
        self._legal.notes = value

    def __repr__(self):
        return Utils.pretty_print_proto(self._legal)


class Online:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._online = self._feature_set.online

    @property
    def online_namespace(self):
        return self._online.online_namespace

    @property
    def connection_type(self):
        return self._online.connection_type

    @property
    def topic(self):
        return self._online.topic

    def __repr__(self):
        return Utils.pretty_print_proto(self._online)
