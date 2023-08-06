##############################################################################
#
#                        Crossbar.io FX
#     Copyright (C) Crossbar.io Technologies GmbH. All rights reserved.
#
##############################################################################

from setuptools import setup, find_packages


# read package version
with open('cfxdb/_version.py') as f:
    exec(f.read())  # defines __version__

# read package description
with open('README.rst') as f:
    docstr = f.read()


setup(
    name='cfxdb',
    version=__version__,  # noqa
    description='Crossbar.io database schemata, based on zLMDB',
    long_description=docstr,
    author='Crossbar.io Technologies GmbH',
    author_email='support@crossbario.com',
    url='https://crossbario.com',
    license='proprietary',
    classifiers=['License :: Other/Proprietary License'],
    platforms=('Any'),
    python_requires='>=3.7',
    install_requires=[
        'zlmdb>=21.2.1',
    ],
    packages=find_packages(),
    include_package_data=True,
    data_files=[('.', ['LICENSE', 'LEGAL', 'README.rst'])],
    zip_safe=True
)
