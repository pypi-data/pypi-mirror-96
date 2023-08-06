from setuptools import setup, find_packages
import re

VERSIONFILE="asysocks/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


setup(
	# Application name:
	name="asysocks",

	# Version number (initial):
	version=verstr,

	# Application author details:
	author="Tamas Jos",
	author_email="info@skelsecprojects.com",

	# Packages
	packages=find_packages(),

	# Include additional files into the package
	include_package_data=True,


	# Details
	url="https://github.com/skelsec/asysocks",

	zip_safe = True,
	#
	# license="LICENSE.txt",
	description="",
	long_description="",

	# long_description=open("README.txt").read(),
	python_requires='>=3.6',
	classifiers=(
		"Programming Language :: Python :: 3.6",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	),
	install_requires=[
	],
	entry_points={
		'console_scripts': [
			'asysockstunnel = asysocks.examples.sockstunnel:main',
			'asysockssec = asysocks.examples.sockssec:main',
			'asysocksbrute = asysocks.examples.socksbrute:main',
			'asysocksportscan = asysocks.examples.socksportscan:main',
			'asysocksproxy = asysocks.examples.socksproxy:main',
		],
	}
)