# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow/core/framework/tensor_slice.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorflow/core/framework/tensor_slice.proto',
  package='tensorflow',
  syntax='proto3',
  serialized_options=b'\n\030org.tensorflow.frameworkB\021TensorSliceProtosP\001ZSgithub.com/tensorflow/tensorflow/tensorflow/go/core/framework/tensor_slice_go_proto\370\001\001',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n,tensorflow/core/framework/tensor_slice.proto\x12\ntensorflow\"\x80\x01\n\x10TensorSliceProto\x12\x33\n\x06\x65xtent\x18\x01 \x03(\x0b\x32#.tensorflow.TensorSliceProto.Extent\x1a\x37\n\x06\x45xtent\x12\r\n\x05start\x18\x01 \x01(\x03\x12\x10\n\x06length\x18\x02 \x01(\x03H\x00\x42\x0c\n\nhas_lengthB\x87\x01\n\x18org.tensorflow.frameworkB\x11TensorSliceProtosP\x01ZSgithub.com/tensorflow/tensorflow/tensorflow/go/core/framework/tensor_slice_go_proto\xf8\x01\x01\x62\x06proto3'
)




_TENSORSLICEPROTO_EXTENT = _descriptor.Descriptor(
  name='Extent',
  full_name='tensorflow.TensorSliceProto.Extent',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='start', full_name='tensorflow.TensorSliceProto.Extent.start', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='length', full_name='tensorflow.TensorSliceProto.Extent.length', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
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
    _descriptor.OneofDescriptor(
      name='has_length', full_name='tensorflow.TensorSliceProto.Extent.has_length',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=134,
  serialized_end=189,
)

_TENSORSLICEPROTO = _descriptor.Descriptor(
  name='TensorSliceProto',
  full_name='tensorflow.TensorSliceProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='extent', full_name='tensorflow.TensorSliceProto.extent', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_TENSORSLICEPROTO_EXTENT, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=61,
  serialized_end=189,
)

_TENSORSLICEPROTO_EXTENT.containing_type = _TENSORSLICEPROTO
_TENSORSLICEPROTO_EXTENT.oneofs_by_name['has_length'].fields.append(
  _TENSORSLICEPROTO_EXTENT.fields_by_name['length'])
_TENSORSLICEPROTO_EXTENT.fields_by_name['length'].containing_oneof = _TENSORSLICEPROTO_EXTENT.oneofs_by_name['has_length']
_TENSORSLICEPROTO.fields_by_name['extent'].message_type = _TENSORSLICEPROTO_EXTENT
DESCRIPTOR.message_types_by_name['TensorSliceProto'] = _TENSORSLICEPROTO
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TensorSliceProto = _reflection.GeneratedProtocolMessageType('TensorSliceProto', (_message.Message,), {

  'Extent' : _reflection.GeneratedProtocolMessageType('Extent', (_message.Message,), {
    'DESCRIPTOR' : _TENSORSLICEPROTO_EXTENT,
    '__module__' : 'tensorflow.core.framework.tensor_slice_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.TensorSliceProto.Extent)
    })
  ,
  'DESCRIPTOR' : _TENSORSLICEPROTO,
  '__module__' : 'tensorflow.core.framework.tensor_slice_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.TensorSliceProto)
  })
_sym_db.RegisterMessage(TensorSliceProto)
_sym_db.RegisterMessage(TensorSliceProto.Extent)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
