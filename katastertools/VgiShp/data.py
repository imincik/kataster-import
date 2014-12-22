#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import math
import logging

from osgeo import ogr


class NepodporovanaVeta(Exception):
	pass

class Objekt(object):
	nazov_vrstvy = None
	polia = ()

	"""Zaklady abstraktny objekt v katastri"""
	def __init__(self, atributy_suboru):
		# v spravach sa zbieraju chybove hlasky ktore sa po spracovani vypisu
		self.spravy = []

		# atributy objektu su pre kazdy objekt ine
		self.atributy_objektu = {}
		self.atributy_objektu['ID'] = ''
		# atributy suboru su rovnake pre vsetky objektu v danom subore
		self.atributy_suboru = atributy_suboru

		self.textove_elementy = []

		# meta informacie atributov ktore su potrebne pre spravne vytvorenie vystupneho suboru
		self.meta = {'nazov_vrstvy': self.nazov_vrstvy}
		self.meta['polia'] = []
		self.meta['polia'].append({'nazov': 'o_id', 'typ': 'OFTInteger'})
		self.meta['polia'].append({'nazov': 'ku', 'typ': 'OFTInteger', 'sirka': 6})
		self.meta['polia'].extend(self.polia)
		self.meta['polia'].append({'nazov': 'stav_k', 'typ': 'OFTDateTime'})
		self.meta['polia'].append({'nazov': 'subor', 'typ': 'OFTString', 'sirka': 32})

		# regex vyrazy riadkov suboru, druhy parameter je prefix funkcie ?_riadok ktora ma
		# dany riadok spracovat
		self.reg_riadky = (
			(re.compile(r"""(&L +)?P (?P<y>\d+(\.\d\d|\.\d)?) (?P<x>\d+(\.\d\d|\.\d)?)(?P<info>.*)"""), 'p'),
			(re.compile(r"""(L|C|R) (?P<y>\d+(\.\d\d|\.\d)?) (?P<x>\d+(\.\d\d|\.\d)?)(?P<info>.*)"""), 'lc'),
			#obluky sa spracuvavaju ako ciary
			#(re.compile(r"""(R|NR) (?P<y>\d+(\.\d\d|\.\d)?) (?P<x>\d+(\.\d\d|\.\d)?)"""), 'r'),
			(re.compile(r"""(NL|NC|NR) (?P<y>\d+(\.\d\d|\.\d)?) (?P<x>\d+(\.\d\d|\.\d)?)(?P<info>.*)"""), 'n'),
			(re.compile(r"""&A (?P<nazov>.{1,6})=(?P<hodnota>.{1,40})"""), 'a'),
			(re.compile(r"""&T (?P<y>\d+(\.\d\d|\.\d)?) (?P<x>\d+(\.\d\d|\.\d)?) ['"](?P<text>.+)['"](?P<info>.*)"""), 't'),
			(re.compile(r"""&O (?P<nazov>.{1,8}) (?P<id>\d+)"""), 'o'),
			(re.compile(r"""&*"""), 'vynechaj')
		)

		self.buffer_obluku = None # obluk sa sklada z troch bodov, tu sa ulozi druhy, kym sa nenacita treti
		self.prvy = False # priznak ci uz bol spracovany prvy objekt
		self.index = 0

	def spracuj_info(self, text):
		info = {}
		for param in text.split():
			param = param.strip()
			if param and '=' in param:
				meno, hodnota = param.split('=', 1)
				info[meno] = hodnota
		return info

	def o_riadok(self, data):
		self.atributy_objektu['ID'] = data['id']
		self.meta['meno_objektu'] = data['nazov']

	def r_riadok(self, data):
		self.wl.rotuj(data['y'], data['x'])

	def lc_riadok(self, data):
		self.wl.kresli(data['y'], data['x'])

	def a_riadok(self, data):
		logging.debug("  Atribut %s=%s", data['nazov'], data['hodnota'])
		self.atributy_objektu[data['nazov']] = data['hodnota']

	def p_riadok(self, data):
		if self.prvy:
			self.wl.kresli(data['y'], data['x'])
			self.prvy = True
		else:
			self.wl.skoc(data['y'], data['x'])

	def n_riadok(self, data):
		self.p_riadok(data)

	def t_riadok(self, data):
		text = data['text'].decode('cp852')
		info = self.spracuj_info(data['info'])
		self.textove_elementy.append({
			'wkt': 'POINT(%.2f %.2f)' % (-float(data['y']), -float(data['x'])),
			'y': -float(data['y']),
			'x': -float(data['x']),
			'text': text,
			'info': info
		})

	def vynechaj_riadok(self, data):
		pass

	def pridaj_riadok(self, riadok):
		"""Funkcia prechaza regularnymi vyrazmi a hlada ktory zapasuje, vysledok sa preda
		na spracovanie definovanej funkcie"""
		for reg, fcia in self.reg_riadky:
			m = reg.match(riadok)
			if m:
				if fcia == "lc":
					self.lc_riadok(m.groupdict())
				elif fcia == "p":
					self.p_riadok(m.groupdict())
				elif fcia == "n":
					self.n_riadok(m.groupdict())
				elif fcia == "o":
					self.o_riadok(m.groupdict())
				elif fcia == "r":
					self.r_riadok(m.groupdict())
				elif fcia == "a":
					self.a_riadok(m.groupdict())
				elif fcia == "t":
					self.t_riadok(m.groupdict())
				return
		raise NepodporovanaVeta

	def spolocne_atributy(self):
		pass

	def geometricke_objekty(self):
		pass

	def data(self):
		atributy = {
			'o_id': self.atributy_objektu['ID'],
			'ku': int(self.atributy_suboru.get('KU')),
			'stav_k': self.atributy_suboru.get('AKTUAL'),
			'subor': self.atributy_suboru.get('SUBOR')
		}
		atributy.update(self.spolocne_atributy() or {})
		return {
			'meta': self.meta,
			'atributy': atributy,
			'geometricke_objekty': self.geometricke_objekty(),
			'textove_elementy': self.textove_elementy,
			'spravy': self.spravy
		}


class Bodovy_objekt(Objekt):
	def __init__(self, atributy_suboru):
		super(Bodovy_objekt, self).__init__(atributy_suboru)
		self.meta['wkb_typ'] = ogr.wkbPoint
		self.body = []

	def p_riadok(self, data):
		wkt = 'POINT(%.2f %.2f)' % (-float(data['y']), -float(data['x']))
		info = self.spracuj_info(data['info'])
		self.body.append( {'wkt': wkt, 'text': '', 'info': info} )

	def lc_riadok(self, data):
		raise NepodporovanaVeta

class Liniovy_objekt(Objekt):
	polia = (
		{'nazov': 'g_k', 'typ': 'OFTInteger'},
	)
	aktual_k = None

	def __init__(self, atributy_suboru):
		super(Liniovy_objekt, self).__init__(atributy_suboru)
		self.meta['wkb_typ'] = ogr.wkbMultiLineString
		self.linie = []
		self.wl = WktLinia(self)

	def _ukonci_liniu(self):
		wkt = self.wl.wkt()
		if wkt:
			objekt = {'wkt': wkt, 'atributy': {'g_k': int(self.aktual_k)}}
			self.linie.append(objekt)
		self.wl = WktLinia(self)

	def p_riadok(self, data):
		info = self.spracuj_info(data['info'])
		k = info.get('K', '1')
		if self.aktual_k is not None and k != self.aktual_k:
			self._ukonci_liniu()
			super(Liniovy_objekt, self).p_riadok(data)
		else:
			super(Liniovy_objekt, self).p_riadok(data)
		self.aktual_k = k

	def lc_riadok(self, data):
		super(Liniovy_objekt, self).lc_riadok(data)
		info = self.spracuj_info(data['info'])
		k = info.get('K', self.aktual_k)
		if self.aktual_k is not None and k != self.aktual_k:
			self._ukonci_liniu()
			# zacne novu liniu v tom istom bode (ale s inou hodnotou K)
			super(Liniovy_objekt, self).lc_riadok(data)
		self.aktual_k = k

	def n_riadok(self, data):
		info = self.spracuj_info(data['info'])
		k = info.get('K', self.aktual_k)
		if self.aktual_k is not None and k != self.aktual_k:
			self._ukonci_liniu()
			super(Liniovy_objekt, self).n_riadok(data)
		else:
			super(Liniovy_objekt, self).n_riadok(data)
		self.aktual_k = k

	def geometricke_objekty(self):
		if self.wl is not None:
			self._ukonci_liniu()
			self.wl = None
		return self.linie

