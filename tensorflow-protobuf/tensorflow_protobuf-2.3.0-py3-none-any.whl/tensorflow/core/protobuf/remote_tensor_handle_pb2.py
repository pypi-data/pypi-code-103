# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow/core/protobuf/remote_tensor_handle.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from tensorflow.core.framework import tensor_shape_pb2 as tensorflow_dot_core_dot_framework_dot_tensor__shape__pb2
from tensorflow.core.framework import types_pb2 as tensorflow_dot_core_dot_framework_dot_types__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorflow/core/protobuf/remote_tensor_handle.proto',
  package='tensorflow.eager',
  syntax='proto3',
  serialized_options=b'\n\030org.tensorflow.frameworkB\030RemoteTensorHandleProtosP\001ZHgithub.com/tensorflow/tensorflow/tensorflow/go/core/core_protos_go_proto\370\001\001',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n3tensorflow/core/protobuf/remote_tensor_handle.proto\x12\x10tensorflow.eager\x1a,tensorflow/core/framework/tensor_shape.proto\x1a%tensorflow/core/framework/types.proto\"i\n\x15ResourceDtypeAndShape\x12#\n\x05\x64type\x18\x01 \x01(\x0e\x32\x14.tensorflow.DataType\x12+\n\x05shape\x18\x02 \x01(\x0b\x32\x1c.tensorflow.TensorShapeProto\"\xcc\x01\n\x12RemoteTensorHandle\x12\r\n\x05op_id\x18\x01 \x01(\x03\x12\x12\n\noutput_num\x18\x02 \x01(\x05\x12\x0e\n\x06\x64\x65vice\x18\x03 \x01(\t\x12\x11\n\top_device\x18\x04 \x01(\t\x12#\n\x05\x64type\x18\x05 \x01(\x0e\x32\x14.tensorflow.DataType\x12K\n\x1aresource_dtypes_and_shapes\x18\x06 \x03(\x0b\x32\'.tensorflow.eager.ResourceDtypeAndShapeB\x83\x01\n\x18org.tensorflow.frameworkB\x18RemoteTensorHandleProtosP\x01ZHgithub.com/tensorflow/tensorflow/tensorflow/go/core/core_protos_go_proto\xf8\x01\x01\x62\x06proto3'
  ,
  dependencies=[tensorflow_dot_core_dot_framework_dot_tensor__shape__pb2.DESCRIPTOR,tensorflow_dot_core_dot_framework_dot_types__pb2.DESCRIPTOR,])




_RESOURCEDTYPEANDSHAPE = _descriptor.Descriptor(
  name='ResourceDtypeAndShape',
  full_name='tensorflow.eager.ResourceDtypeAndShape',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='dtype', full_name='tensorflow.eager.ResourceDtypeAndShape.dtype', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='shape', full_name='tensorflow.eager.ResourceDtypeAndShape.shape', index=1,
      number=2, type=11, cpp_type=10, label=1,
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
  serialized_start=158,
  serialized_end=263,
)


_REMOTETENSORHANDLE = _descriptor.Descriptor(
  name='RemoteTensorHandle',
  full_name='tensorflow.eager.RemoteTensorHandle',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='op_id', full_name='tensorflow.eager.RemoteTensorHandle.op_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='output_num', full_name='tensorflow.eager.RemoteTensorHandle.output_num', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='device', full_name='tensorflow.eager.RemoteTensorHandle.device', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='op_device', full_name='tensorflow.eager.RemoteTensorHandle.op_device', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='dtype', full_name='tensorflow.eager.RemoteTensorHandle.dtype', index=4,
      number=5, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='resource_dtypes_and_shapes', full_name='tensorflow.eager.RemoteTensorHandle.resource_dtypes_and_shapes', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=266,
  serialized_end=470,
)

_RESOURCEDTYPEANDSHAPE.fields_by_name['dtype'].enum_type = tensorflow_dot_core_dot_framework_dot_types__pb2._DATATYPE
_RESOURCEDTYPEANDSHAPE.fields_by_name['shape'].message_type = tensorflow_dot_core_dot_framework_dot_tensor__shape__pb2._TENSORSHAPEPROTO
_REMOTETENSORHANDLE.fields_by_name['dtype'].enum_type = tensorflow_dot_core_dot_framework_dot_types__pb2._DATATYPE
_REMOTETENSORHANDLE.fields_by_name['resource_dtypes_and_shapes'].message_type = _RESOURCEDTYPEANDSHAPE
DESCRIPTOR.message_types_by_name['ResourceDtypeAndShape'] = _RESOURCEDTYPEANDSHAPE
DESCRIPTOR.message_types_by_name['RemoteTensorHandle'] = _REMOTETENSORHANDLE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ResourceDtypeAndShape = _reflection.GeneratedProtocolMessageType('ResourceDtypeAndShape', (_message.Message,), {
  'DESCRIPTOR' : _RESOURCEDTYPEANDSHAPE,
  '__module__' : 'tensorflow.core.protobuf.remote_tensor_handle_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.eager.ResourceDtypeAndShape)
  })
_sym_db.RegisterMessage(ResourceDtypeAndShape)

RemoteTensorHandle = _reflection.GeneratedProtocolMessageType('RemoteTensorHandle', (_message.Message,), {
  'DESCRIPTOR' : _REMOTETENSORHANDLE,
  '__module__' : 'tensorflow.core.protobuf.remote_tensor_handle_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.eager.RemoteTensorHandle)
  })
_sym_db.RegisterMessage(RemoteTensorHandle)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
