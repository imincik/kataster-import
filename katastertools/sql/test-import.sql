-- REGISTER C
SELECT
	'C' AS "reg",
	kl.ku AS "c. KU",

	-- vsetky parcely
	COUNT(*) AS "p. celkom",

	-- parcely obsahujuce platny LV
	(SELECT COUNT(*)
		FROM kn_kladpar a
		LEFT JOIN kn_pa pa ON a.parckey = pa.parckey
		WHERE a.parcela != '0'
		AND pa.clv IS NOT NULL
		AND a.ku = kl.ku) AS "p. platny LV",

	-- parcely s nezalozenym LV (LV = 0)
	(SELECT COUNT(*)
		FROM kn_kladpar a
		WHERE a.parcela = '0'
		AND a.ku = kl.ku) AS "p. bez LV", 

	-- parcely bez popisnych udajov
	(SELECT COUNT(*)
		FROM kn_kladpar a
		LEFT JOIN kn_pa pa ON a.parckey = pa.parckey
		WHERE a.parcela != '0'
		AND pa.clv IS NULL
		AND a.ku = kl.ku) AS "p. bez popis. u.",

	-- duplicitne parcely
	(SELECT COUNT(*)
		FROM kn_kladpar a, kn_kladpar b
			WHERE a.parckey = b.parckey
			AND a.gid > b.gid
			AND a.parcela != '0'
			AND a.ku = kl.ku
	) AS "p. duplicitne"

FROM kn_kladpar kl
GROUP BY "reg", "c. KU"
ORDER BY "c. KU";


-- REGISTER E
SELECT
	'E' AS "reg",
	kl.ku AS "c. KU",

	-- vsetky parcely
	COUNT(*) AS "p. celkom",

	-- parcely obsahujuce platny LV
	(SELECT COUNT(*)
		FROM kn_uov a
		LEFT JOIN kn_ep p ON a.parckey = p.parckey
		WHERE a.parcela != '0'
		AND p.clv IS NOT NULL
		AND a.ku = kl.ku) AS "p. platny LV",

	-- parcely s nezalozenym LV (LV = 0)
	(SELECT COUNT(*)
		FROM kn_uov a
		WHERE a.parcela = '0'
		AND a.ku = kl.ku) AS "p. bez LV", 

	-- parcely bez popisnych udajov
	(SELECT COUNT(*)
		FROM kn_uov a
		LEFT JOIN kn_ep p ON a.parckey = p.parckey
		WHERE a.parcela != '0'
		AND p.clv IS NULL
		AND a.ku = kl.ku) AS "p. bez popis. u.",

	-- duplicitne parcely
	(SELECT COUNT(*)
		FROM kn_kladpar a, kn_kladpar b
			WHERE a.parckey = b.parckey
			AND a.gid > b.gid
			AND a.parcela != '0'
			AND a.ku = kl.ku
	) AS "p. duplicitne"

FROM kn_uov kl
GROUP BY "reg", "c. KU"
ORDER BY "c. KU";


-- vim: set ts=2 sts=2 sw=2 noet:
