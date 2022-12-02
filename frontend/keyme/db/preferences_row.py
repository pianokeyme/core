import json
from dataclasses import dataclass


@dataclass
class PreferencesRow:
    id: int
    for_user: int
    prefs: str

    @staticmethod
    def from_rom(row):
        return PreferencesRow(row[0], row[1], json.dumps(row[2]))
