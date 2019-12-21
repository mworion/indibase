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
## Licence APL2.0
#
###########################################################
# standard libraries
import sys
import logging
import time
import zlib
# external packages
import PyQt5
import PyQt5.QtWidgets
from PyQt5.QtTest import QTest
from astropy.io import fits
# local import
from indibase import indiBase
from indibase import indiXML


class IndiPythonBase(PyQt5.QtWidgets.QWidget):
    def __init__(self,):
        super().__init__()

        self.client = indiBase.Client('astro-comp.fritz.box')
        self.client2 = indiBase.Client('astro-comp.fritz.box')

        self.expose = None
        self.ccdDevice = None
        self.initUI()
        self.runTest()

    def initUI(self):
        qbtn = PyQt5.QtWidgets.QPushButton('Quit', self)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 10)
        qbtn.clicked.connect(self.quit)

        self.client.signals.newDevice.connect(self.showDevice)
        self.client.signals.deviceConnected.connect(self.showDeviceConn)
        self.client.signals.deviceDisconnected.connect(self.showDeviceDisconn)

        self.client2.signals.newDevice.connect(self.showDevice2)
        self.client2.signals.deviceConnected.connect(self.showDeviceConn2)
        self.client2.signals.deviceDisconnected.connect(self.showDeviceDisconn2)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Test IndiBaseClient')
        self.show()

    def runTest(self):
        self.client.connectServer()
        self.client.setVerbose(False)
        self.client.watchDevice('CCD Simulator')
        while not self.ccdDevice:
            QTest.qWait(100)
        self.client.connectDevice('CCD Simulator')

        self.client2.connectServer()
        self.client2.setVerbose(False)
        self.client2.watchDevice('CCD Simulator')
        while not self.ccdDevice:
            QTest.qWait(100)
        self.client2.connectDevice('CCD Simulator')

    def showDevice(self, deviceName):
        if deviceName == 'CCD Simulator':
            self.ccdDevice = self.client.getDevice('CCD Simulator')
            print('new device: ', deviceName)

    def showDeviceConn(self, deviceName):
        if deviceName == 'CCD Simulator':
            self.ccdDevice = self.client.getDevice('CCD Simulator')
            print('device connected: ', deviceName)

    def showDeviceDisconn(self, deviceName):
        if deviceName == 'CCD Simulator':
            self.ccdDevice = self.client.getDevice('CCD Simulator')
            print('device disconnected: ', deviceName)

    def showDevice2(self, deviceName):
        if deviceName == 'CCD Simulator':
            self.ccdDevice = self.client.getDevice('CCD Simulator')
            print('2 new device: ', deviceName)

    def showDeviceConn2(self, deviceName):
        if deviceName == 'CCD Simulator':
            self.ccdDevice = self.client.getDevice('CCD Simulator')
            print('2 device connected: ', deviceName)

    def showDeviceDisconn2(self, deviceName):
        if deviceName == 'CCD Simulator':
            self.ccdDevice = self.client.getDevice('CCD Simulator')
            print('2 device disconnected: ', deviceName)

    def quit(self):
        self.client.disconnectServer()
        self.client2.disconnectServer()
        self.close()
        PyQt5.QtWidgets.QApplication.instance().quit()


app = PyQt5.QtWidgets.QApplication(sys.argv)
widget = IndiPythonBase()
rc = app.exec_()
sys.exit(rc)