class Plosny_objekt(Objekt):
	def __init__(self, atributy_suboru):
		super(Plosny_objekt, self).__init__(atributy_suboru)
		self.meta['wkb_typ'] = ogr.wkbMultiPolygon

		self.wl = WktPolygon(self)

	def geometricke_objekty(self):
		wkt = self.wl.wkt()
		return [{'wkt': wkt}] if wkt else []

	def data(self):
		data = super(Plosny_objekt, self).data()
		data["pocet_uzatvoreni"] = self.wl.pocet_uzatvoreni
		return data

class Parcela(Plosny_objekt):
	polia = Plosny_objekt.polia + (
		{'nazov': 'parckey', 'typ': 'OFTString', 'sirka': 17},
		{'nazov': 'parcela', 'typ': 'OFTString', 'sirka': 40},
		{'nazov': 'kmen', 'typ': 'OFTInteger'},
		{'nazov': 'podlomenie', 'typ': 'OFTInteger'},
		{'nazov': 't', 'typ': 'OFTString', 'sirka': 254},
	)

	def spracuj_cislo_parcely(self, hodnota):
		# uprava specialneho pripadu cisla parcely bez desatinnej casti
		if '.' not in hodnota:
			hodnota = hodnota + '.0'

		# ak cislo parcely obsahuje aj cislo povodneho uzemia
		if '-' in hodnota:
			cpu, pcis = hodnota.split('-')
			cpu = int(cpu)
		else:
			cpu = 0
			pcis = hodnota

		kmen, podlomenie = map(int, pcis.split('.'))
		lomeny_tvar = "%s/%d" % (kmen, podlomenie) if podlomenie > 0 else "%s" % kmen
		if cpu:
			lomeny_tvar = "%s-%s" % (cpu, lomeny_tvar)
		parckey = '%06d%02d%05d%03d0' % (int(self.atributy_suboru['KU']), cpu, kmen, podlomenie)
		return {
			'kmen': kmen,
			'podlomenie': podlomenie,
			'parcela': lomeny_tvar,
			'parckey': parckey
		}

	def spracuj_textovy_atribut(self):
		textove_data = []
		for textovy_element in self.textove_elementy:
			h = float(textovy_element['info'].get('H', 1))
			u = float(textovy_element['info'].get('U', 0))
			textove_data.append('%.2f;%.2f;%.1f;%.2f' % (textovy_element['y'], textovy_element['x'], h, u))
		return '|'.join(textove_data)

class KLADPAR(Parcela):
	nazov_vrstvy = 'kn_kladpar'
	polia = Parcela.polia + (
		{'nazov': 'g_s', 'typ': 'OFTString', 'sirka': 254},
	)
	symboly = ''

	def p_riadok(self, data):
		if 'S' not in data['info']:
			super(KLADPAR, self).p_riadok(data)
		else:
			y = -float(data['y'])
			x = -float(data['x'])
			info = self.spracuj_info(data['info'])
			s = int(info.get('S', 1))
			u = float(info.get('U', 0))
			m = float(info.get('M', 1))
			symbol = '%.2f;%.2f;%d;%.2f;%.2f' % (y, x, s, u, m)
			self.symboly = self.symboly + '|' + symbol if self.symboly else symbol

	def spolocne_atributy(self):
		atributy = {
			'g_s': self.symboly
		}

		logging.debug("  Konvertujem PARCIS: %s", self.atributy_objektu.get('PARCIS'))
		try:
			atributy.update(self.spracuj_cislo_parcely(self.atributy_objektu['PARCIS']))
		except:
			logging.error("Zly PARCIS %s v objekte %s", self.atributy_objektu.get('PARCIS'), self.atributy_objektu['ID'])

		atributy['t'] = self.spracuj_textovy_atribut()
		return atributy

class UOV(Parcela):
	nazov_vrstvy = 'kn_uov'

	def spolocne_atributy(self):
		atributy = {}

		logging.debug("  Konvertujem UO: %s", self.atributy_objektu.get('UO'))
		try:
			atributy.update(self.spracuj_cislo_parcely(self.atributy_objektu['UO']))
		except:
			logging.error("Zly UO %s v objekte %s", self.atributy_objektu.get('UO'), self.atributy_objektu['ID'])

		atributy['t'] = self.spracuj_textovy_atribut()
		return atributy


