############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
from setuptools import setup

indibase_version = '0.105'

setup(
    name='indibase',
    version=indibase_version,
    packages=[
        'indibase',
    ],
    python_requires='>=3.7.4',
    setup_requires=[
        'PyQt5>=5.13',
        'numpy==1.17',
    ],
    install_requires=[
        'PyQt5>=5.13',
        'numpy==1.17',
    ],
    url='https://github.com/mworion/indibase',
    license='APL 2.0',
    author='mw',
    author_email='michael@wuertenberger.org',
    description='indi base client in python based on qt',
    zip_safe=True,
)
