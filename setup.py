# from distutils.core import setup
from setuptools import setup
from indibase.indiBase import Client

setup(
    name='indibase',
    version=Client.version,
    packages=[
        'indibase',
    ],
    python_requires='>=3.7.2',
    install_requires=[
        'PyQt5>=5.13',
        'numpy>=1.16.4',
    ],
    url='https://github.com/mworion/indibase',
    license='APL 2.0',
    author='mw',
    author_email='michael@wuertenberger.org',
    description='indi base client in python based on qt',
)