class KATUZ(Liniovy_objekt):
	nazov_vrstvy = 'kn_katuz'
	polia = (
		{'nazov': 'ku_cislo', 'typ': 'OFTInteger', 'sirka': 6},
		{'nazov': 'ku_nazov', 'typ': 'OFTString', 'sirka': 40},
		{'nazov': 'g_k', 'typ': 'OFTInteger'},
	)

	def spolocne_atributy(self):
		atributy = {'ku_nazov': self.atributy_objektu.get('HKU', '')}
		try:
			atributy['ku_cislo'] = int(self.atributy_objektu['KU'])
		except:
			atributy['ku_cislo'] = 0
		return atributy

class ZAPPAR(Liniovy_objekt):
	nazov_vrstvy = 'kn_zappar'

class LINIE(Liniovy_objekt):
	nazov_vrstvy = 'kn_linie'


class POPIS(Bodovy_objekt):
	nazov_vrstvy = 'kn_popis'
	polia = Bodovy_objekt.polia + (
		{'nazov': 'text', 'typ': 'OFTString', 'sirka': 40},
		{'nazov': 'g_k', 'typ': 'OFTInteger'},
		{'nazov': 'g_u', 'typ': 'OFTReal', 'presnost': 2},
		{'nazov': 'g_h', 'typ': 'OFTReal', 'presnost': 1},
		{'nazov': 'g_f', 'typ': 'OFTInteger'},
		{'nazov': 'g_d', 'typ': 'OFTInteger'}
	)

	def geometricke_objekty(self):
		objekty = []
		for textovy_element in self.textove_elementy:
			info = textovy_element['info']
			objekty.append({
				'wkt': textovy_element['wkt'],
				'atributy': {
					'text': textovy_element['text'],
					'g_k': int(info.get('K', 1)),
					'g_u': float(info.get('U', 0)),
					'g_h': float(info.get('H', 2)),
					'g_f': int(info.get('F', 1)),
					'g_d': int(info.get('D', 1)),
				}
			})
		return objekty

class ZNACKY(Bodovy_objekt):
	nazov_vrstvy = 'kn_znacky'
	polia = Plosny_objekt.polia + (
		{'nazov': 'g_s', 'typ': 'OFTInteger'},
		{'nazov': 'g_u', 'typ': 'OFTReal', 'presnost': 2},
		{'nazov': 'g_m', 'typ': 'OFTReal', 'presnost': 1}
	)

	def p_riadok(self, data):
		super(ZNACKY, self).p_riadok(data)

	def geometricke_objekty(self):
		objekty = []
		for bod in self.body:
			objekty.append({
				'wkt': bod['wkt'],
				'atributy': {
					'g_s': int(bod['info'].get('S', 1)),
					'g_u': float(bod['info'].get('U', 0)),
					'g_m': float(bod['info'].get('M', 1)),
				}
			})
		return objekty


class ZUOB(Plosny_objekt):
	nazov_vrstvy = 'kn_zuob'

class BPEJ(Plosny_objekt):
	nazov_vrstvy = 'kn_bpej'
	polia = Plosny_objekt.polia + (
		{'nazov': 'bj', 'typ': 'OFTString', 'sirka': 40},
	)

	def spolocne_atributy(self):
		return {'bj': self.atributy_objektu.get('BJ', '')}


#----------- Ine objekty --------------

class INE_BODY(Bodovy_objekt):

	polia = Bodovy_objekt.polia + (
		{'nazov': 'text', 'typ': 'OFTString', 'sirka': 80},
	)

	def __init__(self, atributy_suboru, nazov_vrstvy):
		self.nazov_vrstvy = 'kn_%s' % nazov_vrstvy.lower()
		super(INE_BODY, self).__init__(atributy_suboru)

	def geometricke_objekty(self):
		objekty = []
		for bod in self.body+self.textove_elementy:
			objekty.append({
				'wkt': bod['wkt'],
				'atributy': {
					'text': bod['text'],
				}
			})
		return objekty

class INE_LINIE(Liniovy_objekt):
	def __init__(self, atributy_suboru, nazov_vrstvy):
		self.nazov_vrstvy = 'kn_%s' % nazov_vrstvy.lower()
		super(INE_LINIE, self).__init__(atributy_suboru)

#------------ Triedy zapisujuce vrstvy ---------------

