# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14protos/service.proto\x12\x04grpc\"\x07\n\x05\x45mpty\"8\n\x04User\x12\x0c\n\x04uuid\x18\x01 \x01(\x03\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\"G\n\x04\x43hat\x12\x11\n\tfrom_uuid\x18\x01 \x01(\x03\x12\r\n\x05to_id\x18\x02 \x01(\x03\x12\x10\n\x08username\x18\x03 \x01(\t\x12\x0b\n\x03msg\x18\x04 \x01(\t\")\n\x08Response\x12\x10\n\x08\x65rr_type\x18\x01 \x01(\x03\x12\x0b\n\x03msg\x18\x02 \x01(\t2\\\n\nChatServer\x12(\n\x0b\x63hat_stream\x12\x0b.grpc.Empty\x1a\n.grpc.Chat0\x01\x12$\n\tsend_chat\x12\n.grpc.Chat\x1a\x0b.grpc.Emptyb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _EMPTY._serialized_start=30
  _EMPTY._serialized_end=37
  _USER._serialized_start=39
  _USER._serialized_end=95
  _CHAT._serialized_start=97
  _CHAT._serialized_end=168
  _RESPONSE._serialized_start=170
  _RESPONSE._serialized_end=211
  _CHATSERVER._serialized_start=213
  _CHATSERVER._serialized_end=305
# @@protoc_insertion_point(module_scope)
