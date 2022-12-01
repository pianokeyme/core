from datetime import datetime
from dataclasses import dataclass

from marshmallow import Schema, fields

from keyme.db import RecordingRow


@dataclass
class Recording:
    id: int
    name: str
    audio_id: int
    is_preprocessed: bool
    created_by: int
    created_at: datetime
    audio_url: str
    audio_version: int

    @staticmethod
    def from_db(row: RecordingRow):
        return Recording(row.id, row.name, row.audio_id, row.is_preprocessed, row.created_by, row.created_at, "",
                         row.audio_version)


class RecordingSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    audio_id = fields.Int()
    is_preprocessed = fields.Bool()
    created_by = fields.Int()
    created_at = fields.DateTime()
    audio_url = fields.Str()
    audio_version = fields.Int()
