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


class TestQtIndi(PyQt5.QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()

        self.client = client
        self.initUI()

    def initUI(self):
        qbtn = PyQt5.QtWidgets.QPushButton('Quit', self)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 10)
        conn = PyQt5.QtWidgets.QPushButton('Connect', self)
        conn.move(50, 40)
        disconn = PyQt5.QtWidgets.QPushButton('Disconnect', self)
        disconn.move(50, 70)

        qbtn.clicked.connect(self.quit)
        conn.clicked.connect(self.connectDev)
        disconn.clicked.connect(self.disconnectDev)

        self.client.signals.newSwitch.connect(self.showStat)
        self.client.signals.newNumber.connect(self.showExposure)
        self.client.signals.newNumber.connect(self.showCoordinates)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Test IndiBaseClient')
        self.show()

    def connectDev(self):
        self.client.connectDevice('CCD Simulator')

    def disconnectDev(self):
        self.client.disconnectDevice('CCD Simulator')

    def showStat(self, name):
        print(name)
        ccdDevice = self.client.getDevice('CCD Simulator')
        connSwitch = ccdDevice.getSwitch('CONNECTION')
        print(connSwitch)

    def showExposure(self, name):
        if name != 'CCD_EXPOSURE':
            return
        ccdDevice = self.client.getDevice('CCD Simulator')
        number = ccdDevice.getNumber('CCD_EXPOSURE')
        print('Exposing for {0:3.1f} seconds'.format(number['CCD_EXPOSURE_VALUE']))

    def showCoordinates(self, name):
        if name != 'EQUATORIAL_EOD_COORD':
            return
        telDevice = self.client.getDevice('Telescope Simulator')
        number = telDevice.getNumber('EQUATORIAL_EOD_COORD')
        print('Telescope coordinates: RA:{0:3.5f}, DEC:{1:3.5f}'
              .format(number['RA'], number['DEC']))

    def quit(self):
        self.close()
        PyQt5.QtWidgets.QApplication.instance().quit()


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s.%(msecs)03d]'
                           '[%(levelname)7s]'
                           '[%(filename)15s]'
                           '[%(lineno)5s]'
                           '[%(funcName)25s]'
                           '[%(threadName)10s]'
                           ' > %(message)s',
                    handlers=[logging.FileHandler('test_indi.log')],
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )

app = PyQt5.QtWidgets.QApplication(sys.argv)
client = indiBase.Client('192.168.2.57')
widget = TestQtIndi(client)
client.connectServer()
client.setVerbose(False)
client.watchDevice('CCD Simulator')
client.watchDevice('Telescope Simulator')
client.setBlobMode('Also', 'CCD Simulator')
rc = app.exec_()
client.disconnectServer()
sys.exit(rc)
