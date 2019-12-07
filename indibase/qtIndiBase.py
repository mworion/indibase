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
# Python  v3.7.4

#
# Michael Würtenberger
# (c) 2019
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


class WorkerSignals(PyQt5.QtCore.QObject):
    """
    The WorkerSignals class offers a list of signals to be used and instantiated by the
    Worker class to get signals for error, finished and result to be transferred to the
    caller back
    """

    __all__ = ['WorkerSignals']

    finished = PyQt5.QtCore.pyqtSignal()
    error = PyQt5.QtCore.pyqtSignal(object)
    result = PyQt5.QtCore.pyqtSignal(object)


class Worker(PyQt5.QtCore.QRunnable):
    """
    The Worker class offers a generic interface to allow any function to be executed as a
    thread in an threadpool
    """

    __all__ = ['Worker',
               'run']

    logger = logging.getLogger(__name__)

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        # the worker signal must not be a class variable, but instance otherwise
        # we get trouble when having multiple threads running
        self.signals = WorkerSignals()

    def run(self):
        """
        runs an arbitrary methods with it's parameters and catches the result

        :return: nothing, but sends results and status as signals
        """

        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.logger.error(f'error: {e}')
            self.signals.error.emit(e)
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


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
    SOCKET_TIMEOUT = 1
    # cycle timer for checking server up
    CYCLE_SERVER_UP = 1000

    def __init__(self,
                 host=None,
                 ):
        super().__init__(host=host)

        self.threadpool = PyQt5.QtCore.QThreadPool()
        self.mutexServerUp = PyQt5.QtCore.QMutex()

        self.timerServerUp = PyQt5.QtCore.QTimer()
        self.timerServerUp.setSingleShot(False)
        self.timerServerUp.timeout.connect(self.cycleCheckServerUp)

    def checkServerUp(self):
        """
        checkServerUp polls the host/port of the mount computer and set the state and
        signals for the status accordingly.

        :return: nothing
        """

        socket.setdefaulttimeout(self.SOCKET_TIMEOUT)
        client = socket.socket()
        client.settimeout(self.SOCKET_TIMEOUT)
        try:
            client.connect(self.host)
        except Exception:
            client.close()
            suc = False
        else:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            suc = True

        return suc

    def checkServerUpResult(self, result):
        """

        :param result:
        :return:
        """

        if result and not self.connected:
            suc = self.connectServer()
            self.logger.info(f'Connect to server, result: {suc}')
            return suc
        elif not result and self.connected:
            suc = self.disconnectServer()
            self.logger.info(f'Disconnect from server, result: {suc}')
            return suc
        else:
            return False

    def errorCycleCheckServerUp(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """
        self.logger.error(f'Cycle error: {e}')

    def clearCycleCheckServerUp(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """

        self.mutexServerUp.unlock()

    def cycleCheckServerUp(self):
        """
        cycleCheckServerUp prepares the worker thread and the signals for getting the settings
        data.

        :return: nothing
        """

        if not self.mutexServerUp.tryLock():
            return
        worker = Worker(self.checkServerUp)
        worker.signals.finished.connect(self.clearCycleCheckServerUp)
        worker.signals.result.connect(self.checkServerUpResult)
        worker.signals.error.connect(self.errorCycleCheckServerUp)
        self.threadpool.start(worker)

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
