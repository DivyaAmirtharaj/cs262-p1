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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14protos/service.proto\x12\x04grpc\"\x07\n\x05\x45mpty\"8\n\x04User\x12\x0c\n\x04uuid\x18\x01 \x01(\x03\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\"<\n\x04\x43hat\x12\x0f\n\x07send_id\x18\x01 \x01(\x03\x12\x12\n\nreceive_id\x18\x02 \x01(\x03\x12\x0f\n\x07message\x18\x03 \x01(\t\",\n\x07Outcome\x12\x10\n\x08\x65rr_type\x18\x01 \x01(\x03\x12\x0f\n\x07\x65rr_msg\x18\x02 \x01(\t2c\n\x07\x43hatBot\x12-\n\x10server_send_chat\x12\n.grpc.Chat\x1a\r.grpc.Outcome\x12)\n\x0fserver_get_chat\x12\n.grpc.User\x1a\n.grpc.Chatb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _EMPTY._serialized_start=30
  _EMPTY._serialized_end=37
  _USER._serialized_start=39
  _USER._serialized_end=95
  _CHAT._serialized_start=97
  _CHAT._serialized_end=157
  _OUTCOME._serialized_start=159
  _OUTCOME._serialized_end=203
  _CHATBOT._serialized_start=205
  _CHATBOT._serialized_end=304
# @@protoc_insertion_point(module_scope)
