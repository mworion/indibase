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
# external packages
import PyQt5.QtCore
import PyQt5.QtNetwork
import xml.etree.ElementTree as ETree
# local import
from indibase import indiXML


class INDISignals(PyQt5.QtCore.QObject):
    """
    The INDISignals class offers a list of signals to be used and instantiated by the
    IndiBase class to get signals for indi events.
    """

    __all__ = ['INDISignals']
    version = '0.9'

    newDevice = PyQt5.QtCore.pyqtSignal(str)
    removeDevice = PyQt5.QtCore.pyqtSignal(str)
    newProperty = PyQt5.QtCore.pyqtSignal(str, str)
    removeProperty = PyQt5.QtCore.pyqtSignal(str, str)

    newBLOB = PyQt5.QtCore.pyqtSignal(str, str)
    newSwitch = PyQt5.QtCore.pyqtSignal(str, str)
    newNumber = PyQt5.QtCore.pyqtSignal(str, str)
    newText = PyQt5.QtCore.pyqtSignal(str, str)
    newLight = PyQt5.QtCore.pyqtSignal(str, str)

    defBLOB = PyQt5.QtCore.pyqtSignal(str, str)
    defSwitch = PyQt5.QtCore.pyqtSignal(str, str)
    defNumber = PyQt5.QtCore.pyqtSignal(str, str)
    defText = PyQt5.QtCore.pyqtSignal(str, str)
    defLight = PyQt5.QtCore.pyqtSignal(str, str)

    newMessage = PyQt5.QtCore.pyqtSignal(str, str)
    serverConnected = PyQt5.QtCore.pyqtSignal()
    serverDisconnected = PyQt5.QtCore.pyqtSignal(object)
    deviceConnected = PyQt5.QtCore.pyqtSignal(str)
    deviceDisconnected = PyQt5.QtCore.pyqtSignal(str)


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
               'getNumber',
               'getText',
               'getSwitch',
               'getLight',
               'getBlob',
               ]

    version = '0.100'
    logger = logging.getLogger(__name__)

    def __init__(self,
                 name='',
                 ):
        super().__init__()

        self.name = name

    def getNumber(self, propertyName):
        """
        getNumber extracts from the device dictionary the relevant property subset for
        number or list of number elements. the return dict could be used later on for
        setting an element list (number vector) in indi client.

        :param propertyName: string with name
        :return: dict with number / number vector
        """

        if not hasattr(self, propertyName):
            return {}
        iProperty = getattr(self, propertyName)
        if iProperty['propertyType'] not in ['defNumberVector',
                                             'setNumberVector']:
            self.logger.error('Property: {0} is not Number'.format(iProperty['propertyType']))
            return
        elementList = iProperty['elementList']
        retDict = {}
        for prop in elementList:
            retDict[prop] = elementList[prop]['value']
        self.logger.debug('Get number: {0}'.format(retDict))
        return retDict

    def getText(self, propertyName):
        """
        getNumber extracts from the device dictionary the relevant property subset for
        text or list of text elements. the return dict could be used later on for
        setting an element list (text vector) in indi client.

        :param propertyName: string with name
        :return: dict with text or text vector
        """

        if not hasattr(self, propertyName):
            return {}
        iProperty = getattr(self, propertyName)
        if iProperty['propertyType'] not in ['defTextVector',
                                             'setTextVector']:
            self.logger.error('Property: {0} is not Text'.format(iProperty['propertyType']))
            return
        elementList = iProperty['elementList']
        retDict = {}
        for prop in elementList:
            retDict[prop] = elementList[prop]['value']
        self.logger.debug('Get text: {0}'.format(retDict))
        return retDict

    def getSwitch(self, propertyName):
        """
        getSwitch extracts from the device dictionary the relevant property subset for
        switch or list of switch elements. the return dict could be used later on for
        setting an element list (switch vector) in indi client.

        :param propertyName: string with name
        :return: dict with switch or switch vector
        """

        if not hasattr(self, propertyName):
            return {}
        iProperty = getattr(self, propertyName)
        if iProperty['propertyType'] not in ['defSwitchVector',
                                             'setSwitchVector']:
            self.logger.error('Property: {0} is not Switch'.format(iProperty['propertyType']))
            return
        elementList = iProperty['elementList']
        retDict = {}
        for prop in elementList:
            retDict[prop] = elementList[prop]['value']
        self.logger.debug('Get switch: {0}'.format(retDict))
        return retDict

    def getLight(self, propertyName):
        """
        getLight extracts from the device dictionary the relevant property subset for
        light or list of light elements. the return dict could be used later on for
        setting an element list (light vector) in indi client.

        :param propertyName: string with name
        :return: dict with light or light vector
        """

        if not hasattr(self, propertyName):
            return {}
        iProperty = getattr(self, propertyName)
        if iProperty['propertyType'] not in ['defLightVector',
                                             'setLightVector']:
            self.logger.error('Property: {0} is not Light'.format(iProperty['propertyType']))
            return
        elementList = iProperty['elementList']
        retDict = {}
        for prop in elementList:
            retDict[prop] = elementList[prop]['value']
        self.logger.debug('Get light: {0}'.format(retDict))
        return retDict

    def getBlob(self, propertyName):
        """
        getBlob extracts from the device dictionary the relevant property value for
        blob.

        :param propertyName: string with name
        :return: return blob
        """

        # blob return different, because it's binary data
        if not hasattr(self, propertyName):
            return {}
        iProperty = getattr(self, propertyName)
        if iProperty['propertyType'] not in ['defBLOBVector',
                                             'setBLOBVector']:
            self.logger.error('Property: {0} is not Blob'.format(iProperty['propertyType']))
            return
        elementList = iProperty['elementList']
        self.logger.debug('Get blob')
        return elementList[propertyName]


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
               'setConnectionTimeout',
               ]

    version = '0.104'
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
    CONNECTION_TIMEOUT = 1000

    def __init__(self,
                 host=None,
                 ):
        super().__init__()

        self.host = host

        # instance variables
        self.signals = INDISignals()
        self.connected = False
        self.blobMode = 'Never'
        self.devices = dict()
        self.curDepth = 0
        self.parser = None

        # tcp handling
        self.socket = PyQt5.QtNetwork.QTcpSocket()
        self.socket.readyRead.connect(self._handleReadyRead)
        self.socket.error.connect(self._handleError)
        self.socket.disconnected.connect(self._handleDisconnected)
        self.clearParser()

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

    def clearParser(self):
        """

        :return: success for test purpose
        """
        # XML parser
        self.parser = ETree.XMLPullParser(['start', 'end'])
        self.parser.feed('<root>')
        # clear the event queue of parser
        for _, _ in self.parser.read_events():
            pass

        return True

    def setServer(self, host='', port=7624):
        """
        Part of BASE CLIENT API of EKOS
        setServer sets the server address of the indi server

        :param host: host name as string
        :param port: port as int
        :return: success for test purpose
        """
        self.host = (host, port)
        self.connected = False
        return True

    def watchDevice(self, deviceName=''):
        """
        Part of BASE CLIENT API of EKOS
        adds a device to the watchlist. if the device name is empty, all traffic for all
        devices will be watched and therefore received

        :param deviceName: name string of INDI device
        :return: success for test purpose
        """
        cmd = indiXML.clientGetProperties(indi_attr={'version': '1.7',
                                                     'device': deviceName})
        suc = self._sendCmd(cmd)
        return suc

    def connectServer(self):
        """
        Part of BASE CLIENT API of EKOS
        connect starts the link to the indi server.

        :return: success
        """

        if self._host is None:
            return False
        if len(self._host) != 2:
            return False
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

    def clearDevices(self, deviceName):
        """
        clearDevices deletes all the actual knows devices and sens out the appropriate
        qt signals

        :param deviceName: name string of INDI device
        :return: success for test purpose
        """

        for device in self.devices:
            if not device == deviceName:
                continue
            self.signals.removeDevice.emit(device)
            self.signals.deviceDisconnected.emit(device)
            self.logger.info('Remove device {0}'.format(device))
        self.devices = {}
        return True

    def disconnectServer(self, deviceName=''):
        """
        Part of BASE CLIENT API of EKOS
        disconnect drops the connection to the indi server

        :param deviceName: name string of INDI device
        :return: success
        """

        self.connected = False
        self.clearParser()
        self.signals.serverDisconnected.emit(self.devices)
        self.clearDevices(deviceName)
        self.socket.abort()
        return True

    @PyQt5.QtCore.pyqtSlot()
    def _handleDisconnected(self):
        """
        _handleDisconnected log all network errors in case of problems.

        :return: nothing
        """

        self.logger.info('INDI client disconnected')
        self.disconnectServer()

    def isServerConnected(self):
        """
        Part of BASE CLIENT API of EKOS

        :return: true if server connected
        """

        return self.connected

    def connectDevice(self, deviceName=''):
        """
        Part of BASE CLIENT API of EKOS

        :param deviceName: name string of INDI device
        :return: success
        """

        if not self.connected:
            return False
        if not deviceName:
            return False
        suc = self.sendNewSwitch(deviceName=deviceName,
                                 propertyName='CONNECTION',
                                 elements='CONNECT',
                                 )
        return suc

    def disconnectDevice(self, deviceName=''):
        """
        Part of BASE CLIENT API of EKOS

        :param deviceName: name string of INDI device
        :return: success
        """

        if not self.connected:
            return False
        if not deviceName:
            return False
        if deviceName not in self.devices:
            return False
        suc = self.sendNewSwitch(deviceName=deviceName,
                                 propertyName='CONNECTION',
                                 elements='DISCONNECT',
                                 )
        return suc

    def getDevice(self, deviceName=''):
        """
        Part of BASE CLIENT API of EKOS
        getDevice collects all the data of the given device

        :param deviceName: name of device
        :return: dict with data of that give device
        """

        return self.devices.get(deviceName, None)

    def getDevices(self, driverInterface=0xFFFF):
        """
        Part of BASE CLIENT API of EKOS
        getDevices generates a list of devices, which are from type of the given
        driver interface type.

        :param driverInterface: binary value of driver interface type
        :return: list of knows devices of this type
        """

        deviceList = list()
        for deviceName in self.devices:
            typeCheck = self._getDriverInterface(deviceName) & driverInterface
            if typeCheck:
                deviceList.append(deviceName)
        return deviceList

    def setBlobMode(self, blobHandling='Never', deviceName='', propertyName=''):
        """
        Part of BASE CLIENT API of EKOS

        :param blobHandling:
        :param deviceName: name string of INDI device
        :param propertyName: name string of device property
        :return: true if server connected
        """

        if not deviceName:
            return False
        if deviceName not in self.devices:
            return False
        cmd = indiXML.enableBLOB(blobHandling,
                                 indi_attr={'name': propertyName,
                                            'device': deviceName})
        self.blobMode = blobHandling
        suc = self._sendCmd(cmd)
        return suc

    def getBlobMode(self, deviceName='', propertyName=''):
        """
        Part of BASE CLIENT API of EKOS

        :param deviceName: name string of INDI device
        :param propertyName: name string of device property
        :return: None, because not implemented
        """
        pass

    def getHost(self):
        """
        Part of BASE CLIENT API of EKOS

        :return: host name as str
        """

        if self._host is None:
            return ''
        if len(self._host) != 2:
            return 0
        return self._host[0]

    def getPort(self):
        """
        Part of BASE CLIENT API of EKOS

        :return: port number as int
        """

        if self._host is None:
            return 0
        if len(self._host) != 2:
            return 0
        return self._host[1]

    def sendNewText(self, deviceName='', propertyName='', elements='', text=''):
        """
        Part of BASE CLIENT API of EKOS

        :param deviceName: name string of INDI device
        :param propertyName: name string of device property
        :param elements: element name or dict of element name / values
        :param text: string in case of having only one element in elements
        :return: success for test
        """

        if deviceName not in self.devices:
            return False
        if not hasattr(self.devices[deviceName], propertyName):
            return False
        if not isinstance(elements, dict):
            elements = {elements: text}
        elementList = []
        for element in elements:
            text = elements[element]
            elementList.append(
                indiXML.oneText(text,
                                indi_attr={'name': element}
                                )
            )
        cmd = indiXML.newTextVector(elementList,
                                    indi_attr={'name': propertyName,
                                               'device': deviceName})
        suc = self._sendCmd(cmd)
        return suc

    def sendNewNumber(self, deviceName='', propertyName='', elements='', number=0):
        """
        Part of BASE CLIENT API of EKOS

        :param deviceName: name string of INDI device
        :param propertyName: name string of device property
        :param elements: element name or dict of element name / values
        :param number: value in case of having only one element in elements
        :return: success for test
        """

        if deviceName not in self.devices:
            return False
        if not hasattr(self.devices[deviceName], propertyName):
            return False
        if not isinstance(elements, dict):
            elements = {elements: number}
        elementList = []
        for element in elements:
            number = elements[element]
            elementList.append(
                indiXML.oneNumber(number,
                                  indi_attr={'name': element}
                                  )
            )
        cmd = indiXML.newNumberVector(elementList,
                                      indi_attr={'name': propertyName,
                                                 'device': deviceName})
        suc = self._sendCmd(cmd)
        return suc

    def sendNewSwitch(self, deviceName='', propertyName='', elements=''):
        """
        Part of BASE CLIENT API of EKOS

        :param deviceName: name string of INDI device
        :param propertyName: name string of device property
        :param elements: element name or dict of element name / values
        :return: success for test
        """

        if deviceName not in self.devices:
            return False
        if not hasattr(self.devices[deviceName], propertyName):
            return False
        if not isinstance(elements, dict):
            elements = {elements: 'On'}
        elementList = []
        for element in elements:
            switch = elements[element]
            elementList.append(
                indiXML.oneSwitch(switch,
                                  indi_attr={'name': element}
                                  )
            )
        cmd = indiXML.newSwitchVector(elementList,
                                      indi_attr={'name': propertyName,
                                                 'device': deviceName})
        suc = self._sendCmd(cmd)
        return suc

    def startBlob(self, deviceName='', propertyName='', timestamp=''):
        """
        Part of BASE CLIENT API of EKOS

        :return:
        """
        pass

    def sendOneBlob(self, blobName='', blobSize=0, blobFormat='', blobBuffer=None):
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

        pass

    @staticmethod
    def isVerbose():
        """
        Part of BASE CLIENT API of EKOS

        :return: status of verbose
        """

        return False

    def setConnectionTimeout(self, seconds=2, microseconds=0):
        """
        Part of BASE CLIENT API of EKOS

        :return: success for test purpose
        """

        self.CONNECTION_TIMEOUT = seconds + microseconds / 1000000
        return True

    def _sendCmd(self, indiCommand):
        """
        sendCmd take an XML indi command, converts it and sends it over the network and
        flushes the buffer

        :param indiCommand: XML command to send
        :return: success of sending
        """

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

        device = self.devices[deviceName]
        if not hasattr(device, 'DRIVER_INFO'):
            return -1
        val = getattr(device, 'DRIVER_INFO')
        if val:
            val = val['elementList'].get('DRIVER_INTERFACE', '')
            if val:
                interface = val['value']
                return int(interface)
            else:
                return -1
        else:
            return -1

    def _fillAttributes(self, deviceName=None, chunk=None, elementList=None, defVector=None):
        """

        :param deviceName: device name
        :param chunk:   xml element from INDI
        :param elementList:
        :param defVector:
        :return: True for test purpose
        """

        # now running through all atomic elements
        for elt in chunk.elt_list:
            name = elt.attr.get('name', '')
            elementList[name] = {}
            elementList[name]['elementType'] = elt.etype

            # as a new blob vector does not  contain an initial value, we have to separate this
            if not isinstance(elt, indiXML.DefBLOB):

                if elt.etype in ['defNumber',
                                 'setNumber',
                                 'oneNumber']:
                    elementList[name]['value'] = float(elt.getValue())

                elif elt.etype in ['defSwitch',
                                   'oneSwitch',
                                   'setSwitch']:
                    elementList[name]['value'] = (elt.getValue() == 'On')

                else:
                    elementList[name]['value'] = elt.getValue()

            # now all other attributes of element are stored
            for attr in elt.attr:
                elementList[name][attr] = elt.attr[attr]

            # if we don't set values, no connection signals
            if defVector:
                continue

            # send connected signals
            if name == 'CONNECT' and elt.getValue() == 'On':
                self.signals.deviceConnected.emit(deviceName)
                self.logger.info('Device {0} connected'.format(deviceName))
            if name == 'DISCONNECT' and elt.getValue() == 'On':
                self.signals.deviceDisconnected.emit(deviceName)
                self.logger.info('Device {0} disconnected'.format(deviceName))

        return True

    @staticmethod
    def _setupPropertyStructure(chunk=None, device=None):
        """

        :param chunk:   xml element from INDI
        :param device:  device class
        :return:
        """

        iProperty = chunk.attr.get('name', '')
        if not hasattr(device, iProperty):
            setattr(device, iProperty, {})

        # shortening for readability
        deviceProperty = getattr(device, iProperty)

        deviceProperty['propertyType'] = chunk.etype
        for vecAttr in chunk.attr:
            deviceProperty[vecAttr] = chunk.attr.get(vecAttr)

        # adding subspace for atomic elements (text, switch, etc)
        deviceProperty['elementList'] = {}
        elementList = deviceProperty['elementList']

        return iProperty, elementList

    def _getDeviceReference(self, chunk=None):
        """
        _getDeviceReference extracts the device name from INDI chunk and looks device
        presence in INDi base class up. if not present, a new device will be generated

        :param chunk:   xml element from INDI
        :return: device and device name
        """

        deviceName = chunk.attr.get('device', '')

        if deviceName not in self.devices:
            self.devices[deviceName] = Device(deviceName)
            self.signals.newDevice.emit(deviceName)
            self.logger.info('New device {0}'.format(deviceName))

        device = self.devices[deviceName]
        return device, deviceName

    def _delProperty(self, chunk=None, device=None, deviceName=None):
        """
        _delProperty removes property from device class

        :param chunk:   xml element from INDI
        :param device:  device class
        :param deviceName: device name
        :return: success
        """

        if deviceName not in self.devices:
            return False
        if 'name' not in chunk.attr:
            return False
        iProperty = chunk.attr['name']
        if hasattr(device, iProperty):
            delattr(device, iProperty)
            self.signals.removeProperty.emit(deviceName, iProperty)
            self.logger.info('New device [{0}] property {1}'.format(deviceName, iProperty))
        return True

    def _setProperty(self, chunk=None, device=None, deviceName=None):
        """
        _sefProperty generate and write all data to device class for SefVector chunks

        :param chunk:   xml element from INDI
        :param device:  device class
        :param deviceName: device name
        :return: success
        """

        iProperty, elementList = self._setupPropertyStructure(chunk=chunk, device=device)

        self._fillAttributes(deviceName=deviceName,
                             chunk=chunk,
                             elementList=elementList,
                             defVector=False)

        if isinstance(chunk, indiXML.SetBLOBVector):
            self.signals.newBLOB.emit(deviceName, iProperty)
        elif isinstance(chunk, indiXML.SetSwitchVector):
            self.signals.newSwitch.emit(deviceName, iProperty)
        elif isinstance(chunk, indiXML.SetNumberVector):
            self.signals.newNumber.emit(deviceName, iProperty)
        elif isinstance(chunk, indiXML.SetTextVector):
            self.signals.newText.emit(deviceName, iProperty)
        elif isinstance(chunk, indiXML.SetLightVector):
            self.signals.newLight.emit(deviceName, iProperty)

        return True

    def _defProperty(self, chunk=None, device=None, deviceName=None):
        """
        _defProperty generate and write all data to device class for DefVector chunks

        :param chunk:   xml element from INDI
        :param device:  device class
        :param deviceName: device name
        :return: success
        """

        iProperty, elementList = self._setupPropertyStructure(chunk=chunk, device=device)

        self._fillAttributes(deviceName=deviceName,
                             chunk=chunk,
                             elementList=elementList,
                             defVector=True)

        self.signals.newProperty.emit(deviceName, iProperty)

        if isinstance(chunk, indiXML.DefBLOBVector):
            self.signals.defBLOB.emit(deviceName, iProperty)
        elif isinstance(chunk, indiXML.DefSwitchVector):
            self.signals.defSwitch.emit(deviceName, iProperty)
        elif isinstance(chunk, indiXML.DefNumberVector):
            self.signals.defNumber.emit(deviceName, iProperty)
        elif isinstance(chunk, indiXML.DefTextVector):
            self.signals.defText.emit(deviceName, iProperty)
        elif isinstance(chunk, indiXML.DefLightVector):
            self.signals.defLight.emit(deviceName, iProperty)

        return True

    def _getProperty(self, chunk=None, device=None, deviceName=None):
        """

        :param chunk:   xml element from INDI
        :param device:  device class
        :param deviceName: device name
        :return: success
        """

        # todo: there is actually no implementation for this type. check if it is relevant
        # get property is for snooping other devices
        pass

    def _message(self, chunk=None, deviceName=None):
        """

        :param chunk:   xml element from INDI
        :param deviceName: device name
        :return: success
        """

        message = chunk.attr.get('message', '-')
        self.signals.newMessage.emit(deviceName, message)
        return True

    def _parseCmd(self, chunk):
        """
        _parseCmd parses the incoming indi XL data and builds up a dictionary of devices
        in device class which holds all the data transferred through INDI protocol.

        :param chunk: raw indi XML element
        :return: success if it could be parsed
        """

        self.logger.debug('INDI XML chunk: {0}'.format(chunk))
        if not self.connected:
            return False

        if 'device' not in chunk.attr:
            self.logger.error('No device in chunk: {0}'.format(chunk))
            return False

        device, deviceName = self._getDeviceReference(chunk=chunk)

        # all message have no device names, they could be general
        if isinstance(chunk, indiXML.Message):
            self._message(chunk=chunk, deviceName=deviceName)
            return True

        if 'name' not in chunk.attr:
            self.logger.error('No property in chunk: {0}'.format(chunk))
            return False

        if isinstance(chunk, indiXML.DelProperty):
            self._delProperty(chunk=chunk, device=device, deviceName=deviceName)
            return True

        if isinstance(chunk, (indiXML.SetBLOBVector,
                              indiXML.SetSwitchVector,
                              indiXML.SetTextVector,
                              indiXML.SetLightVector,
                              indiXML.SetNumberVector,
                              )
                      ):
            self._setProperty(chunk=chunk, device=device, deviceName=deviceName)
            return True

        if isinstance(chunk, (indiXML.DefBLOBVector,
                              indiXML.DefSwitchVector,
                              indiXML.DefTextVector,
                              indiXML.DefLightVector,
                              indiXML.DefNumberVector,
                              )
                      ):
            self._defProperty(chunk=chunk, device=device, deviceName=deviceName)
            return True

        if isinstance(chunk, indiXML.GetProperties):
            self._getProperty(chunk=chunk, device=device, deviceName=deviceName)
            return True

        if isinstance(chunk, (indiXML.NewBLOBVector,
                              indiXML.NewSwitchVector,
                              indiXML.NewTextVector,
                              indiXML.NewNumberVector,
                              )
                      ):
            # todo: what to do with the "New" vector ?
            return True

        if isinstance(chunk, (indiXML.OneBLOB,
                              indiXML.OneSwitch,
                              indiXML.OneText,
                              indiXML.OneNumber,
                              )
                      ):
            # todo: what to do with the "One" vector ?
            return True

        self.logger.error('Unknown vectors: {0}'.format(chunk))
        return False

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
            # print(self.curDepth, event, elem.tag, elem.items(), '\n')
            if event == 'start':
                self.curDepth += 1
            elif event == 'end':
                self.curDepth -= 1
            else:
                self.logger.error('Problem parsing event: {0}'.format(event))
            if self.curDepth > 0:
                continue
            # print('Depth: ', self.curDepth, '  Parsed: ', elem.items())
            elemParsed = indiXML.parseETree(elem)
            elem.clear()
            self._parseCmd(elemParsed)

    @PyQt5.QtCore.pyqtSlot(PyQt5.QtNetwork.QAbstractSocket.SocketError)
    def _handleError(self, socketError):
        """
        _handleError log all network errors in case of problems.

        :param socketError: the error from socket library
        :return: nothing
        """

        if not self.connected:
            return
        self.logger.error('INDI client connection fault, error: {0}'.format(socketError))
        self.disconnectServer()
