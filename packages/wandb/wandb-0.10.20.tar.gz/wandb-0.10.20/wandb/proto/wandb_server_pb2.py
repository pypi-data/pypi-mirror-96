# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: wandb/proto/wandb_server.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from wandb.proto import wandb_internal_pb2 as wandb_dot_proto_dot_wandb__internal__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='wandb/proto/wandb_server.proto',
  package='wandb_internal',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x1ewandb/proto/wandb_server.proto\x12\x0ewandb_internal\x1a wandb/proto/wandb_internal.proto\"\x17\n\x15ServerShutdownRequest\"\x16\n\x14ServerShutdownResult\"\x15\n\x13ServerStatusRequest\"\x14\n\x12ServerStatusResult2\x85\x05\n\x0fInternalService\x12I\n\tRunUpdate\x12\x19.wandb_internal.RunRecord\x1a\x1f.wandb_internal.RunUpdateResult\"\x00\x12I\n\x07RunExit\x12\x1d.wandb_internal.RunExitRecord\x1a\x1d.wandb_internal.RunExitResult\"\x00\x12\x45\n\x03Log\x12\x1d.wandb_internal.HistoryRecord\x1a\x1d.wandb_internal.HistoryResult\"\x00\x12I\n\x07Summary\x12\x1d.wandb_internal.SummaryRecord\x1a\x1d.wandb_internal.SummaryResult\"\x00\x12\x46\n\x06\x43onfig\x12\x1c.wandb_internal.ConfigRecord\x1a\x1c.wandb_internal.ConfigResult\"\x00\x12\x46\n\x06Output\x12\x1c.wandb_internal.OutputRecord\x1a\x1c.wandb_internal.OutputResult\"\x00\x12_\n\x0eServerShutdown\x12%.wandb_internal.ServerShutdownRequest\x1a$.wandb_internal.ServerShutdownResult\"\x00\x12Y\n\x0cServerStatus\x12#.wandb_internal.ServerStatusRequest\x1a\".wandb_internal.ServerStatusResult\"\x00\x62\x06proto3'
  ,
  dependencies=[wandb_dot_proto_dot_wandb__internal__pb2.DESCRIPTOR,])




_SERVERSHUTDOWNREQUEST = _descriptor.Descriptor(
  name='ServerShutdownRequest',
  full_name='wandb_internal.ServerShutdownRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
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
  serialized_start=84,
  serialized_end=107,
)


_SERVERSHUTDOWNRESULT = _descriptor.Descriptor(
  name='ServerShutdownResult',
  full_name='wandb_internal.ServerShutdownResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
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
  serialized_start=109,
  serialized_end=131,
)


_SERVERSTATUSREQUEST = _descriptor.Descriptor(
  name='ServerStatusRequest',
  full_name='wandb_internal.ServerStatusRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
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
  serialized_start=133,
  serialized_end=154,
)


_SERVERSTATUSRESULT = _descriptor.Descriptor(
  name='ServerStatusResult',
  full_name='wandb_internal.ServerStatusResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
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
  serialized_start=156,
  serialized_end=176,
)

DESCRIPTOR.message_types_by_name['ServerShutdownRequest'] = _SERVERSHUTDOWNREQUEST
DESCRIPTOR.message_types_by_name['ServerShutdownResult'] = _SERVERSHUTDOWNRESULT
DESCRIPTOR.message_types_by_name['ServerStatusRequest'] = _SERVERSTATUSREQUEST
DESCRIPTOR.message_types_by_name['ServerStatusResult'] = _SERVERSTATUSRESULT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ServerShutdownRequest = _reflection.GeneratedProtocolMessageType('ServerShutdownRequest', (_message.Message,), {
  'DESCRIPTOR' : _SERVERSHUTDOWNREQUEST,
  '__module__' : 'wandb.proto.wandb_server_pb2'
  # @@protoc_insertion_point(class_scope:wandb_internal.ServerShutdownRequest)
  })
_sym_db.RegisterMessage(ServerShutdownRequest)

