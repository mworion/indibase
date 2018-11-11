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
from PyQt5.QtTest import QTest
# local import
from indibase import indiBase
from indibase import indiXML


class IndiPythonBase(PyQt5.QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()

        self.client = client
        self.expose = None
        self.ccdDevice = None
        self.initUI()
        self.runTest()

    def initUI(self):
        qbtn = PyQt5.QtWidgets.QPushButton('Quit', self)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 10)
        qbtn.clicked.connect(self.quit)

        self.expose = PyQt5.QtWidgets.QPushButton('Expose', self)
        self.expose.move(50, 40)
        self.expose.clicked.connect(self.doExpose)

        self.client.signals.newDevice.connect(self.showDevice)
        self.client.signals.newNumber.connect(self.showExposure)
        self.client.signals.newBLOB.connect(self.getBlob)

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
        self.client.setBlobMode('Also', 'CCD Simulator')

    def showDevice(self, deviceName):
        if deviceName == 'CCD Simulator':
            self.ccdDevice = self.client.getDevice('CCD Simulator')
            print('new device: ', deviceName)

    def doExpose(self):
        number = self.ccdDevice.getNumber('CCD_EXPOSURE')
        number['CCD_EXPOSURE_VALUE'] = 1
        suc = self.client.sendNewNumber(deviceName='CCD Simulator',
                                        propertyName='CCD_EXPOSURE',
                                        elements=number,
                                        )

    def showExposure(self, deviceName, deviceProperty):
        if deviceName != 'CCD Simulator':
            return
        if deviceProperty != 'CCD_EXPOSURE':
            return
        number = self.ccdDevice.getNumber('CCD_EXPOSURE')
        print('Exposing for {0:3.5f} seconds'.format(number['CCD_EXPOSURE_VALUE']))

    def getBlob(self, deviceName, deviceProperty):
        print('got blob ')
        if deviceName == 'CCD Simulator':
            blob = self.ccdDevice.getBlob(propertyName=deviceProperty)
            """
            imageHDU = pyfits.HDUList.fromstring(blob['value'])
            imageHDU.writeto(self.imagePath, overwrite=True)
            """
    def quit(self):
        self.client.disconnectServer()
        self.close()
        PyQt5.QtWidgets.QApplication.instance().quit()


app = PyQt5.QtWidgets.QApplication(sys.argv)
client = indiBase.Client('astro-mount.fritz.box')
widget = IndiPythonBase(client)
rc = app.exec_()
sys.exit(rc)
