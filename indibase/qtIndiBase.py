############################################################
# -*- coding: utf-8 -*-
#
# INDIBASE
#
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import socket
# external packages
import PyQt5.QtCore
# local import
import indibase.indiBase


class Client(indibase.indiBase.Client):
    """
    Client implements an INDI Base Client for INDI servers. it rely on PyQt5 and it's
    signalling scheme. there might be not all capabilities implemented right now. all
    the data, properties and attributes are stored in a the devices dict.
    The reading and parsing of the XML data is done in a streaming way, so for xml the
    xml.parse.feed() mechanism is used.

        >>> indiClient = Client(
        >>>                     host=host
        >>>                     )

    """

    __all__ = ['Client',
               ]

    logger = logging.getLogger(__name__)

    # socket timeout for testing if server is present
    SOCKET_TIMEOUT = 0.5
    # cycle timer for checking server up
    CYCLE_SERVER_UP = 1000

    def __init__(self,
                 host=None,
                 ):
        super().__init__(host=host,
                         )

        self.timerServerUp = PyQt5.QtCore.QTimer()
        self.timerServerUp.setSingleShot(False)
        self.timerServerUp.timeout.connect(self.checkServerUp)

    def checkServerUp(self):
        """
        checkServerUp polls the host/port of the mount computer and set the state and
        signals for the status accordingly.

        :return: nothing
        """

        if self.connected:
            return

        client = socket.socket()
        client.settimeout(self.SOCKET_TIMEOUT)
        try:
            client.connect(self.host)
        except Exception:
            pass
        else:
            self.connectServer()
        finally:
            client.close()

    def startTimers(self):
        """
        startTimers enables the cyclic timers for polling necessary mount data.

        :return: nothing
        """

        self.timerServerUp.start(self.CYCLE_SERVER_UP)

    def stopTimers(self):
        """
        stopTimers disables the cyclic timers for polling necessary mount data.


        :return: nothing
        """

        self.timerServerUp.stop()
