import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='scenariogeneration', 
    version='0.7.4',
    license='MPL-2.0',
    author='Mikael Andersson, Irene Natale, Andreas Tingberg',
    author_email='andmika@gmail.com',
    description='Generation of OpenSCENARIO and OpenDRIVE xml files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pyoscx/scenariogeneration',
    download_url = 'https://github.com/pyoscx/scenariogeneration/archive/v0.7.4.tar.gz',
    packages=setuptools.find_packages(),
    keywords = ['OpenDRIVE','OpenSCENARIO','xml'],
    install_requires=[
        'numpy',
        'scipy',
        'pyclothoids',
        'attrs'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
