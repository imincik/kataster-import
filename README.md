# Kataster Import
Nastroj pre konverziu a import popisnych a grafickych dat Katastra SR do GIS.


# Instalacia
Vytvorenie Python virtualenv

```
$ virtualenv --system-site-packages $HOME/venvs/kataster-import
$ source $HOME/venvs/kataster-import/bin/activate
```

Instalacia cez setup.py

```
$ git clone https://github.com/imincik/kataster-import.git
$ cd kataster-import
$ python ./setup.py install
$ pip install -r requirements.txt
````

alebo bez instalacie

```
$ git clone https://github.com/imincik/kataster-import.git
$ cd kataster-import
$ pip install -r requirements.txt
$ source ./env-setup.sh
```


# Pouzitie
## Konverzia dat
Nastroj obsahuje skript _kt-sql_, ktory sluzi ako wrapper nad ostatnymi specializovanymi nastrojmi a umoznuje vykonat
konverziu popisnych a grafickych udajov v jednom kroku. Vyzaduje data ulozene v hlavnom adresari, ktory obsahuje
adresare s datami v presne definovanej strukture.

struktura podadresarov s datami katastra:
 * hlavny adresar
   * adresar 'vgi'             - subory VGI
   * adresar 'dbf' alebo 'fpu' - subory DBF resp. FPU+FPT

```
$ kt-sql <hlavny-adresar>
```

## Import dat do PostGIS
Data ziskane konverziou je mozne importovat do PostGIS z SQL suborov.

```
$ createdb kataster -T template_postgis
$ kt-vytvor_db | psql kataster
$ PGOPTIONS="-c search_path=kataster,public" psql kataster -f <hlavny-adresar>/sql/popisne_udaje.sql
$ PGOPTIONS="-c search_path=kataster,public" psql kataster -f <hlavny-adresar>/sql/graficke_udaje.sql
```

## Testovanie importu
Pre zakladne testovanie importu z hladiska kontroly vzajomneho prepojenia grafickych a popisnych udajov sluzi
SQL skript _katastertools/sql/test-import.sql_.

```
$ PGOPTIONS="-c search_path=kataster,public" psql kataster -f katastertools/sql/test-import.sql
```

# Graficke udaje
Zdrojom grafickych udajov su subory VGI. Obsahuju graficku reprezentaciu polygonovych, liniovych a bodovych
objektov Katastra.

## Vrstvy
### KLADPAR
Hranice a cisla parciel registra C, symboly druhov pozemkov

nazov vrstvy: kn_kladpar

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - cislo katastralneho uzemia
 * parckey (string)     - jedinecny identifikator parcely
 * parcela (string)     - lomene cislo parcely
 * kmen (integer)       - kmenove cislo parcely
 * podlomenie (integer) - podlomenie parcely
 * t (string)           - umiestnenia cisiel parciel v tvare Y;X;H;U|X;Y;H;U|..., kde:
                          * Y a X su suradnice referencneho bodu textu
                          * H je vyska pisma v mm pre mierku uvedenu vo vete rozsahu vykresu
                          * U je uhol stocenia textu
 * g_s (string)         - umiestnenie symbolov spolu s ich atributmi v tvare Y;X;S;U;M|X;Y;S;U;M|..., kde:
                          * Y a X su suradnice symbolu
                          * S je kod symbolu
                          * U je uhol stocenia symbolu
                          * M je mierka zmensenia symbolu
 * stav_k (timestamp with timezone) - datum a cas aktualnosti udajov
 * subor (string)       - nazov suboru
 * geom (MULTIPOLYGON)


### UOV
Hranice a cisla parciel registra E

nazov vrstvy: kn_uov

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * parckey (string)     - jedinecny identifikator parcely
 * ku (integer)         - cislo katastralneho uzemia
 * parcela (string)     - lomene cislo parcely
 * kmen (integer)       - kmenove cislo parcely
 * podlomenie (integer) - podlomenie parcely
 * t (string)           - umiestnenia cisiel parciel v tvare Y;X;H;U|X;Y;H;U|..., kde:
                          * Y a X su suradnice referencneho bodu textu
                          * H je vyska pisma textu v mm pre mierku uvedenu vo vete rozsahu vykresu
                          * U je uhol stocenia textu
 * stav_k (timestamp with timezone) - datum a cas aktualnosti udajov
 * subor (string)       - nazov suboru
 * geom (MULTIPOLYGON)


### ZAPPAR
Hranica druhov pozemkov, ktore nie su v KLADPAR

nazov vrstvy: kn_zappar

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - cislo katastralneho uzemia
 * g_k (integer)        - kresliaci kluc linie. Linie musia mat K uvedenu na prvom bode. Vsetky nasledujuce spojenia preberaju
                          tuto hodnotu atributu. Pokial je na bode uvedena nova hodnota atributu K, je potrebne liniu
                          na tomto bode ukoncit a zacat dalsiu liniu s novou hodnotou K.
 * stav_k (timestamp with timezone) - datum a cas aktualnosti udajov
 * subor (string)       - nazov suboru
 * geom (LINESTRING)


### KATUZ
Hranica katastralneho uzemia

nazov vrstvy: kn_katuz

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - cislo katastralneho uzemia
 * ku_cislo (integer)   - cislo katastralneho uzemia KU
 * ku_nazov (string)    - nazov susedneho kat. uzemia HKU
 * g_k (integer)        - kresliaci kluc linie. Linie musia mat K uvedenu na prvom bode. Vsetky nasledujuce spojenia preberaju
                          tuto hodnotu atributu. Pokial je na bode uvedena nova hodnota atributu K, je potrebne liniu
                          na tomto bode ukoncit a zacat dalsiu liniu s novou hodnotou K.
 * stav_k (timestamp with timezone) - datum a cas aktualnosti udajov
 * subor (string)       - nazov suboru
 * geom (LINESTRING)


### LINIE
Dalsie prvky polohopisu (inzinierske siete, hranica CHKO ...)

nazov vrstvy: kn_linie

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - cislo katastralneho uzemia
 * g_k (integer)        - kresliaci kluc linie. Linie musia mat K uvedenu na prvom bode. Vsetky nasledujuce spojenia preberaju
                          tuto hodnotu atributu. Pokial je na bode uvedena nova hodnota atributu K, je potrebne liniu
                          na tomto bode ukoncit a zacat dalsiu liniu s novou hodnotou K.
 * stav_k (timestamp with timezone) - datum a cas aktualnosti udajov
 * subor (string)       - nazov suboru
 * geom (LINESTRING)


### ZNACKY
Mapove znacky okrem znaciek druhov pozemkov

nazov vrstvy: kn_znacky

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - cislo katastralneho uzemia
 * g_s (integer)        - kod znacky (hodnota atributu S vo VGI)
 * g_u (real)           - uhol stocenia znacky
 * g_m (real)           - mierka zmensenia znacky
 * stav_k (timestamp with timezone) - datum a cas aktualnosti udajov
 * subor (string)       - nazov suboru
 * geom (POINT)


### POPIS
Sidelne a nesidelne nazvy

nazov vrstvy: kn_popisy

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - cislo katastralneho uzemia
 * text (string)        - text
 * g_k (integer)        - kresliaci kluc textu
 * g_u (real)           - uhol stocenia textu
 * g_h (real)           - vyska pisma textu v mm pre mierku uvedenu vo vete rozsahu vykresu
 * g_f (integer)        - typ fontu
 * g_d (integer)        - vztazny bod textu
 * stav_k (timestamp with timezone) - datum a cas aktualnosti udajov
 * subor (string)       - nazov suboru
 * geom (POINT)


### ZUOB
Hranica zastavaneho uzemia obce

nazov vrstvy: kn_zuob

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - cislo katastralneho uzemia
 * stav_k (timestamp with timezone) - datum a cas aktualnosti udajov
 * subor (string)       - nazov suboru
 * geom (MULTIPOLYGON)


### BPEJ
Hranice arealov bonitovanych podno-ekologickych jednotiek

nazov vrstvy: kn_bpej

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - cislo katastralneho uzemia
 * bj (string)          - bonitna jednotka
 * stav_k (timestamp with timezone) - datum a cas aktualnosti udajov
 * subor (string)       - nazov suboru
 * geom (MULTIPOLYGON)


## parckey
format: KKKKKKCCAAAAABBBD
 * KKKKKK               - kod katastralneho uzemia
 * CC                   - cislo povodneho uzemia (u parciel registra C vzdy 00)
 * AAAAA                - kmenove cislo parcely
 * BBB                  - podlomenie parcely
 * D                    - diel parcely

cislo s nizsim poctom cifier je zlava doplnene nulami


# Popisne udaje
Zdrojom popisnych udajov su subory FPU alebo DBF. Obsahuju popisne informacie
viazuce sa na objekty Katastra.
