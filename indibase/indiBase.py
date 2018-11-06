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
import base64
# external packages
import PyQt5.QtCore
import PyQt5.QtNetwork
import xml.etree.ElementTree
# local import
from indibase import indiXML


class INDISignals(PyQt5.QtCore.QObject):
    """
    The INDISignals class offers a list of signals to be used and instantiated by the
    IndiBase class to get signals for indi events.
    """

    __all__ = ['INDISignals']
    version = '0.1'

    newDevice = PyQt5.QtCore.pyqtSignal(str)
    removeDevice = PyQt5.QtCore.pyqtSignal(str)
    newProperty = PyQt5.QtCore.pyqtSignal(str)
    removeProperty = PyQt5.QtCore.pyqtSignal(str)
    newBLOB = PyQt5.QtCore.pyqtSignal(str)
    newSwitch = PyQt5.QtCore.pyqtSignal(str)
    newNumber = PyQt5.QtCore.pyqtSignal(str)
    newText = PyQt5.QtCore.pyqtSignal(str)
    newLight = PyQt5.QtCore.pyqtSignal(str)
    newMessage = PyQt5.QtCore.pyqtSignal(str)
    serverConnected = PyQt5.QtCore.pyqtSignal()
    serverDisconnected = PyQt5.QtCore.pyqtSignal()


class Device(object):
    """
    Device implements an INDI Device. it rely on PyQt5 and it's signalling scheme.
    there might be not all capabilities implemented right now. all the data, properties
    and attributes are stored in a the devices dict.

        >>> indiDevice = Device(
        >>>                     name=''
        >>>                     )

    """

    __all__ = ['Device',
               'version',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    def __init__(self,
                 name='',
                 ):
        super().__init__()

        self.name = name

    def getNumber(self, propertyName):
        return getattr(self, propertyName)

    def getText(self, propertyName):
        return getattr(self, propertyName)

    def getSwitch(self, propertyName):
        return getattr(self, propertyName)

    def getLight(self, propertyName):
        return getattr(self, propertyName)


class Client(PyQt5.QtCore.QObject):
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
               'version',
               'setServer',
               'watchDevice',
               'connectServer',
               'disconnectServer',
               'isServerConnected',
               'connectDevice',
               'disconnectDevice',
               'getDevice',
               'getDevices',
               'setBlobMode',
               'getBlobMode',
               'getHost',
               'getPort',
               'sendNewText',
               'sendNewNumber',
               'sendNewSwitch',
               'startBlob',
               'sendOneBlob',
               'finishBlob',
               'setVerbose',
               'isVerbose',
               'setConnectionTimeout'
               'sendCmd',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # INDI device types
    GENERAL_INTERFACE = 0
    TELESCOPE_INTERFACE = (1 << 0)
    CCD_INTERFACE = (1 << 1)
    GUIDER_INTERFACE = (1 << 2)
    FOCUSER_INTERFACE = (1 << 3)
    FILTER_INTERFACE = (1 << 4)
    DOME_INTERFACE = (1 << 5)
    GPS_INTERFACE = (1 << 6)
    WEATHER_INTERFACE = (1 << 7)
    AO_INTERFACE = (1 << 8)
    DUSTCAP_INTERFACE = (1 << 9)
    LIGHTBOX_INTERFACE = (1 << 10)
    DETECTOR_INTERFACE = (1 << 11)
    AUX_INTERFACE = (1 << 15)

    # default port indi servers
    DEFAULT_PORT = 7624
    # timeout for client to server
    CONNECTION_TIMEOUT = 2000

    def __init__(self,
                 host=None,
                 ):
        super().__init__()
        # parameters
        self.host = host
        # instance variables
        self.signals = INDISignals()
        self.connected = False
        self.verbose = False
        self.blobMode = 'Never'
        self.devices = dict()
        self.curDepth = 0
        # tcp handling
        self.socket = PyQt5.QtNetwork.QTcpSocket()
        self.socket.readyRead.connect(self._handleReadyRead)
        self.socket.error.connect(self._handleError)
        # XML parser
        self.parser = xml.etree.ElementTree.XMLPullParser(['start', 'end'])
        self.parser.feed('<root>')
        # clear the event queue of parser
        for _, _ in self.parser.read_events():
            pass

    @property
    def host(self):
        return self._host

    def checkFormat(self, value):
        # checking format
        if not value:
            self.logger.error('wrong host value: {0}'.format(value))
            return None
        if not isinstance(value, (tuple, str)):
            self.logger.error('wrong host value: {0}'.format(value))
            return None
        # now we got the right format
        if isinstance(value, str):
            value = (value, self.DEFAULT_PORT)
        return value

    @host.setter
    def host(self, value):
        value = self.checkFormat(value)
        self._host = value

    def setServer(self, host='', port=0):
        """
        Part of BASE CLIENT API of EKOS
        setServer sets the server address of the indi server

        :param host: host name as string
        :param port: port as int
        :return: success for test purpose
        """
        self.host = (host, port)
        return True

    def watchDevice(self, deviceName=''):
        """
        Part of BASE CLIENT API of EKOS
        adds a device to the watchlist. if the device name is empty, all traffic for all
        devices will be watched and therefore received

        :param deviceName: device name
        :return: success for test purpose
        """
        cmd = indiXML.clientGetProperties(indi_attr={'version': '1.7',
                                                     'device': deviceName})
        self.sendCmd(cmd)
        return True

    def connectServer(self):
        """
        Part of BASE CLIENT API of EKOS
        connect starts the link to the indi server.

        :return: success
        """

        if self.connected:
            return True
        self.socket.connectToHost(*self._host)
        if not self.socket.waitForConnected(self.CONNECTION_TIMEOUT):
            self.connected = False
            return False
        self.connected = True
        self.signals.serverConnected.emit()
        return True

    def disconnectServer(self):
        """
        Part of BASE CLIENT API of EKOS
        disconnect drops the connection to the indi server

        :return: success
        """

        if not self.connected:
            return True
        self.connected = False
        self.socket.close()
        self._clearDevices()
        self.signals.serverDisconnected.emit()
        return True

    def isServerConnected(self):
        """
        Part of BASE CLIENT API of EKOS

        :return: true if server connected
        """

        return self.connected

    def connectDevice(self, deviceName):
        """
        Part of BASE CLIENT API of EKOS

        :return: success
        """

        self.sendNewSwitch(deviceName=deviceName,
                           propertyName='CONNECTION',
                           elementName='CONNECT',
                           )
        return True

    def disconnectDevice(self, deviceName):
        """
        Part of BASE CLIENT API of EKOS

        :return: success
        """

        self.sendNewSwitch(deviceName=deviceName,
                           propertyName='CONNECTION',
                           elementName='DISCONNECT',
                           )
        return True

    def getDevice(self, deviceName):
        """
        getDevice collects all the data of the given device

        :param deviceName: name of device
        :return: dict with data of that give device
        """

        return self.devices.get(deviceName, None)

    def getDevices(self, driverInterface):
        """
        getDevices generates a list of devices, which are from type of the given
        driver interface type.

        :param driverInterface: binary value of driver interface type
        :return: list of knows devices of this type
        """

        deviceList = list()
        for deviceName in self.devices:
            if self._getDriverInterface(deviceName) & driverInterface:
                deviceList.append(deviceName)
        return deviceList

    def setBlobMode(self, blobHandling='Never', deviceName='', propertyName=''):
        """
        Part of BASE CLIENT API of EKOS

        :param blobHandling:
        :param deviceName:
        :param propertyName:
        :return: true if server connected
        """

        cmd = indiXML.enableBLOB(blobHandling,
                                 indi_attr={'name': propertyName,
                                            'device': deviceName})
        self.blobMode = blobHandling
        self.sendCmd(cmd)
        return True

    def getBlobMode(self, deviceName='', propertyName=None):
        """
        Part of BASE CLIENT API of EKOS

        :param deviceName:
        :param propertyName:
        :return: true if server connected
        """

        pass

    def getHost(self):
        """
        Part of BASE CLIENT API of EKOS

        :return: host name as str
        """
        return self._host[0]

    def getPort(self):
        """
        Part of BASE CLIENT API of EKOS

        :return: port number as int
        """
        return self._host[1]

    def sendNewText(self, deviceName='', propertyName='', elementName='', text=''):
        """
        Part of BASE CLIENT API of EKOS

        :param deviceName:
        :param propertyName:
        :param elementName:
        :param text:
        :return: success for test
        """
        cmd = indiXML.newTextVector([indiXML.oneText(text,
                                                     indi_attr={'name': elementName})
                                     ],
                                    indi_attr={'name': propertyName,
                                               'device': deviceName})
        self.sendCmd(cmd)
        return True

    def sendNewNumber(self, deviceName='', propertyName='', elementName='', value=0):
        """
        Part of BASE CLIENT API of EKOS

        :param deviceName:
        :param propertyName:
        :param elementName:
        :param value:
        :return: success for test
        """

        cmd = indiXML.newNumberVector([indiXML.oneNumber(value,
                                                         indi_attr={'name': elementName})
                                       ],
                                      indi_attr={'name': propertyName,
                                                 'device': deviceName})
        self.sendCmd(cmd)
        return True

    def sendNewSwitch(self, deviceName='', propertyName='', elementName=''):
        """
        Part of BASE CLIENT API of EKOS

        :param deviceName:
        :param propertyName:
        :param elementName:
        :return: success for test
        """

        cmd = indiXML.newSwitchVector([indiXML.oneSwitch('On',
                                                         indi_attr={'name': elementName})
                                       ],
                                      indi_attr={'name': propertyName,
                                                 'device': deviceName})
        self.sendCmd(cmd)
        return True

    def startBlob(self, deviceName, propertyName, timestamp):
        """
        Part of BASE CLIENT API of EKOS

        :return:
        """
        pass

    def sendOneBlob(self, blobName, blobSize, blobFormat, blobBuffer):
        """
        Part of BASE CLIENT API of EKOS

        :return:
        """
        pass

    def finishBlob(self):
        """
        Part of BASE CLIENT API of EKOS

        :return:
        """
        pass

    def setVerbose(self, status):
        """
        Part of BASE CLIENT API of EKOS

        :return:
        """

        self.verbose = bool(status)

    def isVerbose(self):
        """
        Part of BASE CLIENT API of EKOS

        :return: status of verbose
        """

        return self.verbose

    def setConnectionTimeout(self, seconds=2, microseconds=0):
        """
        Part of BASE CLIENT API of EKOS

        :return:
        """
        pass

    def sendCmd(self, indiCommand):
        """
        sendCmd take an XML indi command, converts it and sends it over the network and
        flushes the buffer

        :param indiCommand: XML command to send
        :return: nothing
        """

        if self.connected:
            self.socket.write(indiCommand.toXML() + b'\n')
            self.socket.flush()
        if self.verbose:
            print(indiCommand.toXML())

    def _getDriverInterface(self, deviceName):
        """
        _getDriverInterface look the type of the device's driver interface up and gives
        it back as binary value.

        :param deviceName: device name
        :return: binary value of type of device drivers interface
        """

        val = self.devices[deviceName].__dict__.get('DRIVER_INFO', '')
        if val:
            interface = val.get('DRIVER_INTERFACE', '')
            return int(interface)
        else:
            return 0

    def _clearDevices(self):
        """
        _clearDevices deletes all the actual knows devices and sens out the appropriate
        qt signals

        :return: success for test purpose
        """

        for deviceName in self.devices:
            self.devices[deviceName] = None
            self.signals.removeDevice.emit(deviceName)
        self.devices = {}
        return True

    def _dispatchCmd(self, elem):
        """
        _dispatchCmd parses the incoming indi XL data and builds up a dictionary which
        holds all the data.

        :param elem: raw indi XML element
        :return: success if it could be parsed
        """

        elem = indiXML.parseETree(elem)
        if self.verbose:
            print(elem)
        if 'device' not in elem.attr:
            self.logger.error('No device in elem: {0}'.format(elem))
            return False

        deviceName = elem.attr['device']
        if deviceName not in self.devices:
            self.devices[deviceName] = Device(deviceName)
            self.signals.newDevice.emit(deviceName)
        rawDev = self.devices[deviceName]

        # deleting properties from devices
        if isinstance(elem, indiXML.DelProperty):
            if device not in self.devices:
                return False
            if 'name' not in elem.attr:
                return False
            delVector = elem.attr['name']
            if delVector in rawDev.__dict__:
                del rawDev.delVector
                self.signals.removeProperty.emit(delVector)

        elif isinstance(elem, (indiXML.SetBLOBVector,
                               indiXML.SetSwitchVector,
                               indiXML.SetTextVector,
                               indiXML.SetLightVector,
                               indiXML.SetNumberVector,
                               indiXML.DefBLOBVector,
                               indiXML.DefSwitchVector,
                               indiXML.DefTextVector,
                               indiXML.DefLightVector,
                               indiXML.DefNumberVector,
                               )
                        ):
            if 'name' not in elem.attr:
                return False
            vector = elem.attr['name']
            if isinstance(elem, (indiXML.DefBLOBVector,
                                 indiXML.DefSwitchVector,
                                 indiXML.DefTextVector,
                                 indiXML.DefLightVector,
                                 indiXML.DefNumberVector,
                                 )
                          ):
                self.signals.newProperty.emit(vector)
            elif isinstance(elem, indiXML.SetBLOBVector):
                self.signals.newBLOB.emit(vector)
            elif isinstance(elem, indiXML.SetSwitchVector):
                self.signals.newSwitch.emit(vector)
            elif isinstance(elem, indiXML.SetNumberVector):
                self.signals.newNumber.emit(vector)
            elif isinstance(elem, indiXML.SetTextVector):
                self.signals.newText.emit(vector)
            elif isinstance(elem, indiXML.SetLightVector):
                self.signals.newLight.emit(vector)
            elif isinstance(elem, indiXML.SetMessageVector):
                self.signals.newMessage.emit(vector)

            if vector not in rawDev.__dict__:
                setattr(rawDev, vector, {})
            for elemAttr in elem.attr:
                rawDev.__dict__[vector][elemAttr] = elem.attr.get(elemAttr)
            if not isinstance(elem, indiXML.DefBLOBVector):
                for elt in elem.elt_list:
                    rawDev.__dict__[vector][elt.attr['name']] = elt.getValue()

    @PyQt5.QtCore.pyqtSlot()
    def _handleReadyRead(self):
        """
        _handleReadyRead gets the date in buffer signal and starts to read data from the
        network. as long as data is streaming, it feeds to the xml parser. with this
        construct you don't have to put the whole data set into the parser at once, but
        doing the work step be step.

        :return: nothing
        """

        buf = self.socket.readAll()
        self.parser.feed(buf)
        for event, elem in self.parser.read_events():
            # print(self.curDepth, event, elem.tag, elem.keys(), '\n')
            if event == 'start':
                self.curDepth += 1
            elif event == 'end':
                self.curDepth -= 1
            else:
                self.logger.error('Problem parsing event: {0}'.format(event))
            if self.curDepth > 0:
                continue
            # print('Parsed ', elem.tag)
            self._dispatchCmd(elem)

    @PyQt5.QtCore.pyqtSlot(PyQt5.QtNetwork.QAbstractSocket.SocketError)
    def _handleError(self, socketError):
        """
        _handleError log all network errors in case of problems.
        :param socketError: the error from socket library
        :return: nothing
        """

        if not self.connected:
            return
        self.logger.warning('INDI client connection fault, error: {0}'.format(socketError))
        self.socket.close()
