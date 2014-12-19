#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import stat

class Citac:
	"""Trieda starajuca sa o citanie vstupneho suboru. Citanie prebieha po riadkoch. Dokaze sa
	posuvat aj dozadu"""
	def __init__(self, nazov_suboru):
		try:
			mode = os.stat(nazov_suboru)[stat.ST_MODE]
			if stat.S_ISREG(mode):
				self.__subor = open(nazov_suboru, "r")
				
				if ' ' in nazov_suboru: raise MedzeraVNazveSuboru, nazov_suboru
				if self.__subor.read(2) != "&V": raise ZlyTypSuboru, nazov_suboru
			else:
				raise NieJeSubor, vstupny_subor
		except OSError, vstupny_subor:
			raise NieJeSubor, vstupny_subor
		except IOError, t:
			print t
			sys.exit(2)

		self.__subor.seek(0)
		self.__precitane_bajty = 0
		self.__dlzka_riadkov = []
		self.__precitany_riadok = self.__subor.readline()

	def __del__(self):
		self.zavriet()

	def __getitem__(self, index):
		riadok = self.__precitany_riadok
		self.__dlzka_riadkov.append(len(riadok))
		self.__precitane_bajty += len(riadok)

		if riadok == "":
			self.zavriet()
			raise ChybaKoncovaVeta
		elif riadok[:2] == '&K':
			self.zavriet()
			raise IndexError
		else:
			self.__precitany_riadok = self.__subor.readline()
			# ak veta pokracuje na dalsom riadku vo vstupnom subore, spoj ju do jedneho riadku
			if self.__precitany_riadok.startswith("\t"):
				self.__precitane_bajty += len(self.__precitany_riadok)
				self.__dlzka_riadkov[-1] += len(self.__precitany_riadok)
				riadok = riadok.rstrip() + ' ' + self.__precitany_riadok.lstrip()
				self.__precitany_riadok = self.__subor.readline()
			return riadok.strip()

	def spat(self, index): # posunie sa spat o dany pocet riadkov
		z = 0
		for x in self.__dlzka_riadkov[-index:]:
			z += x
		self.__precitane_bajty -= z
		self.__subor.seek(self.__precitane_bajty)
		self.__precitany_riadok = self.__subor.readline()

	def zavriet(self):
		if self.__subor:
			self.__subor.close()
			self.__subor = None

	def je_koniec_suboru(self):
		return self.__subor is None

class Citac_objektov:
	"""Trieda pomocou Citaca cita subor. Citanie prebieha po objektoch. V pripade potreby dokaze otocit poradie
	riadkov v objekte"""
	def __init__(self, citac):
		self.__citac = citac
		self.__koniec_suboru = False

	def __nacitaj_dalsi_objekt(self):
		self.__objekt = []
		self.__meno_vrstvy = ""
		prvy = False
		try:
			for riadok in self.__citac:
				if riadok[:2] == "&O" and not prvy:
					prvy = True
					self.__meno_vrstvy = riadok.split(' ')[1].upper()
					self.__objekt.append(riadok)
				elif riadok[:2] == "&O" and prvy:
					self.__citac.spat(1)
					return
				elif riadok[:2] == "&*":
					pass
				else:
					self.__objekt.append(riadok)
		except ChybaKoncovaVeta:
			print "E: Chyba koncova veta"
			return

	def __getitem__(self, index):
		if not self.__citac.je_koniec_suboru():
			self.__nacitaj_dalsi_objekt()
			return {
				"meno_vrstvy": self.__meno_vrstvy,
				"riadky": self.__objekt,
			}
		else:
			raise IndexError

	def posun_skoky(self):
		hranice = []
		zaciatok = False
		skok = False
		i = 0
		for riadok in self.__objekt:
			if riadok[:4] == "&L P" and "S=" not in riadok:
				if zaciatok:
					if skok:
						hranice.append((zaciatok, i))
					zaciatok = i
					skok = False
				else:
					zaciatok = i
			elif riadok[:1] == "&" and zaciatok:
				if skok:
					hranice.append((zaciatok, i))
				zaciatok = False
				skok = False
			elif riadok[:2] in ("NL", "NR", "NC"):
				skok = True
			i += 1

		if zaciatok and skok:
			hranice.append((zaciatok, i))

		if hranice:
			ret = self.__objekt[:hranice[0][0]]
			for hranica in hranice:
				o = self.__objekt[hranica[0]:hranica[1]]
				upravene_o = []
				skocil = False
				for riadok_o in o:
					if riadok_o [:2] in ("NL", "NR", "NC"):
						if skocil:
							upravene_o.append(riadok_o)
						else:
							skocil = True
							upravene_o.append(riadok_o[1:])
					else:
						if skocil:
							upravene_o.append("N%s" % riadok_o)
							skocil = False
						else:
							upravene_o.append(riadok_o)

				ret += upravene_o
			if hranice[-1][1] < len(self.__objekt):
				ret += self.__objekt[hranice[-1][1]:]
			return ret
		else:
			return self.__objekt

class NieJeSubor(Exception):
	pass

class ZlyTypSuboru(Exception):
	pass

class ChybaKoncovaVeta(Exception):
	pass

class NeplatneKU(Exception):
	pass

class MedzeraVNazveSuboru(Exception):
	pass


# vim: set ts=4 sts=4 sw=4 noet:
