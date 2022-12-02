# language=sql
SELECT_RECORDING = """
select r.id,
       r."name",
       r.audio_id,
       r.analyzed_id,
       r.is_preprocessed,
       r.created_by,
       r.created_at,
       au.data_ref  as audio_data_ref,
       au."version" as audio_version,
       an.data_ref  as analyzed_data_ref,
       an."version" as analyzed_version
from keyme.recording r
         join keyme.audio au on
    r.audio_id = au.id
         join keyme.analyzed an on
    r.analyzed_id = an.id
where r.deleted_at is null
  and r.id = %s
limit 1
"""

# language=sql
SELECT_RECORDINGS = """
select r.id,
       r."name",
       r.audio_id,
       r.analyzed_id,
       r.is_preprocessed,
       r.created_by,
       r.created_at,
       au.data_ref  as audio_data_ref,
       au."version" as audio_version,
       an.data_ref  as analyzed_data_ref,
       an."version" as analyzed_version
from keyme.recording r
         join keyme.audio au on
    r.audio_id = au.id
         join keyme.analyzed an on
    r.analyzed_id = an.id
where r.deleted_at is null
order by r.created_at desc,
         r.id;
"""

# language=sql
INSERT_ANALYZED = """
insert into keyme.analyzed (id, data_ref, version)
values (default, %s, %s)
returning id;
"""

# language=sql
INSERT_AUDIO = """
insert into keyme.audio (id, data_ref, version)
values (default, %s, %s)
returning id;
"""

# language=sql
INSERT_RECORDING = """
insert into keyme.recording (id, name, audio_id, analyzed_id, is_preprocessed, created_by, created_at, deleted_at)
values (default, %s, %s, %s, %s, %s, now(), null);
"""

# language=sql
DELETE_RECORDING = """
update keyme.recording r
set deleted_at = now()
where r.id = %s;
"""

# langauge=sql
GET_PREFERENCES = """
select p.id, p.for_user, p.prefs from keyme.preferences p where p.id = 1;
"""

# langauge=sql
UPDATE_PREFERENCES = """
update keyme.preferences p set prefs = %s where p.for_user = 1;
"""
