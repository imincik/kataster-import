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
Hranice a čísla parciel registra C, symboly druhov pozemkov

názov vrstvy: kn_kladpar

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - číslo katastrálneho územia
 * parckey (string)     - jedinecny identifikator parcely
 * parcela (string)     - lomené číslo parcely
 * kmen (integer)       - kmenové číslo parcely
 * podlomenie (integer) - podlomenie parcely
 * t (string)           - umiestnenia čísiel parciel v tvare Y;X;H;U|X;Y;H;U|..., kde:
                          * Y a X sú súradnice referenčného bodu textu
                          * H je výška písma v mm pre mierku uvedenú vo vete rozsahu výkresu
                          * U je uhol stočenia textu
 * g_s (string)         - umiestnenie symbolov spolu s ich atributmi v tvare Y;X;S;U;M|X;Y;S;U;M|..., kde:
                          * Y a X sú súradnice symbolu
                          * S je kód symbolu
                          * U je uhol stočenia symbolu
                          * M je mierka zmenšenia symbolu
 * stav_k (timestamp with timezone) - dátum a čas aktuálnosti údajov
 * subor (string)       - názov súboru
 * geom (MULTIPOLYGON)


### UOV
Hranice a čísla parciel registra E

názov vrstvy: kn_uov

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * parckey (string)     - jedinecny identifikator parcely
 * ku (integer)         - číslo katastrálneho územia
 * parcela (string)     - lomené číslo parcely
 * kmen (integer)       - kmenové číslo parcely
 * podlomenie (integer) - podlomenie parcely
 * t (string)           - umiestnenia čísiel parciel v tvare Y;X;H;U|X;Y;H;U|..., kde:
                          * Y a X sú súradnice referenčného bodu textu
                          * H je výška písma textu v mm pre mierku uvedenú vo vete rozsahu výkresu
                          * U je uhol stočenia textu
 * stav_k (timestamp with timezone) - dátum a čas aktuálnosti údajov
 * subor (string)       - názov súboru
 * geom (MULTIPOLYGON)


### ZAPPAR
Hranica druhov pozemkov, ktoré nie sú v KLADPAR

názov vrstvy: kn_zappar

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - číslo katastrálneho územia
 * g_k (integer)        - kresliaci kľúč línie. Linie musia mať K uvedenú na prvom bode. Všetky následujúce spojenia preberajú
                          túto hodnotu atribútu. Pokiaľ je na bode uvedená nová hodnota atribútu K, je potrebné líniu
                          na tomto bode ukončit a začať ďalšiu líniu s novou hodnotou K.
 * stav_k (timestamp with timezone) - dátum a čas aktuálnosti údajov
 * subor (string)       - názov súboru
 * geom (LINESTRING)


### KATUZ
Hranica katastrálneho územia

názov vrstvy: kn_katuz

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - číslo katastrálneho územia
 * ku_cislo (integer)   - číslo katastrálneho územia KU
 * ku_nazov (string)    - názov susedného kat. územia HKU
 * g_k (integer)        - kresliaci kľúč línie. Linie musia mať K uvedenú na prvom bode. Všetky následujúce spojenia preberajú
                          túto hodnotu atribútu. Pokiaľ je na bode uvedená nová hodnota atribútu K, je potrebné líniu
                          na tomto bode ukončit a začať ďalšiu líniu s novou hodnotou K.
 * stav_k (timestamp with timezone) - dátum a čas aktuálnosti údajov
 * subor (string)       - názov súboru
 * geom (LINESTRING)


### LINIE
Ďalšie prvky polohopisu (inžinierske siete, hranica CHKO ...)

názov vrstvy: kn_linie

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - číslo katastrálneho územia
 * g_k (integer)        - kresliaci kľúč línie. Linie musia mať K uvedenú na prvom bode. Všetky následujúce spojenia preberajú
                          túto hodnotu atribútu. Pokiaľ je na bode uvedená nová hodnota atribútu K, je potrebné líniu
                          na tomto bode ukončit a začať ďalšiu líniu s novou hodnotou K.
 * stav_k (timestamp with timezone) - dátum a čas aktuálnosti údajov
 * subor (string)       - názov súboru
 * geom (LINESTRING)


### ZNACKY
Mapové značky okrem značiek druhov pozemkov

názov vrstvy: kn_znacky

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - číslo katastrálneho územia
 * g_s (integer)        - kód značky (hodnota atributu S vo VGI)
 * g_u (real)           - uhol stočenia značky
 * g_m (real)           - mierka zmenšenia značky
 * stav_k (timestamp with timezone) - dátum a čas aktuálnosti údajov
 * subor (string)       - názov súboru
 * geom (POINT)


### POPIS
Sídelné a nesídelné názvy

názov vrstvy: kn_popisy

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - číslo katastrálneho územia
 * text (string)        - text
 * g_k (integer)        - kresliaci kľúč textu
 * g_u (real)           - uhol stočenia textu
 * g_h (real)           - výška písma textu v mm pre mierku uvedenú vo vete rozsahu výkresu
 * g_f (integer)        - typ fontu
 * g_d (integer)        - vzťažný bod textu
 * stav_k (timestamp with timezone) - dátum a čas aktuálnosti údajov
 * subor (string)       - názov súboru
 * geom (POINT)


### ZUOB
Hranica zastavaného územia obce

názov vrstvy: kn_zuob

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - číslo katastrálneho územia
 * stav_k (timestamp with timezone) - dátum a čas aktuálnosti údajov
 * subor (string)       - názov súboru
 * geom (MULTIPOLYGON)


### BPEJ
Hranice areálov bonitovaných pôdno-ekologických jednotiek

názov vrstvy: kn_bpej

atributy:
 * o_id (integer)       - ID objektu vo VGI subore
 * ku (integer)         - číslo katastrálneho územia
 * bj (string)          - bonitná jednotka
 * stav_k (timestamp with timezone) - dátum a čas aktuálnosti údajov
 * subor (string)       - názov súboru
 * geom (MULTIPOLYGON)


## parckey
format: KKKKKKCCAAAAABBBD
 * KKKKKK               - kód katastrálneho územia
 * CC                   - u parcel registra C vyplňujeme 00 (CPU nie je zadané)
 * AAAAA                - kmeňové číslo parcely
 * BBB                  - podlomenie parcely
 * D                    -  diel parcely

číslo s nižším počtom cifier je zľava doplnené nulami


# Popisne udaje
Zdrojom popisnych udajov su subory FPU alebo DBF. Obsahuju popisne informacie
viazuce sa na objekty Katastra.