class Vystup_vrstvy(object):
	"""Zakladna trieda ktora sa stara o vytvorenie a zapis objektov jednej vrstvy do vystupneho suboru"""
	datovy_zdroj = None

	def __init__(self, nazov_suboru, driver, geom_type, nazov_vrstvy, nastavenia_vrstvy = None, kodovanie = 'utf-8'):
		self.driver = driver
		self.kodovanie = kodovanie
		driver = ogr.GetDriverByName(driver)
		self.datovy_zdroj = driver.CreateDataSource(nazov_suboru, options = nastavenia_vrstvy)
		self.vrstva = self.datovy_zdroj.CreateLayer(nazov_vrstvy, geom_type = geom_type, options = nastavenia_vrstvy)
		self.polia = None

	def __del__(self):
		self.zatvor()

	def zatvor(self):
		if self.datovy_zdroj:
			self.datovy_zdroj.Destroy()
			self.datovy_zdroj = None

	def priprav_polia(self, meta_polia):
		for pole in meta_polia:
			# pridanie vynimky pre ESRI Shapefile format, ktory nepodporuje datovy typ datetime
			if self.driver == 'ESRI Shapefile' and pole['typ'] == 'OFTDateTime':
				pole['typ'] = 'OFTDate'
			typ = 'ogr.%s' % pole['typ']

			fd = ogr.FieldDefn(pole['nazov'], eval(typ))
			if 'sirka' in pole:
				fd.SetWidth(pole['sirka'])
			if 'presnost' in pole:
				fd.SetPrecision(pole['presnost'])
			self.vrstva.CreateField(fd)

		self.polia = True

	def features(self, data):
		for objekt in data['geometricke_objekty']:
			f = ogr.Feature(feature_def=self.vrstva.GetLayerDefn())

			atributy = data['atributy']
			atributy.update(objekt.get('atributy', {}))
			for atribut, hodnota in atributy.iteritems():
				if isinstance(hodnota, tuple):
					# datetime hodnota
					f.SetField(atribut, *hodnota)
				else:
					if isinstance(hodnota, basestring):
						f.SetField(atribut, hodnota.encode(self.kodovanie))
					else:
						f.SetField(atribut, hodnota)

			wkt = objekt['wkt']
			geom = ogr.CreateGeometryFromWkt(wkt)
			if geom.GetGeometryType() == ogr.wkbLineString:
				geom =  ogr.ForceToMultiLineString(geom)
			elif geom.GetGeometryType() == ogr.wkbPolygon:
				geom =  ogr.ForceToMultiPolygon(geom)
			f.SetGeometryDirectly(geom)
			yield f

	def uloz(self, data):
		if not self.polia:
			self.priprav_polia(data['meta']['polia'])
		for feature in self.features(data):
			self.vrstva.CreateFeature(feature)
			feature.Destroy()


class CAD_vystup(object):
	def __init__(self, vystup):
		self.vystup = vystup

	def uloz(self, data):
		# Ak objekt obsahuje textove elementy (vety), potom sa pre kazdy element vytvori bodovy objekt na danej
		# pozicii s hodnotou textu ulozenou v atribute 'Text'. Vsetky povodne atributy sa zmazu, resp. neulozia.
		data['atributy'] = {}
		data['meta']['polia'] = []
		for geom_objekt in data['geometricke_objekty']:
			geom_objekt['atributy'] = {}

		for f in self.vystup.features(data):
			f.SetStyleString('PEN(c:#FF0000)')
			self.vystup.vrstva.CreateFeature(f)
			f.Destroy()
		if data.get('textove_elementy'):
			for text_element in data['textove_elementy']:
				f = ogr.Feature(feature_def=self.vystup.vrstva.GetLayerDefn())
				geom = ogr.CreateGeometryFromWkt(text_element['wkt'])
				f.SetGeometry(geom)
				f.SetField('Text', text_element['text'].encode(self.vystup.kodovanie))
				f.SetStyleString('LABEL(f:"Times New Roman",s:10pt)')
				self.vystup.vrstva.CreateFeature(f)
				f.Destroy()


class Zapisovac:
	def __init__(self, nazov, cesta, format, nazvy_vrstiev = None, nastavenia_vrstvy = None):
		self.__zapisovac_vrstvy = {}
		self.__nazov = nazov
		self.__cesta = os.path.join(cesta, nazov)
		self.__format = format
		self.__nazvy_vrstiev = nazvy_vrstiev
		self.__nastavenia_vrstvy = nastavenia_vrstvy

	def uloz(self, data):
		os.environ['PG_USE_COPY'] = 'YES' if self.__format == 'sql-copy' else 'NO'
		vrstva = data['meta']['nazov_vrstvy']
		if not self.__zapisovac_vrstvy.has_key(vrstva.lower()):
			if self.__nazvy_vrstiev and vrstva in self.__nazvy_vrstiev:
				nazov_vystupnej_vrstvy = self.__nazvy_vrstiev[vrstva].lower()
			else:
				nazov_vystupnej_vrstvy = vrstva.lower()

			kodovanie = 'utf-8'
			nastavenia_vrstvy = {}
			if self.__format == 'shp':
				driver = 'ESRI Shapefile'
				kodovanie = 'cp1250'
				# Shapefile driver vygeneruje nazvy suborov podla nazvov vrstiev
				nazov_suboru = ''
				nazov_vystupnej_vrstvy = '%s_%s' % (self.__nazov, nazov_vystupnej_vrstvy)
			elif self.__format == 'dgn':
				driver = 'DGN'
				nazov_suboru = '%s_%s.dgn' % (self.__nazov, nazov_vystupnej_vrstvy)
				nastavenia_vrstvy = {
					'ORIGIN': '-393839,-1232725,0', # centeroid of Slovak rep.
					'MASTER_UNIT_NAME': 'm'
				}
			else:
				driver = 'PGDump'
				nazov_suboru = '%s_%s.sql' % (self.__nazov, nazov_vystupnej_vrstvy)
				nastavenia_vrstvy = {
					'CREATE_TABLE': 'OFF',
					'DROP_TABLE': 'OFF',
					'GEOMETRY_NAME': 'geom',
					'SRID': '5514',
					'SCHEMA': 'kataster',
					'CREATE_SCHEMA': 'OFF',
				}
			if self.__nastavenia_vrstvy:
				nastavenia_vrstvy.update(dict(item.split("=") for item in self.__nastavenia_vrstvy))
			nastavenia_vrstvy = ["%s=%s" % (key, value) for key, value in nastavenia_vrstvy.iteritems()]

			nazov_suboru = os.path.join(self.__cesta, nazov_suboru)
			cesta = os.path.dirname(nazov_suboru)
			if not os.path.exists(cesta):
				os.makedirs(cesta)

			vystup = Vystup_vrstvy(nazov_suboru, driver, data['meta']['wkb_typ'],
					nazov_vystupnej_vrstvy, nastavenia_vrstvy=nastavenia_vrstvy, kodovanie=kodovanie)
			if self.__format == 'dgn':
				vystup = CAD_vystup(vystup)
			self.__zapisovac_vrstvy[vrstva.lower()] = vystup

		self.__zapisovac_vrstvy[vrstva.lower()].uloz(data)

#------------ Pomocne triedy ---------------

class HBod(object):
	"""Trieda v ktorej sa ukladaju suradnice konkretneho bodu"""
	def __init__(self, bx, by):
		self.__str = "-%s -%s" % (bx, by)
		self.x = float(bx)
		self.y = float(by)

	def __str__(self):
		return self.__str

	def __repr__(self):
		return self.__str

	def __eq__(self, iny_bod):
		"""Funcia porovnava dva HBody ak sa pouziju vo vyraze HBod1 == HBod2"""
		return isinstance(iny_bod, HBod) and self.x == iny_bod.x and self.y == iny_bod.y

class HLinia(object):
	"""Trieda v ktorej sa ukladaju HBod-y ktore tvoria konkretnu liniu alebo polygon"""
	def __init__(self, i):
		self.__index = i
		self.__body = []
		self.pocet_bodov = 0
		self.zatvorena = False

	def __preved_na_str(self):
		str_body = []
		for bod in self.__body:
			str_body.append(str(bod))
		return ', '.join(str_body)

	def __str__(self):
		return self.__preved_na_str()

	def __repr__(self):
		return self.__preved_na_str()

	def __getitem__(self, index):
		return self.__body[index]

	def pridaj(self, bx, by):
		if self.zatvorena:
			self.zatvorena = False
		self.__body.append(HBod(bx, by))
		self.pocet_bodov += 1
		if self.pocet_bodov > 1 and self.__body[0] == self.__body[-1]:
			self.zatvorena = True

	def porovnaj(self, bx, by):
		"""Funcia porovna suradnice so suradnicami posledneho bodu v linii. Vyuziva sa to pri
		hladani ciary, na ktorej mam pokracovat, pri odskokoch na inu ciaru"""
		bod = HBod(bx, by)

		if self.__body[-1] == bod:
			return self.__index
		else:
			return False

	def zatvor(self):
		"""Funkcia zatvori polygon, cize prida na koniec rovnaky bod ako je na zaciatku"""
		self.__body.append(self.__body[0])
		self.pocet_bodov += 1
		self.zatvorena = True


class WktGeneric(object):
	"""Toto je jadro celeho skriptu, objekt ktory sa stara o spravne vygenerovanie WKT z vlozenej
	postupnosti bodov"""
	_wkt = None

	def __init__(self, objekt):
		self.__index = False
		self.__index_indexov = 1
		self.__buffer_obluku = None
		self._ciary = {}
		self._objekt = objekt
		self.spravy = []
		self.pocet_uzatvoreni = 0

	def __oprav_uhol(self, uhol): # ak je uhol mimo interval 0 - 360 tak ho opravi
		if uhol >= 360:
			return uhol -360
		elif uhol < 0:
			return 360 + uhol
		else:
			return uhol

	def kresli(self, bx, by):
		if self.__buffer_obluku:
			logging.warn("Nespravna definicia obluku v objekte %s", self._objekt.atributy_objektu['ID'])
			self.__buffer_obluku = None

		if not self._ciary.has_key(self.__index_indexov):
			self.__index = self.__index_indexov
			self._ciary[self.__index] = HLinia(self.__index)

		self._ciary[self.__index].pridaj(bx, by)

	def skoc(self, bx, by):
		index = False
		for i in self._ciary.keys():
			index = self._ciary[i].porovnaj(bx, by)
			if index:
				break

		if self.__buffer_obluku:
			logging.warn("Nespravna definicia obluku v objekte %s", self._objekt.atributy_objektu['ID'])
			self.__buffer_obluku = None

		if index:
			self.__index = index
		else:
			self.__index_indexov += 1
			self.kresli(bx, by)

	def rotuj(self, bx, by):
		if self.__buffer_obluku:
			koncovy_bod = HBod(bx, by)

			x1 = self._ciary[self.__index][-1].x
			y1 = self._ciary[self.__index][-1].y
			x2 = self.__buffer_obluku.x
			y2 = self.__buffer_obluku.y
			x3 = koncovy_bod.x
			y3 = koncovy_bod.y

			try:
				k = (x1-x3) / (x1-x2)
				ys = (((x1**2)+(y1**2))-((x3**2)+(y3**2))-(k*(((x1**2)+(y1**2))-((x2**2)+(y2**2))))) / (2*((y1-y3)-(k*(y1-y2))))
				xs = (((x1**2)-(x2**2))+((y1-ys)**2)-((y2-ys)**2)) / (2*(x1-x2))
			except ZeroDivisionError:
				ys = (y1+y2) / 2
				try:
					xs = (((x2**2)-(x3**2))+((y2-ys)**2)-((y3-ys)**2)) / (2*(x2-x3))
				except ZeroDivisionError:
					if ((x1 == x2) and (x1 == x3)) and (y1 == y3):
						xs = x1
						if y1 > y2:
							ys = ((y1 - y2) / 2) + y2
						else:
							ys = ((y2 - y1) / 2) + y1
					elif ((y1 == y2) and (y1 == y3)) and (x1 == x3):
						ys = y1
						if x1 > x2:
							xs = ((x1 - x2) / 2) + x2
						else:
							ys = ((x2 - x1) / 2) + x1
					else:
						logging.warn("Nespravna definicia obluku v objekte %s", self._objekt.atributy_objektu['ID'])
						self._ciary[self.__index].pridaj("%.2f" % x3, "%.2f" % y3)
						return False

			zaciatok = Bod([xs, ys],[x1, y1])
			prechod = Bod([xs, ys],[x2, y2])
			koniec = Bod([xs, ys],[x3, y3])

			# uhly jednotlivych bodov
			za = zaciatok.argument() 
			pa = prechod.argument()
			ka = koniec.argument()

			# uhly posunute tak aby bol zaciatok na nule
			opa = self.__oprav_uhol(pa - za)
			oka = self.__oprav_uhol(ka - za)

			ret = ''
			if opa < oka: # ak je uhol prechodoveho bodu mensi ako uhol koncoveho tak v smere hodinovych ruciciek
				oza = 0
				while oza < oka:
				#	ret = ret + ',' + zaciatok.get()
					zaciatok.otoc()
					rx, ry = zaciatok.get()
					self._ciary[self.__index].pridaj(rx, ry)
					oza = oza + 5 # cislo je uhol o ktory sa otacam
			else:
				oza = 360
				while oza > oka:
				#	ret = ret + ',' + zaciatok.get()
					zaciatok.otoc(False)
					rx, ry = zaciatok.get()
					self._ciary[self.__index].pridaj(rx, ry)
					oza = oza - 5
			
			self._ciary[self.__index].pridaj("%.2f" % x3, "%.2f" % y3)
			self.__buffer_obluku = None

		else: 
			self.__buffer_obluku = HBod(bx, by)

	def __str__(self):
		if self._wkt is None:
			self._wkt = self._preved_na_wkt()
		return self._wkt

	def __repr__(self):
		return self.__str__()

	def wkt(self):
		return self.__str__()

