delete from keyme.recording where id = 1;
delete from keyme.audio where id = 1;
delete from keyme.analyzed where id = 1;
delete from keyme.controller where id = 1;
delete from keyme."user" where id = 1;

insert into	keyme."user" (id, "name", email) values
(1, 'Flow', 'flow@keyme.ca');

insert into keyme.controller (id, "name", conn_id, belongs_to, deleted_at) values
(1, 'Default', 'arduino', 1, NULL);

insert into keyme.analyzed (id, data_ref, "version") values
(1, 'zzz', 1);

insert into keyme.audio (id, data_ref, "version") values
(1, 's3://keyme-dev/UphTb9Vgjj8n9kktTKyncC/audio.mp3', 1);

insert into keyme.recording (id, "name", audio_id, analyzed_id, is_preprocessed, created_by, created_at, deleted_at) values
(1, 'Rondo Alla Turca', 1, 1, false, 1, '2022-11-24T17:18:13.724Z', NULL);
