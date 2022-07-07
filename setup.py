from setuptools import setup, find_packages

setup(
	name='controle_manip',
	version='0.0.1',
	packages=find_packages(),
	install_requires=[
		'numpy >= 1.19.2',
		'comtypes >= 1.1.7',
		'pyvisa >=  1.11.3',
	]
)
