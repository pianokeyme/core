import re
import logging
from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool
import psycopg2.extensions

from .recording_row import RecordingRow
from .preferences_row import PreferencesRow
from .sql import SELECT_RECORDING, SELECT_RECORDINGS, INSERT_AUDIO, INSERT_ANALYZED, INSERT_RECORDING, \
    DELETE_RECORDING, UPDATE_PREFERENCES


class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger(__name__)
        logger.info(self.mogrify(re.sub(r"\s+", " ", sql.replace("\n", " ")), args).decode("utf-8"))

        try:
            psycopg2.extensions.cursor.execute(self, sql, args)
        except Exception as exc:
            logger.error("%s: %s" % (exc.__class__.__name__, exc))
            raise


class Repository:
    def __init__(self):
        self.db = ThreadedConnectionPool(1, 10, "dbname=keyme user=postgres password=postgres host=localhost port=5432",
                                         cursor_factory=LoggingCursor)

    @contextmanager
    def _get_conn(self):
        conn = self.db.getconn()
        try:
            yield conn
        finally:
            self.db.putconn(conn)

    @contextmanager
    def _get_cur(self):
        with self._get_conn() as conn:
            cur = conn.cursor()
            try:
                yield cur
            finally:
                cur.close()

    def get_recording(self, rec_id: int) -> RecordingRow | None:
        with self._get_cur() as cur:
            cur.execute(SELECT_RECORDING, [rec_id])

            row = cur.fetchone()

            if row is None:
                return None

            return RecordingRow.from_row(row)

    def get_all_recordings(self) -> list[RecordingRow]:
        with self._get_cur() as cur:
            cur.execute(SELECT_RECORDINGS)

            recordings = []
            for row in cur:
                recordings.append(RecordingRow.from_row(row))

            return recordings

    def save_recording(self, row: RecordingRow):
        with self._get_cur() as cur:
            cur.execute(INSERT_AUDIO, [row.audio_data_ref, row.audio_version])

            audio_id = cur.fetchone()[0]

            cur.execute(INSERT_ANALYZED, [row.analyzed_data_ref, row.analyzed_version])

            analyzed_id = cur.fetchone()[0]

            # name, audio_id, analyzed_id, is_preprocessed, created_by
            cur.execute(INSERT_RECORDING, [row.name, audio_id, analyzed_id, row.is_preprocessed, row.created_by])

            cur.connection.commit()

    def remove_recording(self, row: RecordingRow):
        with self._get_cur() as cur:
            cur.execute(DELETE_RECORDING, [row.id])

            cur.connection.commit()

    def save_preferences(self, row: PreferencesRow):
        with self._get_cur() as cur:
            cur.execute(UPDATE_PREFERENCES, [row.prefs])

            cur.connection.commit()