class WktLinia(WktGeneric):

	def _preved_na_wkt(self):
		ciary = self._ciary
		str_ciary = []
		for i in ciary.keys():
			if ciary[i].pocet_bodov > 1:
				str_ciary.append(str(ciary[i]))
			else:
				logging.warn("Mazem (%s) v objekte %s", ciary[i], self._objekt.atributy_objektu['ID'])
		if str_ciary:
			return "MULTILINESTRING((%s))" % '),('.join(str_ciary)
		else:
			logging.warn("Neplatna linia v objekte %s", self._objekt.atributy_objektu['ID'])
			return ""


class WktPolygon(WktGeneric):

	def _preved_na_wkt(self):
		ciary = self._ciary
		str_ciary = []
		for i in ciary.keys():
			if ciary[i].pocet_bodov > 3:
				if not ciary[i].zatvorena:
					ciary[i].zatvor()
					self.pocet_uzatvoreni += 1
					logging.warn("Zatvaram polygon v objekte %s", self._objekt.atributy_objektu['ID'])
				str_ciary.append(str(ciary[i]))
			else:
				if ciary[i].pocet_bodov > 1:
					logging.warn("Mazem (%s) v objekte %s", ciary[i], self._objekt.atributy_objektu['ID'])

		if str_ciary:
			return "POLYGON((%s))" % '),('.join(str_ciary)
		else:
			logging.warn("Neplatny polygon v objekte %s", self._objekt.atributy_objektu['ID'])
			return ""

class Bod:
	""" Trieda ktora dokaze uchovat 2d bod a rotovat o okolo zadaneho stredu """
	def __init__(self, s, b):
		self.__xs = s[0] # suradnice stredu
		self.__ys = s[1]
		self.__x = b[0] - self.__xs
		self.__y = b[1] - self.__ys

	def __modul(self):
		return math.sqrt(self.__x**2 + self.__y**2)

	def __nu2cu(self, uhol): # zmeni normalny uhol (0,90,180,270) na uhol triedy (0, -90, -180, 90)
		if uhol < 180:
			return -uhol
		else:
			return 360 - uhol

	def __cu2nu(self, uhol):
		if uhol <= 0:
			return -uhol
		else:
			return 360 - uhol

	def argument(self):
		return self.__cu2nu(math.degrees(math.atan2(self.__y, self.__x)))

	def __zmen_argument(self, uhol):
		mod = self.__modul()
		self.__x = mod * math.cos(math.radians(uhol))
		self.__y = mod * math.sin(math.radians(uhol))

	def get(self):
		return ("%.2f" % round(self.__x + self.__xs,2), "%.2f" % round(self.__y + self.__ys,2))

	def otoc(self, smer_otocenia=True): # smer_otocenia: True = v smere hodinovych ruciciek
		if smer_otocenia:
			uhol_otocenia = 5
		else:
			uhol_otocenia = -5
		novy_uhol = self.argument() + uhol_otocenia
		if novy_uhol >= 360:
			novy_uhol = novy_uhol - 360
		elif novy_uhol < 0:
			novy_uhol = 360 + novy_uhol
		self.__zmen_argument(self.__nu2cu(novy_uhol))


# vim: set ts=4 sts=4 sw=4 noet:
