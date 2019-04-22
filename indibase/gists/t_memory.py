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
import sys
import logging
import time
# external packages
import PyQt5
import PyQt5.QtWidgets
from pympler import muppy, summary
# local import
from indibase import qtIndiBase
from indibase import indiXML


class IndiPythonBase(PyQt5.QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.client = qtIndiBase.Client(host='astrocomp.fritz.box')
        self.client.signals.serverConnected.connect(self.serverConnected)
        self.client.signals.newProperty.connect(self.connectDevice)
        self.client.signals.newNumber.connect(self.showStat)
        self.client.signals.defNumber.connect(self.showStat)
        self.startCommunication()

    def initUI(self):
        qbtn = PyQt5.QtWidgets.QPushButton('Quit', self)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 10)
        qbtn.clicked.connect(self.quit)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Test IndiBaseClient')
        self.show()

    def startCommunication(self):
        """
        startCommunication adds a device on the watch list of the server.

        :return: success of reconnecting to server
        """

        suc = self.client.connectServer()
        return suc

    def connectDevice(self, deviceName, propertyName):
        """
        connectDevice is called when a new property is received and checks it against
        property CONNECTION. if this is there, we could check the connection state of
        a given device

        :param deviceName:
        :param propertyName:
        :return: success if device could connect
        """
        if propertyName != 'CONNECTION':
            return False

        suc = False
        if deviceName == 'MBox':
            suc = self.client.connectDevice(deviceName=deviceName)
        return suc

    def serverConnected(self):
        suc = self.client.watchDevice('MBox')
        return suc

    def showStat(self, deviceName, deviceProperty):
        all_objects = muppy.get_objects()
        sum1 = summary.summarize(all_objects)
        summary.print_(sum1)

    def quit(self):
        self.close()
        PyQt5.QtWidgets.QApplication.instance().quit()


app = PyQt5.QtWidgets.QApplication(sys.argv)
work = IndiPythonBase()

rc = app.exec_()
sys.exit(rc)
