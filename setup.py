from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in intozu_custom/__init__.py
from intozu_custom import __version__ as version

setup(
	name="intozu_custom",
	version=version,
	description="Intozu Custom App",
	author="Stackerbee",
	author_email="info@stackerbee.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
