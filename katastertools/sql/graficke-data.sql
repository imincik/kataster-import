-- Vytvorenie tabuliek pre graficke data Katastra
BEGIN;
	-- kn_kladpar
	CREATE TABLE kn_kladpar (
		gid serial PRIMARY KEY,
		o_id integer,
		ku integer,
		parckey character varying(17),
		parcela character varying(40),
		kmen integer,
		podlomenie integer,
		t text,
		g_s text,
		stav_k timestamptz,
		subor character varying(32)
	);
	SELECT AddGeometryColumn('kn_kladpar','geom',5514,'MULTIPOLYGON',2);
	COMMENT ON TABLE kn_kladpar IS 'Kataster: hranice a cisla parciel registra C, symboly druhov pozemkov';

	CREATE INDEX idx_kn_kladpar_gid
		ON kn_kladpar (gid);

	CREATE INDEX idx_kn_kladpar_ku
		ON kn_kladpar (ku);

	CREATE INDEX idx_kn_kladpar_parckey
		ON kn_kladpar (parckey);

	CREATE INDEX idx_kn_kladpar_parcela
		ON kn_kladpar (parcela);

	CREATE INDEX kn_kladpar_geom
		ON kn_kladpar USING GIST (geom);


	-- kn_uov
	CREATE TABLE kn_uov (
		gid serial PRIMARY KEY,
		o_id integer,
		ku integer,
		parckey character varying(17),
		parcela character varying(40),
		kmen integer,
		podlomenie integer,
		t text,
		stav_k timestamptz,
		subor character varying(32)
	);
	SELECT AddGeometryColumn('kn_uov','geom',5514,'MULTIPOLYGON',2);
	COMMENT ON TABLE kn_uov IS 'Kataster: hranice a cisla parciel registra E';

	CREATE INDEX idx_kn_uov_gid
		ON kn_uov (gid);

	CREATE INDEX idx_kn_uov_ku
		ON kn_uov (ku);

	CREATE INDEX idx_kn_uov_parckey
		ON kn_uov (parckey);

	CREATE INDEX idx_kn_uov_parcela
		ON kn_uov (parcela);

	CREATE INDEX kn_uov_geom
		ON kn_uov USING GIST (geom);


	-- kn_zuob
	CREATE TABLE kn_zuob (
		gid serial PRIMARY KEY,
		o_id integer,
		ku integer,
		stav_k timestamptz,
		subor character varying(32)
	);
	SELECT AddGeometryColumn('kn_zuob','geom',5514,'MULTIPOLYGON',2);
	COMMENT ON TABLE kn_zuob IS 'Kataster: hranica zastavaneho uzemia obce';

	CREATE INDEX idx_kn_zuob_gid
		ON kn_zuob (gid);

	CREATE INDEX idx_kn_zuob_ku
		ON kn_zuob (ku);

	CREATE INDEX kn_zuob_geom
		ON kn_zuob USING GIST (geom);


	-- kn_bpej
	CREATE TABLE kn_bpej (
		gid serial PRIMARY KEY,
		o_id integer,
		ku integer,
		bj character varying(40),
		stav_k timestamptz,
		subor character varying(32)
	);
	SELECT AddGeometryColumn('kn_bpej','geom',5514,'MULTIPOLYGON',2);
	COMMENT ON TABLE kn_bpej IS 'Kataster: hranice arealov bonitovanych podno-ekologickych jednotiek';

	CREATE INDEX idx_kn_bpej_gid
		ON kn_bpej (gid);

	CREATE INDEX idx_kn_bpej_ku
		ON kn_bpej (ku);

	CREATE INDEX kn_bpej_geom
		ON kn_bpej USING GIST (geom);


	-- kn_katuz
	CREATE TABLE kn_katuz (
		gid serial PRIMARY KEY,
		o_id integer,
		ku integer,
		ku_cislo integer,
		ku_nazov character varying(255),
		g_k integer,
		stav_k timestamptz,
		subor character varying(32)
	);
	SELECT AddGeometryColumn('kn_katuz','geom',5514,'MULTILINESTRING',2);
	COMMENT ON TABLE kn_katuz IS 'Kataster: hranica katastralneho uzemia';

	CREATE INDEX idx_kn_katuz_gid
		ON kn_katuz (gid);

	CREATE INDEX idx_kn_katuz_ku
		ON kn_katuz (ku);

	CREATE INDEX idx_kn_katuz_ku_cislo
		ON kn_katuz (ku_cislo);

	CREATE INDEX idx_kn_katuz_ku_nazov
		ON kn_katuz (ku_nazov);

	CREATE INDEX kn_katuz_geom
		ON kn_katuz USING GIST (geom);


	-- kn_zappar
	CREATE TABLE kn_zappar (
		gid serial PRIMARY KEY,
		o_id integer,
		ku integer,
		g_k integer,
		stav_k timestamptz,
		subor character varying(32)
	);
	SELECT AddGeometryColumn('kn_zappar','geom',5514,'MULTILINESTRING',2);
	COMMENT ON TABLE kn_zappar IS 'Kataster: hranica druhov pozemkov, ktore nie su v KLADPAR';

	CREATE INDEX idx_kn_zappar_gid
		ON kn_zappar (gid);

	CREATE INDEX idx_kn_zappar_ku
		ON kn_zappar (ku);

	CREATE INDEX kn_zappar_geom
		ON kn_zappar USING GIST (geom);


	-- kn_linie
	CREATE TABLE kn_linie (
		gid serial PRIMARY KEY,
		o_id integer,
		ku integer,
		g_k integer,
		stav_k timestamptz,
		subor character varying(32)
	);
	SELECT AddGeometryColumn('kn_linie','geom',5514,'MULTILINESTRING',2);
	COMMENT ON TABLE kn_linie IS 'Kataster: dalsie prvky polohopisu (inzinierske siete, hranica CHKO ...)';

	CREATE INDEX idx_kn_linie_gid
		ON kn_linie (gid);

	CREATE INDEX idx_kn_linie_ku
		ON kn_linie (ku);

	CREATE INDEX kn_linie_geom
		ON kn_linie USING GIST (geom);


	-- kn_znacky
	CREATE TABLE kn_znacky (
		gid serial PRIMARY KEY,
		o_id integer,
		ku integer,
		g_s integer,
		g_u real,
		g_m numeric(2, 1),
		stav_k timestamptz,
		subor character varying(32)
	);
	SELECT AddGeometryColumn('kn_znacky','geom',5514,'POINT',2);
	COMMENT ON TABLE kn_znacky IS 'Kataster: mapove znacky okrem znaciek druhov pozemkov';

	CREATE INDEX idx_kn_znacky_gid
		ON kn_znacky (gid);

	CREATE INDEX idx_kn_znacky_ku
		ON kn_znacky (ku);

	CREATE INDEX kn_znacky_geom
		ON kn_znacky USING GIST (geom);


	-- kn_popis
	CREATE TABLE kn_popis (
		gid serial PRIMARY KEY,
		o_id integer,
		ku integer,
		text text,
		g_k integer,
		g_u real,
		g_h numeric(2, 1),
		g_f integer,
		g_d integer,
		stav_k timestamptz,
		subor character varying(32)
	);
	SELECT AddGeometryColumn('kn_popis','geom',5514,'POINT',2);
	COMMENT ON TABLE kn_popis IS 'Kataster: sidelne a nesidelne nazvy';

	CREATE INDEX idx_kn_popis_gid
		ON kn_popis (gid);

	CREATE INDEX idx_kn_popis_ku
		ON kn_popis (ku);

	CREATE INDEX kn_popis_geom
		ON kn_popis USING GIST (geom);
END;


-- vim: set ts=2 sts=2 sw=2 noet:
