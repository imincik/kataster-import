#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert data from ESRI Shapefile to text format containing object ID and WKT.

USAGE: shp2wkt.py <input-file>

	input-file		absolute path to input ESRI Shapefile
"""

import os
import sys

from osgeo import ogr


try:
	infile = sys.argv[1]
except IndexError:
	print __doc__
	sys.exit(0)


sdriver = ogr.GetDriverByName('ESRI Shapefile')

sds = sdriver.Open(infile, 0)
if sds is None:
	print 'Could not open file'
	sys.exit(1)

outfile = '%s.txt' % os.path.splitext(infile)[0]
print 'Processing file {0} to {1} ...'.format(infile, outfile)

slayer = sds.GetLayer()
sfeature = slayer.GetNextFeature()

count_features = 0
with open(outfile, 'w') as f:
	while sfeature:
		count_features += 1
		print 'Feature #{0}\r'.format(sfeature.GetFID()),

		geom = sfeature.GetGeometryRef()
		line = '{0};{1}\n'.format(sfeature.GetField('o_id'), geom.ExportToWkt())
		f.write(line)

		# destroy
		sfeature.Destroy()
		sfeature = slayer.GetNextFeature()

print
print 'Done. Total Features: {0}'.format(count_features)

sds.Destroy()


# vim: set ts=4 sts=4 sw=4 noet:
