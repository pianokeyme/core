--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5 (Homebrew)
-- Dumped by pg_dump version 14.5 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY keyme.preferences DROP CONSTRAINT IF EXISTS preferences_for_user_fkey;
ALTER TABLE IF EXISTS ONLY keyme.preferences DROP CONSTRAINT IF EXISTS preferences_pkey;
ALTER TABLE IF EXISTS keyme.preferences ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS keyme.preferences_id_seq;
DROP TABLE IF EXISTS keyme.preferences;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: preferences; Type: TABLE; Schema: keyme; Owner: postgres
--

CREATE TABLE keyme.preferences (
    id bigint NOT NULL,
    for_user bigint NOT NULL,
    prefs jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE keyme.preferences OWNER TO postgres;

--
-- Name: preferences_id_seq; Type: SEQUENCE; Schema: keyme; Owner: postgres
--

CREATE SEQUENCE keyme.preferences_id_seq
    START WITH 1000000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE keyme.preferences_id_seq OWNER TO postgres;

--
-- Name: preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: keyme; Owner: postgres
--

ALTER SEQUENCE keyme.preferences_id_seq OWNED BY keyme.preferences.id;


--
-- Name: preferences id; Type: DEFAULT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.preferences ALTER COLUMN id SET DEFAULT nextval('keyme.preferences_id_seq'::regclass);


--
-- Name: preferences preferences_pkey; Type: CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.preferences
    ADD CONSTRAINT preferences_pkey PRIMARY KEY (id);


--
-- Name: preferences preferences_for_user_fkey; Type: FK CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.preferences
    ADD CONSTRAINT preferences_for_user_fkey FOREIGN KEY (for_user) REFERENCES keyme."user"(id);


--
-- PostgreSQL database dump complete
--

insert into keyme.preferences (id, for_user, prefs) values
(1, 1, '{ "size": "Keyboard (61)", "scheme": "Default", "color": "#FF0000" }');
