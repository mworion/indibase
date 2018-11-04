# from distutils.core import setup
from setuptools import setup
import indibase.indiBase
import platform

setup(
    name='indibase',
    version=indibase.indiBase.version,
    packages=[
        'indibase',
    ],
    python_requires='~=3.6.5',
    install_requires=[
        'PyQt5==5.11.3',
        'numpy==1.15.3',
    ]
    ,
    url='https://github.com/mworion/indibase',
    license='APL 2.0',
    author='mw',
    author_email='michael@wuertenberger.org',
    description='indi base client in python based on qt',
)