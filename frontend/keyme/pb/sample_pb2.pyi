from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Sample(_message.Message):
    __slots__ = ["frameSize", "id", "notes", "sampleRate", "samples", "seq", "version"]
    FRAMESIZE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    SAMPLERATE_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    frameSize: float
    id: str
    notes: _containers.RepeatedScalarFieldContainer[float]
    sampleRate: float
    samples: _containers.RepeatedScalarFieldContainer[float]
    seq: int
    version: int
    def __init__(self, version: _Optional[int] = ..., id: _Optional[str] = ..., seq: _Optional[int] = ..., sampleRate: _Optional[float] = ..., frameSize: _Optional[float] = ..., samples: _Optional[_Iterable[float]] = ..., notes: _Optional[_Iterable[float]] = ...) -> None: ...
