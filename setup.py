from setuptools import find_packages, setup


with open("README.md") as f:
	readme = f.read()


setup(
	name="jtq_custom",
	version="0.0.1",
	description="JTQ Custom ERP customizations",
	long_description=readme,
	long_description_content_type="text/markdown",
	author="JTQ",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=[],
)
