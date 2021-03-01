import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scenariogeneration", 
    version="0.2.0",
    author="Mikael Andersson, Irene Natale",
    author_email="andmika@gmail.com, irene.natale@volvocars.com",
    description="Generation of OpenSCENARIO and OpenDRIVE xml files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyoscx/scenariogeneration",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MPL-2.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)