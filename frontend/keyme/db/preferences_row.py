from dataclasses import dataclass


@dataclass
class PreferencesRow:
    id: int
    for_user: int
    prefs: str
