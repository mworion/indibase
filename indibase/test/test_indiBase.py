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
from unittest import mock
# external packages
import PyQt5
from PyQt5.QtTest import QTest
# local import
from indibase import indiBase
from indibase import indiXML

app = PyQt5.QtWidgets.QApplication([])

test = indiBase.Client()


#
#
# testing main
#
#

def test_setServer1():

    test.setServer()
    assert ('', 7624) == test.host


def test_setServer2():

    test.setServer('heise.de')
    assert ('heise.de', 7624) == test.host


def test_setServer3():

    test.setServer('heise.de', 7624)
    assert ('heise.de', 7624) == test.host


def test_watchDevice1():

    call_ref = indiXML.clientGetProperties(indi_attr={'version': '1.7',
                                                      'device': 'test'})
    ret_val = True
    with mock.patch.object(test,
                           'sendCmd',
                           return_value=ret_val):
        test.watchDevice('test')
        call_val = test.sendCmd.call_args_list[0][0][0]
        assert call_ref.toXML() == call_val.toXML()


def test_watchDevice2():

    call_ref = indiXML.clientGetProperties(indi_attr={'version': '1.7',
                                                      'device': ''})
    ret_val = True
    with mock.patch.object(test,
                           'sendCmd',
                           return_value=ret_val):
        test.watchDevice()
        call_val = test.sendCmd.call_args_list[0][0][0]
        assert call_ref.toXML() == call_val.toXML()


def test_connectServer1(qtbot):

    test.setServer('')
    with qtbot.assertNotEmitted(test.signals.serverConnected) as blocker:
        suc = test.connectServer()
        assert not suc


def test_connectServer2(qtbot):

    test.setServer('localhost')
    with qtbot.waitSignal(test.signals.serverConnected) as blocker:
        suc = test.connectServer()
        assert suc
    assert [] == blocker.args
    test.disconnectServer()


def test_connectServer3(qtbot):

    test.setServer('localhost')
    test.connected = True
    with qtbot.waitSignal(test.signals.serverConnected) as blocker:
        suc = test.connectServer()
        assert suc
    assert [] == blocker.args
    test.disconnectServer()


def test_disconnectServer1(qtbot):

    test.setServer('')
    with qtbot.assertNotEmitted(test.signals.serverDisconnected) as blocker:
        suc = test.disconnectServer()
        assert suc


def test_disconnectServer2(qtbot):

    test.setServer('localhost')
    test.connectServer()
    with qtbot.waitSignal(test.signals.serverDisconnected) as blocker:
        suc = test.disconnectServer()
        assert suc
    assert [] == blocker.args


def test_disconnectServer3(qtbot):

    test.setServer('localhost')
    with qtbot.assertNotEmitted(test.signals.serverDisconnected) as blocker:
        suc = test.disconnectServer()
        assert suc


def test_isServerConnected1():

    test.setServer('localhost')
    test.connectServer()
    val = test.isServerConnected()
    assert val


def test_isServerConnected2():

    test.setServer('localhost')
    test.disconnectServer()
    val = test.isServerConnected()
    assert not val


def test_connectDevice1():

    test.setServer('localhost')
    test.connectServer()
    suc = test.connectDevice('')
    assert not suc
    test.disconnectServer()


def test_connectDevice2():

    test.setServer('localhost')
    test.connectServer()
    suc = test.connectDevice('CCD Simulator')
    assert suc
    test.disconnectServer()


def test_connectDevice3():

    test.setServer('localhost')
    suc = test.connectDevice('CCD Simulator')
    assert not suc


def test_disconnectDevice1():

    test.setServer('localhost')
    suc = test.connectServer()
    assert suc
    suc = test.connectDevice('CCD Simulator')
    assert suc
    QTest.qWait(500)
    suc = test.disconnectDevice('CCD Simulator')
    assert suc
    test.disconnectServer()


def test_disconnectDevice2():

    test.setServer('localhost')
    suc = test.connectServer()
    assert suc
    suc = test.connectDevice('CCD Simulator')
    assert suc
    suc = test.disconnectDevice('')
    assert not suc
    test.disconnectServer()


def test_disconnectDevice3():

    suc = test.disconnectDevice('CCD Simulator')
    assert not suc


def test_getDevice1():

    dev = test.getDevice('')
    assert not dev


def test_getDevice2():

    test.setServer('localhost')
    test.connectServer()
    test.watchDevice('CCD Simulator')
    QTest.qWait(500)
    dev = test.getDevice('CCD Simulator')
    assert dev
    test.disconnectServer()


def test_getDevices3():
    pass