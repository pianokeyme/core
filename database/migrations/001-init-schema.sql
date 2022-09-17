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

--
-- Name: keyme; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA keyme;


ALTER SCHEMA keyme OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: analyzed; Type: TABLE; Schema: keyme; Owner: postgres
--

CREATE TABLE keyme.analyzed (
    id bigint NOT NULL,
    data_ref text NOT NULL,
    version integer NOT NULL
);


ALTER TABLE keyme.analyzed OWNER TO postgres;

--
-- Name: analyzed_id_seq; Type: SEQUENCE; Schema: keyme; Owner: postgres
--

CREATE SEQUENCE keyme.analyzed_id_seq
    START WITH 1000000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE keyme.analyzed_id_seq OWNER TO postgres;

--
-- Name: analyzed_id_seq; Type: SEQUENCE OWNED BY; Schema: keyme; Owner: postgres
--

ALTER SEQUENCE keyme.analyzed_id_seq OWNED BY keyme.analyzed.id;


--
-- Name: audio; Type: TABLE; Schema: keyme; Owner: postgres
--

CREATE TABLE keyme.audio (
    id bigint NOT NULL,
    data_ref text NOT NULL,
    version integer NOT NULL
);


ALTER TABLE keyme.audio OWNER TO postgres;

--
-- Name: audio_id_seq; Type: SEQUENCE; Schema: keyme; Owner: postgres
--

CREATE SEQUENCE keyme.audio_id_seq
    START WITH 1000000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE keyme.audio_id_seq OWNER TO postgres;

--
-- Name: audio_id_seq; Type: SEQUENCE OWNED BY; Schema: keyme; Owner: postgres
--

ALTER SEQUENCE keyme.audio_id_seq OWNED BY keyme.audio.id;


--
-- Name: controller; Type: TABLE; Schema: keyme; Owner: postgres
--

CREATE TABLE keyme.controller (
    id bigint NOT NULL,
    name text NOT NULL,
    conn_id text NOT NULL,
    belongs_to bigint NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE keyme.controller OWNER TO postgres;

--
-- Name: controller_id_seq; Type: SEQUENCE; Schema: keyme; Owner: postgres
--

CREATE SEQUENCE keyme.controller_id_seq
    START WITH 1000000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE keyme.controller_id_seq OWNER TO postgres;

--
-- Name: controller_id_seq; Type: SEQUENCE OWNED BY; Schema: keyme; Owner: postgres
--

ALTER SEQUENCE keyme.controller_id_seq OWNED BY keyme.controller.id;


--
-- Name: recording; Type: TABLE; Schema: keyme; Owner: postgres
--

CREATE TABLE keyme.recording (
    id bigint NOT NULL,
    name text NOT NULL,
    audio_id bigint NOT NULL,
    analyzed_id bigint NOT NULL,
    created_by bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE keyme.recording OWNER TO postgres;

--
-- Name: recording_id_seq; Type: SEQUENCE; Schema: keyme; Owner: postgres
--

CREATE SEQUENCE keyme.recording_id_seq
    START WITH 1000000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE keyme.recording_id_seq OWNER TO postgres;

--
-- Name: recording_id_seq; Type: SEQUENCE OWNED BY; Schema: keyme; Owner: postgres
--

ALTER SEQUENCE keyme.recording_id_seq OWNED BY keyme.recording.id;


--
-- Name: user; Type: TABLE; Schema: keyme; Owner: postgres
--

CREATE TABLE keyme."user" (
    id bigint NOT NULL,
    name text NOT NULL,
    email text
);


ALTER TABLE keyme."user" OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: keyme; Owner: postgres
--

CREATE SEQUENCE keyme.user_id_seq
    START WITH 1000000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE keyme.user_id_seq OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: keyme; Owner: postgres
--

ALTER SEQUENCE keyme.user_id_seq OWNED BY keyme."user".id;


--
-- Name: analyzed id; Type: DEFAULT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.analyzed ALTER COLUMN id SET DEFAULT nextval('keyme.analyzed_id_seq'::regclass);


--
-- Name: audio id; Type: DEFAULT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.audio ALTER COLUMN id SET DEFAULT nextval('keyme.audio_id_seq'::regclass);


--
-- Name: controller id; Type: DEFAULT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.controller ALTER COLUMN id SET DEFAULT nextval('keyme.controller_id_seq'::regclass);


--
-- Name: recording id; Type: DEFAULT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.recording ALTER COLUMN id SET DEFAULT nextval('keyme.recording_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme."user" ALTER COLUMN id SET DEFAULT nextval('keyme.user_id_seq'::regclass);


--
-- Name: analyzed pk_analyzed; Type: CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.analyzed
    ADD CONSTRAINT pk_analyzed PRIMARY KEY (id);


--
-- Name: audio pk_audio; Type: CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.audio
    ADD CONSTRAINT pk_audio PRIMARY KEY (id);


--
-- Name: controller pk_controller; Type: CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.controller
    ADD CONSTRAINT pk_controller PRIMARY KEY (id);


--
-- Name: recording pk_recording; Type: CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.recording
    ADD CONSTRAINT pk_recording PRIMARY KEY (id);


--
-- Name: user pk_user; Type: CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme."user"
    ADD CONSTRAINT pk_user PRIMARY KEY (id);


--
-- Name: controller fk_controller_user; Type: FK CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.controller
    ADD CONSTRAINT fk_controller_user FOREIGN KEY (belongs_to) REFERENCES keyme."user"(id);


--
-- Name: recording fk_recording_analyzed; Type: FK CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.recording
    ADD CONSTRAINT fk_recording_analyzed FOREIGN KEY (analyzed_id) REFERENCES keyme.analyzed(id);


--
-- Name: recording fk_recording_audio; Type: FK CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.recording
    ADD CONSTRAINT fk_recording_audio FOREIGN KEY (audio_id) REFERENCES keyme.audio(id);


--
-- Name: recording fk_recording_user; Type: FK CONSTRAINT; Schema: keyme; Owner: postgres
--

ALTER TABLE ONLY keyme.recording
    ADD CONSTRAINT fk_recording_user FOREIGN KEY (created_by) REFERENCES keyme."user"(id);


--
-- PostgreSQL database dump complete
--

