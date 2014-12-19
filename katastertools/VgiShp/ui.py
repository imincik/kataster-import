#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import argparse

from katastertools import VgiShp


class Volby(object):
	"""Trieda ktora spracuje prepinace z prikazoveho riadku."""

	def __init__(self):
		self.__atributy = {'subor': False, 'vystupny_adresar': '.', 'debug': False}
		parser = argparse.ArgumentParser(
			description="""Import tool for spatial data created by The Geodesy, Cartography and Cadastre Authority of Slovak republic.

				Supported formats:
				* input : VGI
				* output: SQL (INSERT or COPY format), ESRI Shapefile, Microstation DGN v7

				Import can be performed for specified layers only or for all detected layers, if no layers given.""".replace('\t', ''),
			formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=60, width=120)
		)
		parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
		parser.add_argument(type=file, metavar='FILE', dest='vstupny_subor', help='input file')
		parser.add_argument('-f', '--format', default='sql-copy', help='output format',
				choices=['sql', 'sql-copy', 'shp', 'dgn'])
		parser.add_argument('-c', '--config', default='',
				help='layer configuration parameters (depends on output format). Example: "CREATE_TABLE=OFF SCHEMA=gis')
		parser.add_argument('-o', default=os.curdir, metavar='DIRECTORY', dest='vystupny_adresar', help='output directory')
		# vygeneruj argumenty pre zname vrstvy
		zname_vrstvy = {
			'b': ('BPEJ', u'hranice areálov bonitovaných pôdno-ekologických jednotiek'),
			't': ('KATUZ', u'hranica katastrálneho územia'),
			'k': ('KLADPAR', u'hranice a čísla parciel registra C, symboly druhov pozemkov'),
			'l': ('LINIE', u'ďalšie prvky polohopisu (inžinierske siete, hranica CHKO ...)'),
			'p': ('POPIS', u'sídelné a nesídelné názvy'),
			'u': ('UOV', u'hranice a čísla parciel registra E'),
			'r': ('ZAPPAR', u'hranica druhov pozemkov, ktoré nie sú v KLADPAR'),
			'n': ('ZNACKY', u'mapové značky okrem značiek druhov pozemkov'),
			'z': ('ZUOB', u'hranica zastavaného územia obce'),
		}
		for param, vrstva_info in zname_vrstvy.iteritems():
			parser.add_argument('-%s' % param, nargs='?', const=vrstva_info[0],
					metavar=vrstva_info[0], help="import '%s' layer (%s)" % vrstva_info)

		parser.add_argument('-i', dest='spracuj_nezname_vrstvy', action='store_true',
				help='import also unknown layers')
		args = parser.parse_args()

		self.debug = args.verbose
		self.subor = args.vstupny_subor.name
		self.vystupny_adresar = args.vystupny_adresar
		self.format = args.format
		self.nastavenia_vrstvy = filter(None, args.config.split(' '))
		self.spracuj_nezname_vrstvy = args.spracuj_nezname_vrstvy

		# zoznam zadanych vrstiev ako dictionary s polozkami {VRSTVA: NAZOV_VYSTUPNEJ_VRSTVY}
		vrstvy = {zname_vrstvy[arg][0]: value for arg, value in vars(args).iteritems() if arg in zname_vrstvy and value}
		# v pripade ze nie je zvolena ziadna vrstva, nastavi spracovanie vsetkych
		if not vrstvy and not args.spracuj_nezname_vrstvy:
			vrstvy = {vrstva_info[0]: vrstva_info[0] for vrstva_info in zname_vrstvy.itervalues()}
			self.spracuj_nezname_vrstvy = True
		self.vrstvy = vrstvy


# vim: set ts=4 sts=4 sw=4 noet:
