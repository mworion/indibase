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
    newProperty = PyQt5.QtCore.pyqtSignal(str, str)
    removeProperty = PyQt5.QtCore.pyqtSignal(str, str)
    newBLOB = PyQt5.QtCore.pyqtSignal(str, str)
    newSwitch = PyQt5.QtCore.pyqtSignal(str, str)
    newNumber = PyQt5.QtCore.pyqtSignal(str, str)
    newText = PyQt5.QtCore.pyqtSignal(str, str)
    newLight = PyQt5.QtCore.pyqtSignal(str, str)
    newMessage = PyQt5.QtCore.pyqtSignal(str, str)
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
        _property = getattr(self, propertyName)
        if _property['propertyType'] not in ['defNumberVector',
                                             'setNumberVector']:
            self.logger.error('Property: {0} is not Number'.format(_property['propertyType']))
            return
        propList = _property['property']
        retDict = {}
        for prop in propList:
            retDict[prop] = propList[prop]['value']
        return retDict

    def getText(self, propertyName):
        _property = getattr(self, propertyName)
        if _property['propertyType'] not in ['defTextVector',
                                             'setTextVector']:
            self.logger.error('Property: {0} is not Text'.format(_property['propertyType']))
            return
        propList = _property['property']
        retDict = {}
        for prop in propList:
            retDict[prop] = propList[prop]['value']
        return retDict

    def getSwitch(self, propertyName):
        _property = getattr(self, propertyName)
        if _property['propertyType'] not in ['defSwitchVector',
                                             'setSwitchVector']:
            self.logger.error('Property: {0} is not Switch'.format(_property['propertyType']))
            return
        propList = _property['property']
        retDict = {}
        for prop in propList:
            retDict[prop] = propList[prop]['value']
        return retDict

    def getLight(self, propertyName):
        _property = getattr(self, propertyName)
        if _property['propertyType'] not in ['defLightVector',
                                             'setLightVector']:
            self.logger.error('Property: {0} is not Light'.format(_property['propertyType']))
            return
        propList = _property['property']
        retDict = {}
        for prop in propList:
            retDict[prop] = propList[prop]['value']
        return retDict

    def getBlob(self, propertyName):
        return


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

    def setServer(self, host='', port=7624):
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
        val = self.sendCmd(cmd)
        return val

    def connectServer(self):
        """
        Part of BASE CLIENT API of EKOS
        connect starts the link to the indi server.

        :return: success
        """

        if self.connected:
            self.signals.serverConnected.emit()
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

        if not self.connected:
            return False
        if not deviceName:
            return False
        val = self.sendNewSwitch(deviceName=deviceName,
                                 propertyName='CONNECTION',
                                 elementName='CONNECT',
                                 )
        return val

    def disconnectDevice(self, deviceName):
        """
        Part of BASE CLIENT API of EKOS

        :return: success
        """

        if not self.connected:
            return False
        if not deviceName:
            return False
        if deviceName not in self.devices:
            return False
        val = self.sendNewSwitch(deviceName=deviceName,
                                 propertyName='CONNECTION',
                                 elementName='DISCONNECT',
                                 )
        return val

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
        val = self.sendCmd(cmd)
        return val

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
        val = self.sendCmd(cmd)
        return val

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
        val = self.sendCmd(cmd)
        return val

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
        :return: success of sending
        """

        if self.verbose:
            print(indiCommand.toXML())
        if self.connected:
            number = self.socket.write(indiCommand.toXML() + b'\n')
            self.socket.flush()
            if number > 0:
                return True
            else:
                return False
        else:
            return False

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

    def _dispatchCmd(self, chunk):
        """
        _dispatchCmd parses the incoming indi XL data and builds up a dictionary which
        holds all the data.

        :param chunk: raw indi XML element
        :return: success if it could be parsed
        """

        chunk = indiXML.parseETree(chunk)
        if self.verbose:
            print(chunk)
        if 'device' not in chunk.attr:
            self.logger.error('No device in chunk: {0}'.format(chunk))
            return False

        deviceName = chunk.attr['device']
        if deviceName not in self.devices:
            self.devices[deviceName] = Device(deviceName)
            self.signals.newDevice.emit(deviceName)
        rawDev = self.devices[deviceName]

        # deleting properties from devices
        if isinstance(chunk, indiXML.DelProperty):
            if deviceName not in self.devices:
                return False
            if 'name' not in chunk.attr:
                return False
            delProperty = chunk.attr['name']
            if hasattr(rawDev, delProperty):
                delattr(rawDev, delProperty)
                self.signals.removeProperty.emit(deviceName, delProperty)

        if isinstance(chunk, (indiXML.SetBLOBVector,
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
            if 'name' not in chunk.attr:
                return False
            _property = chunk.attr['name']

            if not hasattr(rawDev, _property):
                # set property (SetSwitchVector etc.)
                setattr(rawDev, _property, {})
            # shortening for readability
            prop = rawDev.__dict__[_property]
            # add property type
            prop['propertyType'] = chunk.etype
            # add attributes to _property
            for vecAttr in chunk.attr:
                prop[vecAttr] = chunk.attr.get(vecAttr)
            # adding subspace for atomic elements (text, switch, etc)
            prop['property'] = {}
            # shortening again
            element = prop['property']
            # now running through all atomic elements
            for elt in chunk.elt_list:
                # first the name
                name = elt.attr['name']
                element[name] = {}
                element[name]['elementType'] = elt.etype
                if not isinstance(elt, indiXML.DefBLOB):
                    if elt.etype in ['defNumber',
                                     'setNumber',
                                     'oneNumber']:
                        element[name]['value'] = float(elt.getValue())
                    elif elt.etype in ['defSwitch',
                                       'oneSwitch',
                                       'setSwitch']:
                        element[name]['value'] = (elt.getValue() == 'On')
                    else:
                        element[name]['value'] = elt.getValue()
                # now all attributes of element
                for attr in elt.attr:
                    element[name][attr] = elt.attr[attr]
            # do signals
            if isinstance(chunk, (indiXML.DefBLOBVector,
                                  indiXML.DefSwitchVector,
                                  indiXML.DefTextVector,
                                  indiXML.DefLightVector,
                                  indiXML.DefNumberVector,
                                  )
                          ):
                self.signals.newProperty.emit(deviceName, _property)
            elif isinstance(chunk, indiXML.SetBLOBVector):
                self.signals.newBLOB.emit(deviceName, _property)
            elif isinstance(chunk, indiXML.SetSwitchVector):
                self.signals.newSwitch.emit(deviceName, _property)
            elif isinstance(chunk, indiXML.SetNumberVector):
                self.signals.newNumber.emit(deviceName, _property)
            elif isinstance(chunk, indiXML.SetTextVector):
                self.signals.newText.emit(deviceName, _property)
            elif isinstance(chunk, indiXML.SetLightVector):
                self.signals.newLight.emit(deviceName, _property)
            elif isinstance(chunk, indiXML.SetMessageVector):
                self.signals.newMessage.emit(deviceName, _property)
        else:
            pass
            # print(elem.attr)

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
