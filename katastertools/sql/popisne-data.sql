-- Vytvorenie tabuliek pre popisne data Katastra
BEGIN;
	-- kn_bp
	CREATE TABLE kn_bp (
		row_id serial PRIMARY KEY,
		ku integer,
		icp integer,
		clv integer,
		pcs integer,
		bnp smallint,
		cip real,
		cib smallint,
		cnp character varying(4),
		civ character varying(30),
		vym integer,
		pec integer,
		mss integer,
		cit bigint,
		men bigint,
		pvz integer,
		kpv smallint,
		cen integer,
		oce integer,
		cas character varying(30),
		crc integer,
		naz_suboru character varying(20)
	);
	COMMENT ON TABLE kn_bp IS 'Kataster: zoznam vlastnickych podielov k bytom';

	CREATE INDEX idx_kn_bp_ku
		ON kn_bp (ku);

	CREATE INDEX idx_kn_bp_clv
		ON kn_bp (clv);

	CREATE INDEX idx_kn_bp_cip
		ON kn_bp (cip);

	CREATE INDEX idx_kn_bp_cib
		ON kn_bp (cib);

	CREATE INDEX idx_kn_bp_cnp
		ON kn_bp (cnp);

	CREATE INDEX idx_kn_bp_civ
		ON kn_bp (civ);

	CREATE INDEX idx_kn_bp_pec
		ON kn_bp (pec);


	-- kn_cs
	CREATE TABLE kn_cs (
		row_id serial PRIMARY KEY,
		parckey character varying(17),
		ku integer,
		ics integer,
		clv integer,
		cel integer,
		cpa integer,
		pec integer,
		mss integer,
		vym integer,
		pkk character varying(40),
		ums smallint,
		drs smallint,
		pvz integer,
		kpv smallint,
		don integer,
		cen integer,
		oce integer,
		cas character varying(30),
		zcs integer,
		crc integer,
		naz_suboru character varying(20) 
	);
	COMMENT ON TABLE kn_cs IS 'Kataster: zoznam stavieb na cudzich pozemkoch';
	
	CREATE INDEX idx_kn_cs_parckey
		ON kn_cs (parckey);

	CREATE INDEX idx_kn_cs_ku
		ON kn_cs (ku);

	CREATE INDEX idx_kn_cs_cpa
		ON kn_cs (cpa);

	CREATE INDEX idx_kn_cs_clv
		ON kn_cs (clv);

	CREATE INDEX idx_kn_cs_pec
		ON kn_cs (pec);


	-- kn_ep
	CREATE TABLE kn_ep (
		row_id serial PRIMARY KEY,
		parckey character varying(17),
		ku integer,
		cpa integer,
		cpu smallint,
		vym integer,
		kvv smallint,
		drp smallint,
		don smallint,
		pkk integer,
		mss smallint,
		pec integer,
		cel integer,
		clv integer,
		kpv smallint,
		ump smallint,
		pvz integer,
		miv smallint,
		clm integer,
		drv integer,
		ndp smallint,
		prp smallint,
		spn smallint,
		mlm integer,
		cen real,
		oce integer,
		pcp integer,
		cas character varying(30),
		crc integer,
		naz_suboru character varying(20)
	);
	COMMENT ON TABLE kn_ep IS 'Kataster: informacie o zdruzenych parcelach';

	CREATE INDEX idx_kn_ep_clv
		ON kn_ep (clv);

	CREATE INDEX idx_kn_ep_drp
		ON kn_ep (drp);

	CREATE INDEX idx_kn_ep_ku
		ON kn_ep (ku);

	CREATE INDEX idx_kn_ep_cpa
		ON kn_ep (cpa);

	CREATE INDEX idx_kn_ep_cpu
		ON kn_ep (cpu);

	CREATE INDEX idx_kn_ep_ump
		ON kn_ep (ump);

	CREATE INDEX idx_kn_ep_parckey
		ON kn_ep (parckey);


	-- kn_lv
	CREATE TABLE kn_lv (
		row_id serial PRIMARY KEY,
		ku integer,
		clv integer,
		psv smallint,
		rzs smallint,
		kpv smallint,
		rzp smallint,
		pvz integer,
		pep smallint,
		ppl smallint,
--SM, 21.06.2017, podla kat. udajov z 28.04.2017 >
                slv character varying(10),
		dst smallint,
--SM, 21.06.2017 <
		crc integer,
		naz_suboru character varying(20)
	);
	COMMENT ON TABLE kn_lv IS 'Kataster: listy vlastnictva';

	CREATE INDEX idx_kn_lv_ku
		ON kn_lv (ku);

	CREATE INDEX idx_kn_lv_clv
		ON kn_lv (clv);


	-- kn_pa
	CREATE TABLE kn_pa (
		row_id serial PRIMARY KEY,
		parckey character varying(17),
		ku integer,
		cpa integer,
		vym integer,
		kvv smallint,
		drp smallint,
		don smallint,
		pkk integer,
		mss smallint,
		pec integer,
		cel integer,
		clv integer,
		kpv smallint,
		ump smallint,
		pvz integer,
		miv smallint,
		clm integer,
		drv integer,
		prp smallint,
		spn smallint,
		ndp smallint,
		dn1 smallint,
		dn2 smallint,
		dn3 smallint,
		dn4 smallint,
		dn5 smallint,
		dn6 smallint,
		dn7 smallint,
		dn8 smallint,
		mlm integer,
		cen real,
		oce integer,
		cas character varying(30),
		crc integer,
		naz_suboru character varying(20)
	);
	COMMENT ON TABLE kn_pa IS 'Kataster: informacie o parcelach';

	CREATE INDEX idx_kn_pa_clv
		ON kn_pa (clv);

	CREATE INDEX idx_kn_pa_drp
		ON kn_pa (drp);

	CREATE INDEX idx_kn_pa_ku
		ON kn_pa (ku);

	CREATE INDEX idx_kn_pa_cpa
		ON kn_pa (cpa);

	CREATE INDEX idx_kn_pa_cel
		ON kn_pa (cel);

	CREATE INDEX idx_kn_pa_ump
		ON kn_pa (ump);

	CREATE INDEX idx_kn_pa_parckey
		ON kn_pa (parckey);


	-- kn_pk
	CREATE TABLE kn_pk (
		row_id serial PRIMARY KEY,
		ku integer,
		ump smallint,
		cpk integer,
		npk character varying(28),
		cpu integer,
		crc integer,
		naz_suboru character varying(20)
	);
	COMMENT ON TABLE kn_pk IS 'Kataster: Povodne k.u.';


	-- kn_pv
	CREATE TABLE kn_pv (
		row_id serial PRIMARY KEY,
		ku integer,
		idc integer,
		clv integer,
		pcs smallint,
		idt smallint,
		idn bigint,
		cde smallint,
		drf smallint,
		poz text,
		pvz integer,
		kpv smallint,
		idu character varying(255),
		crc integer,
		naz_suboru character varying(20)
	);
	COMMENT ON TABLE kn_pv IS 'Kataster: pravne vztahy';

	CREATE INDEX idx_kn_pv_ku
		ON kn_pv (ku);

	CREATE INDEX idx_kn_pv_clv
		ON kn_pv (clv);


	-- kn_uz
	CREATE TABLE kn_uz (
		row_id serial PRIMARY KEY,
		ku integer,
		cel integer,
		sip integer,
		sek smallint,
		pks smallint,
		pvz integer,
		rzp smallint,
		kpv smallint,
		ppe smallint,
		ico bigint,
		uzi character varying(150),
		tid character varying(255),
		naj character varying(255),
		crc integer,
		naz_suboru character varying(20)
	);
	COMMENT ON TABLE kn_uz IS 'Kataster: ';

	CREATE INDEX idx_kn_uz_ku
		ON kn_uz (ku);

	CREATE INDEX idx_kn_uz_cel
		ON kn_uz (cel);


	-- kn_vl
	CREATE TABLE kn_vl (
		row_id serial PRIMARY KEY,
		ku integer,
		clv integer,
		pcs smallint,
		cit bigint,
		men bigint,
		pvz integer,
		kpv smallint,
		ico bigint,
--SM, 21.06.2017, podla kat. udajov z 28.04.2017 >
                pcz bigint,
--SM, 21.06.2017 <
		sta integer,
		rci bigint,
		stb integer,
		vla character varying(255),
		tvl smallint,
		tuc smallint,
		dru smallint,
		pri character varying(150),
		mno character varying(30),
		rod character varying(30),
		tip character varying(30),
		prv character varying(30),
		mev character varying(30),
		rov character varying(30),
		tiz character varying(30),
		ulc character varying(50),
		cpo character varying(30),
		mst character varying(50),
		psc character varying(6),
		dop character varying(90),
		stt character varying(30),
		tid integer,
		crc integer,
		naz_suboru character varying(20)
	);
	COMMENT ON TABLE kn_vl IS 'Kataster: zoznam vlastnikov';

	CREATE INDEX idx_kn_vl_clv
		ON kn_vl (clv);

	CREATE INDEX idx_kn_vl_ku
		ON kn_vl (ku);

	CREATE INDEX idx_kn_vl_ico
		ON kn_vl (ico);

	CREATE INDEX idx_kn_vl_rci
		ON kn_vl (rci);

	CREATE INDEX idx_kn_vl_vla
		ON kn_vl (vla);


	-- kn_nj
	CREATE TABLE kn_nj (
		row_id serial PRIMARY KEY,
		ku integer,
		cel integer,
		ico bigint,
		naj character varying(255),
		pvz integer,
		sek integer,
		sip integer,
		tid integer,
		crc integer,
		naz_suboru character varying(20)
	);
	COMMENT ON TABLE kn_nj IS 'Kataster: drzitel, najomca a ina opr. osoba';
	
	CREATE INDEX idx_kn_nj_ku
		ON kn_nj (ku);

	CREATE INDEX idx_kn_nj_cel
		ON kn_nj (cel);

	CREATE INDEX idx_kn_nj_ico
		ON kn_nj (ico);
END;


-- vim: set ts=2 sts=2 sw=2 noet:
