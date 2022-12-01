import http

import boto3
from flask import Flask, jsonify, request

from .models import Recording, RecordingSchema, Preferences, PreferencesSchema
from keyme.db import Repository as DbRepository, RecordingRow, PreferencesRow
from keyme.s3 import Repository as S3Repository

db_repo = DbRepository()

session = boto3.session.Session(profile_name="uottawa", region_name="ca-central-1")

s3 = session.resource("s3")

s3_repo = S3Repository(s3)

app = Flask(__name__)


def recording_from_row(row: RecordingRow):
    recording = Recording.from_db(row)
    recording.audio_url = s3_repo.audio_ref_to_url(row.audio_data_ref)
    return recording


@app.route("/api/recordings", methods=["GET"])
def get_recordings():
    schema = RecordingSchema(many=True)

    db_recordings = db_repo.get_all_recordings()
    recordings = map(recording_from_row, db_recordings)

    return jsonify(schema.dump(recordings))


@app.route("/api/recording/<int:recording_id>", methods=["DELETE"])
def remove_recording(recording_id: int):
    row = RecordingRow.from_id(recording_id)

    db_repo.remove_recording(row)

    return "", http.HTTPStatus.NO_CONTENT


@app.route("/api/preferences", methods=["PUT"])
def save_preferences():
    schema = PreferencesSchema()
    preferences = schema.load(request.get_json())

    row = PreferencesRow(0, 0, schema.dumps(preferences))

    db_repo.save_preferences(row)

    return "", http.HTTPStatus.NO_CONTENT
