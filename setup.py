#!/usr/bin/env python

import os
from distutils.core import setup

classifiers = [
	'Development Status :: 4 - Beta',
	'Intended Audience :: Developers',
	'Intended Audience :: Science/Research',
	'Operating System :: OS Independent',
	'Programming Language :: Python',
	'Topic :: Scientific/Engineering :: GIS',
	'License :: OSI Approved :: GNU General Public License version 2.0 (GPL-2)',
]


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
package_root_dir = 'katastertools'
packages, package_data = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
	os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk(package_root_dir):
	# Ignore dirnames that start with '.'
	for i, dirname in enumerate(dirnames):
		if dirname.startswith('.'): del dirnames[i]
	if '__init__.py' in filenames:
		pkg = dirpath.replace(os.path.sep, '.')
		if os.path.altsep:
			pkg = pkg.replace(os.path.altsep, '.')
		packages.append(pkg)
	elif filenames:
		prefix = dirpath[len(package_root_dir)+1:] # Strip "package_root_dir/" from path
		for f in filenames:
			package_data.append(os.path.join(prefix, f))

# setup
setup(
	name='kataster-import',
	version="%s.%s.%s" % __import__('katastertools').VERSION[:3],
	description='Import tools for Slovak cadastral data',
	long_description="This package is dedicated for processing cadastral data in exchange formats created by "
		"The Geodesy, Cartography and Cadastre Authority of Slovak republic."
		"There is no reason to use it for other purposes.",

	author='Peter Hyben, Ivan Mincik, Marcel Dancak',
	author_email='peter.hyben@hugis.eu, ivan.mincik@gmail.com, dancakm@gmail.com',

	license='GNU GPL-2',
	url='https://github.com/imincik/kataster-import',

	package_dir={'katastertools': 'katastertools'},
	packages=packages,
	package_data={'katastertools': package_data},
	scripts=['kt-vgi2shp',
		'kt-import_dbf2',
		'kt-import_fuvi',
		'kt-vycisti_fuvi',
		'kt-vytvor_db',
		'kt-sql'],

	classifiers=classifiers
)


# vim: set ts=4 sts=4 sw=4 noet:
