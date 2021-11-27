# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: github.com/metaprov/modelaapi/services/sqlquery/v1/sqlquery.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1 import generated_pb2 as github_dot_com_dot_metaprov_dot_modelaapi_dot_pkg_dot_apis_dot_data_dot_v1alpha1_dot_generated__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='github.com/metaprov/modelaapi/services/sqlquery/v1/sqlquery.proto',
  package='github.com.metaprov.modelaapi.services.sqlquery.v1',
  syntax='proto3',
  serialized_options=b'Z2github.com/metaprov/modelaapi/services/sqlquery/v1',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\nAgithub.com/metaprov/modelaapi/services/sqlquery/v1/sqlquery.proto\x12\x32github.com.metaprov.modelaapi.services.sqlquery.v1\x1a\x1cgoogle/api/annotations.proto\x1a\x44github.com/metaprov/modelaapi/pkg/apis/data/v1alpha1/generated.proto\"\xcc\x01\n\x14ListSqlQuerysRequest\x12\x11\n\tnamespace\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x64\n\x06labels\x18\x03 \x03(\x0b\x32T.github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest.LabelsEntry\x1a-\n\x0bLabelsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"j\n\x15ListSqlQuerysResponse\x12Q\n\x05items\x18\x01 \x01(\x0b\x32\x42.github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.SqlQueryList\"\x18\n\x16\x43reateSqlQueryResponse\"e\n\x15\x43reateSqlQueryRequest\x12L\n\x04item\x18\x01 \x01(\x0b\x32>.github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.SqlQuery\"e\n\x15UpdateSqlQueryRequest\x12L\n\x04item\x18\x01 \x01(\x0b\x32>.github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.SqlQuery\"\x18\n\x16UpdateSqlQueryResponse\"5\n\x12GetSqlQueryRequest\x12\x11\n\tnamespace\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\"q\n\x13GetSqlQueryResponse\x12L\n\x04item\x18\x01 \x01(\x0b\x32>.github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.SqlQuery\x12\x0c\n\x04yaml\x18\x02 \x01(\t\"8\n\x15\x44\x65leteSqlQueryRequest\x12\x11\n\tnamespace\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\"\x18\n\x16\x44\x65leteSqlQueryResponse\"b\n\x12RunSqlQueryRequest\x12L\n\x04item\x18\x01 \x01(\x0b\x32>.github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.SqlQuery\"\x15\n\x13RunSqlQueryResponse2\xbe\t\n\x0fSqlQueryService\x12\xbc\x01\n\rListSqlQuerys\x12H.github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest\x1aI.github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysResponse\"\x16\x82\xd3\xe4\x93\x02\x10\x12\x0e/v1/sqlqueries\x12\xc1\x01\n\x0e\x43reateSqlQuery\x12I.github.com.metaprov.modelaapi.services.sqlquery.v1.CreateSqlQueryRequest\x1aJ.github.com.metaprov.modelaapi.services.sqlquery.v1.CreateSqlQueryResponse\"\x18\x82\xd3\xe4\x93\x02\x12\"\r/v1/sqlquerys:\x01*\x12\xbd\x01\n\x0bGetSqlQuery\x12\x46.github.com.metaprov.modelaapi.services.sqlquery.v1.GetSqlQueryRequest\x1aG.github.com.metaprov.modelaapi.services.sqlquery.v1.GetSqlQueryResponse\"\x1d\x82\xd3\xe4\x93\x02\x17\x12\x15/v1/sqlqueries/{name}\x12\xda\x01\n\x0eUpdateSqlQuery\x12I.github.com.metaprov.modelaapi.services.sqlquery.v1.UpdateSqlQueryRequest\x1aJ.github.com.metaprov.modelaapi.services.sqlquery.v1.UpdateSqlQueryResponse\"1\x82\xd3\xe4\x93\x02+\x1a&/v1/sqlquerys/{sqlquery.metadata.name}:\x01*\x12\xc6\x01\n\x0e\x44\x65leteSqlQuery\x12I.github.com.metaprov.modelaapi.services.sqlquery.v1.DeleteSqlQueryRequest\x1aJ.github.com.metaprov.modelaapi.services.sqlquery.v1.DeleteSqlQueryResponse\"\x1d\x82\xd3\xe4\x93\x02\x17*\x15/v1/sqlqueries/{name}\x12\xc1\x01\n\x0bRunSqlQuery\x12\x46.github.com.metaprov.modelaapi.services.sqlquery.v1.RunSqlQueryRequest\x1aG.github.com.metaprov.modelaapi.services.sqlquery.v1.RunSqlQueryResponse\"!\x82\xd3\xe4\x93\x02\x1b\"\x19/v1/sqlqueries/{name}:runB4Z2github.com/metaprov/modelaapi/services/sqlquery/v1b\x06proto3'
  ,
  dependencies=[google_dot_api_dot_annotations__pb2.DESCRIPTOR,github_dot_com_dot_metaprov_dot_modelaapi_dot_pkg_dot_apis_dot_data_dot_v1alpha1_dot_generated__pb2.DESCRIPTOR,])




_LISTSQLQUERYSREQUEST_LABELSENTRY = _descriptor.Descriptor(
  name='LabelsEntry',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest.LabelsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest.LabelsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest.LabelsEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=381,
  serialized_end=426,
)

_LISTSQLQUERYSREQUEST = _descriptor.Descriptor(
  name='ListSqlQuerysRequest',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='namespace', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest.namespace', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='name', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='labels', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest.labels', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_LISTSQLQUERYSREQUEST_LABELSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=222,
  serialized_end=426,
)


_LISTSQLQUERYSRESPONSE = _descriptor.Descriptor(
  name='ListSqlQuerysResponse',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='items', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysResponse.items', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=428,
  serialized_end=534,
)


_CREATESQLQUERYRESPONSE = _descriptor.Descriptor(
  name='CreateSqlQueryResponse',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.CreateSqlQueryResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=536,
  serialized_end=560,
)


_CREATESQLQUERYREQUEST = _descriptor.Descriptor(
  name='CreateSqlQueryRequest',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.CreateSqlQueryRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='item', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.CreateSqlQueryRequest.item', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=562,
  serialized_end=663,
)


_UPDATESQLQUERYREQUEST = _descriptor.Descriptor(
  name='UpdateSqlQueryRequest',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.UpdateSqlQueryRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='item', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.UpdateSqlQueryRequest.item', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=665,
  serialized_end=766,
)


_UPDATESQLQUERYRESPONSE = _descriptor.Descriptor(
  name='UpdateSqlQueryResponse',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.UpdateSqlQueryResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=768,
  serialized_end=792,
)


_GETSQLQUERYREQUEST = _descriptor.Descriptor(
  name='GetSqlQueryRequest',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.GetSqlQueryRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='namespace', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.GetSqlQueryRequest.namespace', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='name', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.GetSqlQueryRequest.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=794,
  serialized_end=847,
)


_GETSQLQUERYRESPONSE = _descriptor.Descriptor(
  name='GetSqlQueryResponse',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.GetSqlQueryResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='item', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.GetSqlQueryResponse.item', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='yaml', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.GetSqlQueryResponse.yaml', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=849,
  serialized_end=962,
)


_DELETESQLQUERYREQUEST = _descriptor.Descriptor(
  name='DeleteSqlQueryRequest',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.DeleteSqlQueryRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='namespace', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.DeleteSqlQueryRequest.namespace', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='name', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.DeleteSqlQueryRequest.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=964,
  serialized_end=1020,
)


_DELETESQLQUERYRESPONSE = _descriptor.Descriptor(
  name='DeleteSqlQueryResponse',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.DeleteSqlQueryResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1022,
  serialized_end=1046,
)


_RUNSQLQUERYREQUEST = _descriptor.Descriptor(
  name='RunSqlQueryRequest',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.RunSqlQueryRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='item', full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.RunSqlQueryRequest.item', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1048,
  serialized_end=1146,
)


_RUNSQLQUERYRESPONSE = _descriptor.Descriptor(
  name='RunSqlQueryResponse',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.RunSqlQueryResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1148,
  serialized_end=1169,
)

_LISTSQLQUERYSREQUEST_LABELSENTRY.containing_type = _LISTSQLQUERYSREQUEST
_LISTSQLQUERYSREQUEST.fields_by_name['labels'].message_type = _LISTSQLQUERYSREQUEST_LABELSENTRY
_LISTSQLQUERYSRESPONSE.fields_by_name['items'].message_type = github_dot_com_dot_metaprov_dot_modelaapi_dot_pkg_dot_apis_dot_data_dot_v1alpha1_dot_generated__pb2._SQLQUERYLIST
_CREATESQLQUERYREQUEST.fields_by_name['item'].message_type = github_dot_com_dot_metaprov_dot_modelaapi_dot_pkg_dot_apis_dot_data_dot_v1alpha1_dot_generated__pb2._SQLQUERY
_UPDATESQLQUERYREQUEST.fields_by_name['item'].message_type = github_dot_com_dot_metaprov_dot_modelaapi_dot_pkg_dot_apis_dot_data_dot_v1alpha1_dot_generated__pb2._SQLQUERY
_GETSQLQUERYRESPONSE.fields_by_name['item'].message_type = github_dot_com_dot_metaprov_dot_modelaapi_dot_pkg_dot_apis_dot_data_dot_v1alpha1_dot_generated__pb2._SQLQUERY
_RUNSQLQUERYREQUEST.fields_by_name['item'].message_type = github_dot_com_dot_metaprov_dot_modelaapi_dot_pkg_dot_apis_dot_data_dot_v1alpha1_dot_generated__pb2._SQLQUERY
DESCRIPTOR.message_types_by_name['ListSqlQuerysRequest'] = _LISTSQLQUERYSREQUEST
DESCRIPTOR.message_types_by_name['ListSqlQuerysResponse'] = _LISTSQLQUERYSRESPONSE
DESCRIPTOR.message_types_by_name['CreateSqlQueryResponse'] = _CREATESQLQUERYRESPONSE
DESCRIPTOR.message_types_by_name['CreateSqlQueryRequest'] = _CREATESQLQUERYREQUEST
DESCRIPTOR.message_types_by_name['UpdateSqlQueryRequest'] = _UPDATESQLQUERYREQUEST
DESCRIPTOR.message_types_by_name['UpdateSqlQueryResponse'] = _UPDATESQLQUERYRESPONSE
DESCRIPTOR.message_types_by_name['GetSqlQueryRequest'] = _GETSQLQUERYREQUEST
DESCRIPTOR.message_types_by_name['GetSqlQueryResponse'] = _GETSQLQUERYRESPONSE
DESCRIPTOR.message_types_by_name['DeleteSqlQueryRequest'] = _DELETESQLQUERYREQUEST
DESCRIPTOR.message_types_by_name['DeleteSqlQueryResponse'] = _DELETESQLQUERYRESPONSE
DESCRIPTOR.message_types_by_name['RunSqlQueryRequest'] = _RUNSQLQUERYREQUEST
DESCRIPTOR.message_types_by_name['RunSqlQueryResponse'] = _RUNSQLQUERYRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ListSqlQuerysRequest = _reflection.GeneratedProtocolMessageType('ListSqlQuerysRequest', (_message.Message,), {

  'LabelsEntry' : _reflection.GeneratedProtocolMessageType('LabelsEntry', (_message.Message,), {
    'DESCRIPTOR' : _LISTSQLQUERYSREQUEST_LABELSENTRY,
    '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
    # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest.LabelsEntry)
    })
  ,
  'DESCRIPTOR' : _LISTSQLQUERYSREQUEST,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysRequest)
  })
_sym_db.RegisterMessage(ListSqlQuerysRequest)
_sym_db.RegisterMessage(ListSqlQuerysRequest.LabelsEntry)

ListSqlQuerysResponse = _reflection.GeneratedProtocolMessageType('ListSqlQuerysResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTSQLQUERYSRESPONSE,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.ListSqlQuerysResponse)
  })
_sym_db.RegisterMessage(ListSqlQuerysResponse)

CreateSqlQueryResponse = _reflection.GeneratedProtocolMessageType('CreateSqlQueryResponse', (_message.Message,), {
  'DESCRIPTOR' : _CREATESQLQUERYRESPONSE,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.CreateSqlQueryResponse)
  })
_sym_db.RegisterMessage(CreateSqlQueryResponse)

CreateSqlQueryRequest = _reflection.GeneratedProtocolMessageType('CreateSqlQueryRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATESQLQUERYREQUEST,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.CreateSqlQueryRequest)
  })
_sym_db.RegisterMessage(CreateSqlQueryRequest)

UpdateSqlQueryRequest = _reflection.GeneratedProtocolMessageType('UpdateSqlQueryRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPDATESQLQUERYREQUEST,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.UpdateSqlQueryRequest)
  })
_sym_db.RegisterMessage(UpdateSqlQueryRequest)

UpdateSqlQueryResponse = _reflection.GeneratedProtocolMessageType('UpdateSqlQueryResponse', (_message.Message,), {
  'DESCRIPTOR' : _UPDATESQLQUERYRESPONSE,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.UpdateSqlQueryResponse)
  })
_sym_db.RegisterMessage(UpdateSqlQueryResponse)

GetSqlQueryRequest = _reflection.GeneratedProtocolMessageType('GetSqlQueryRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETSQLQUERYREQUEST,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.GetSqlQueryRequest)
  })
_sym_db.RegisterMessage(GetSqlQueryRequest)

GetSqlQueryResponse = _reflection.GeneratedProtocolMessageType('GetSqlQueryResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETSQLQUERYRESPONSE,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.GetSqlQueryResponse)
  })
_sym_db.RegisterMessage(GetSqlQueryResponse)

DeleteSqlQueryRequest = _reflection.GeneratedProtocolMessageType('DeleteSqlQueryRequest', (_message.Message,), {
  'DESCRIPTOR' : _DELETESQLQUERYREQUEST,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.DeleteSqlQueryRequest)
  })
_sym_db.RegisterMessage(DeleteSqlQueryRequest)

DeleteSqlQueryResponse = _reflection.GeneratedProtocolMessageType('DeleteSqlQueryResponse', (_message.Message,), {
  'DESCRIPTOR' : _DELETESQLQUERYRESPONSE,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.DeleteSqlQueryResponse)
  })
_sym_db.RegisterMessage(DeleteSqlQueryResponse)

RunSqlQueryRequest = _reflection.GeneratedProtocolMessageType('RunSqlQueryRequest', (_message.Message,), {
  'DESCRIPTOR' : _RUNSQLQUERYREQUEST,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.RunSqlQueryRequest)
  })
_sym_db.RegisterMessage(RunSqlQueryRequest)

RunSqlQueryResponse = _reflection.GeneratedProtocolMessageType('RunSqlQueryResponse', (_message.Message,), {
  'DESCRIPTOR' : _RUNSQLQUERYRESPONSE,
  '__module__' : 'github.com.metaprov.modelaapi.services.sqlquery.v1.sqlquery_pb2'
  # @@protoc_insertion_point(class_scope:github.com.metaprov.modelaapi.services.sqlquery.v1.RunSqlQueryResponse)
  })
_sym_db.RegisterMessage(RunSqlQueryResponse)


DESCRIPTOR._options = None
_LISTSQLQUERYSREQUEST_LABELSENTRY._options = None

_SQLQUERYSERVICE = _descriptor.ServiceDescriptor(
  name='SqlQueryService',
  full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.SqlQueryService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=1172,
  serialized_end=2386,
  methods=[
  _descriptor.MethodDescriptor(
    name='ListSqlQuerys',
    full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.SqlQueryService.ListSqlQuerys',
    index=0,
    containing_service=None,
    input_type=_LISTSQLQUERYSREQUEST,
    output_type=_LISTSQLQUERYSRESPONSE,
    serialized_options=b'\202\323\344\223\002\020\022\016/v1/sqlqueries',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='CreateSqlQuery',
    full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.SqlQueryService.CreateSqlQuery',
    index=1,
    containing_service=None,
    input_type=_CREATESQLQUERYREQUEST,
    output_type=_CREATESQLQUERYRESPONSE,
    serialized_options=b'\202\323\344\223\002\022\"\r/v1/sqlquerys:\001*',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetSqlQuery',
    full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.SqlQueryService.GetSqlQuery',
    index=2,
    containing_service=None,
    input_type=_GETSQLQUERYREQUEST,
    output_type=_GETSQLQUERYRESPONSE,
    serialized_options=b'\202\323\344\223\002\027\022\025/v1/sqlqueries/{name}',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateSqlQuery',
    full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.SqlQueryService.UpdateSqlQuery',
    index=3,
    containing_service=None,
    input_type=_UPDATESQLQUERYREQUEST,
    output_type=_UPDATESQLQUERYRESPONSE,
    serialized_options=b'\202\323\344\223\002+\032&/v1/sqlquerys/{sqlquery.metadata.name}:\001*',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='DeleteSqlQuery',
    full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.SqlQueryService.DeleteSqlQuery',
    index=4,
    containing_service=None,
    input_type=_DELETESQLQUERYREQUEST,
    output_type=_DELETESQLQUERYRESPONSE,
    serialized_options=b'\202\323\344\223\002\027*\025/v1/sqlqueries/{name}',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='RunSqlQuery',
    full_name='github.com.metaprov.modelaapi.services.sqlquery.v1.SqlQueryService.RunSqlQuery',
    index=5,
    containing_service=None,
    input_type=_RUNSQLQUERYREQUEST,
    output_type=_RUNSQLQUERYRESPONSE,
    serialized_options=b'\202\323\344\223\002\033\"\031/v1/sqlqueries/{name}:run',
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_SQLQUERYSERVICE)

DESCRIPTOR.services_by_name['SqlQueryService'] = _SQLQUERYSERVICE

# @@protoc_insertion_point(module_scope)
