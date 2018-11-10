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
# local import
from indibase import indiBase
from indibase import indiXML


class IndiPythonBase(PyQt5.QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()

        self.client = client
        self.initUI()

        self.runTest()

    def initUI(self):
        qbtn = PyQt5.QtWidgets.QPushButton('Quit', self)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 10)
        qbtn.clicked.connect(self.quit)

        self.conn = PyQt5.QtWidgets.QPushButton('Connect', self)
        self.conn.move(50, 40)
        self.coord = PyQt5.QtWidgets.QPushButton('Coordinates', self)
        self.coord.move(50, 70)

        self.client.signals.newSwitch.connect(self.showStat)
        self.client.signals.newNumber.connect(self.showExposure)
        self.client.signals.newNumber.connect(self.showCoordinates)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Test IndiBaseClient')
        self.show()

    def runTest(self):
        self.client.connectServer()
        self.client.setVerbose(False)
        self.client.watchDevice('CCD Simulator')
        self.client.watchDevice('Telescope Simulator')
        self.client.setBlobMode('Also', 'CCD Simulator')
        time.sleep(0.5)
        vega = {'RA': (279.23473479 * 24.0) / 360.0, 'DEC': +38.78368896}
        self.client.sendNewNumber('Telescope Simulator',
                                  'EQUATORIAL_EOD_COORD',
                                  value=vega)

        self.client.disconnectServer()

    def showStat(self, deviceName, deviceProperty):
        if deviceName != 'CCD Simulator':
            return
        if deviceProperty != 'CONNECTION':
            return
        ccdDevice = self.client.getDevice('CCD Simulator')
        connSwitch = ccdDevice.getSwitch('CONNECTION')
        if connSwitch['CONNECT']:
            self.conn.setStyleSheet('background-color: green;')
        else:
            self.conn.setStyleSheet('background-color: red;')

    def showExposure(self, deviceName, deviceProperty):
        if deviceName != 'CCD Simulator':
            return
        if deviceProperty != 'CCD_EXPOSURE':
            return
        ccdDevice = self.client.getDevice('CCD Simulator')
        number = ccdDevice.getNumber('CCD_EXPOSURE')
        print('Exposing for {0:3.1f} seconds'.format(number['CCD_EXPOSURE_VALUE']))

    def showCoordinates(self, deviceName, deviceProperty):
        if deviceName != 'Telescope Simulator':
            return
        if deviceProperty != 'EQUATORIAL_EOD_COORD':
            return
        telDevice = self.client.getDevice('Telescope Simulator')
        number = telDevice.getNumber('EQUATORIAL_EOD_COORD')
        text = 'RA:{0:3.5f}, DEC:{1:3.5f}'.format(number['RA'], number['DEC'])
        self.coord.setText(text)

    def quit(self):
        self.close()
        PyQt5.QtWidgets.QApplication.instance().quit()

app = PyQt5.QtWidgets.QApplication(sys.argv)
client = indiBase.Client('192.168.2.57')
widget = IndiPythonBase(client)
rc = app.exec_()
sys.exit(rc)
