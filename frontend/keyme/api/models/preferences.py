from dataclasses import dataclass

from marshmallow import Schema, fields, post_load


@dataclass
class Preferences:
    size: str
    scheme: str
    color: str


class PreferencesSchema(Schema):
    size = fields.String()
    scheme = fields.String()
    color = fields.String()

    @post_load
    def make_preferences(self, data, **kwargs):
        return Preferences(**data)
