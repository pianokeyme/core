from dataclasses import dataclass
from datetime import datetime


@dataclass
class RecordingRow:
    id: int
    name: str
    audio_id: int
    analyzed_id: int
    is_preprocessed: bool
    created_by: int
    created_at: datetime
    audio_data_ref: str
    audio_version: int
    analyzed_data_ref: str
    analyzed_version: int

    @staticmethod
    def from_row(row: tuple):
        return RecordingRow(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])

    @staticmethod
    def from_id(recording_id: int):
        return RecordingRow(recording_id, "", 0, 0, False, 0, datetime.now(), "", 0, "", 0)
