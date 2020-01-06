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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
# local imports


class CustomLogger(logging.LoggerAdapter):
    """
    The MWLog class offers an adapter interface interface to allow a more customized
    logging functionality.

    """

    __all__ = ['MWLog',
               'run']

    def process(self, msg, kwargs):
        """
        if you want to prepend or append the contextual information to the message string,
        you just need to subclass LoggerAdapter and override process() to do what you need.
        that's what i am doing here.

        :param msg:
        :param kwargs:
        :return:
        """

        return f'{msg}', kwargs
