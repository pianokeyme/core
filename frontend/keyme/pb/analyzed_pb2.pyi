from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Analyzed(_message.Message):
    __slots__ = ["frameSize", "id", "notes", "version"]
    FRAMESIZE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    frameSize: float
    id: str
    notes: _containers.RepeatedScalarFieldContainer[int]
    version: int
    def __init__(self, version: _Optional[int] = ..., id: _Optional[str] = ..., frameSize: _Optional[float] = ..., notes: _Optional[_Iterable[int]] = ...) -> None: ...