ServerShutdownResult = _reflection.GeneratedProtocolMessageType('ServerShutdownResult', (_message.Message,), {
  'DESCRIPTOR' : _SERVERSHUTDOWNRESULT,
  '__module__' : 'wandb.proto.wandb_server_pb2'
  # @@protoc_insertion_point(class_scope:wandb_internal.ServerShutdownResult)
  })
_sym_db.RegisterMessage(ServerShutdownResult)

ServerStatusRequest = _reflection.GeneratedProtocolMessageType('ServerStatusRequest', (_message.Message,), {
  'DESCRIPTOR' : _SERVERSTATUSREQUEST,
  '__module__' : 'wandb.proto.wandb_server_pb2'
  # @@protoc_insertion_point(class_scope:wandb_internal.ServerStatusRequest)
  })
_sym_db.RegisterMessage(ServerStatusRequest)

ServerStatusResult = _reflection.GeneratedProtocolMessageType('ServerStatusResult', (_message.Message,), {
  'DESCRIPTOR' : _SERVERSTATUSRESULT,
  '__module__' : 'wandb.proto.wandb_server_pb2'
  # @@protoc_insertion_point(class_scope:wandb_internal.ServerStatusResult)
  })
_sym_db.RegisterMessage(ServerStatusResult)



_INTERNALSERVICE = _descriptor.ServiceDescriptor(
  name='InternalService',
  full_name='wandb_internal.InternalService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=179,
  serialized_end=824,
  methods=[
  _descriptor.MethodDescriptor(
    name='RunUpdate',
    full_name='wandb_internal.InternalService.RunUpdate',
    index=0,
    containing_service=None,
    input_type=wandb_dot_proto_dot_wandb__internal__pb2._RUNRECORD,
    output_type=wandb_dot_proto_dot_wandb__internal__pb2._RUNUPDATERESULT,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='RunExit',
    full_name='wandb_internal.InternalService.RunExit',
    index=1,
    containing_service=None,
    input_type=wandb_dot_proto_dot_wandb__internal__pb2._RUNEXITRECORD,
    output_type=wandb_dot_proto_dot_wandb__internal__pb2._RUNEXITRESULT,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Log',
    full_name='wandb_internal.InternalService.Log',
    index=2,
    containing_service=None,
    input_type=wandb_dot_proto_dot_wandb__internal__pb2._HISTORYRECORD,
    output_type=wandb_dot_proto_dot_wandb__internal__pb2._HISTORYRESULT,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Summary',
    full_name='wandb_internal.InternalService.Summary',
    index=3,
    containing_service=None,
    input_type=wandb_dot_proto_dot_wandb__internal__pb2._SUMMARYRECORD,
    output_type=wandb_dot_proto_dot_wandb__internal__pb2._SUMMARYRESULT,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Config',
    full_name='wandb_internal.InternalService.Config',
    index=4,
    containing_service=None,
    input_type=wandb_dot_proto_dot_wandb__internal__pb2._CONFIGRECORD,
    output_type=wandb_dot_proto_dot_wandb__internal__pb2._CONFIGRESULT,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Output',
    full_name='wandb_internal.InternalService.Output',
    index=5,
    containing_service=None,
    input_type=wandb_dot_proto_dot_wandb__internal__pb2._OUTPUTRECORD,
    output_type=wandb_dot_proto_dot_wandb__internal__pb2._OUTPUTRESULT,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='ServerShutdown',
    full_name='wandb_internal.InternalService.ServerShutdown',
    index=6,
    containing_service=None,
    input_type=_SERVERSHUTDOWNREQUEST,
    output_type=_SERVERSHUTDOWNRESULT,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='ServerStatus',
    full_name='wandb_internal.InternalService.ServerStatus',
    index=7,
    containing_service=None,
    input_type=_SERVERSTATUSREQUEST,
    output_type=_SERVERSTATUSRESULT,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_INTERNALSERVICE)

DESCRIPTOR.services_by_name['InternalService'] = _INTERNALSERVICE

# @@protoc_insertion_point(module_scope)
