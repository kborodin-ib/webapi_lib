#! /usr/bin/env python3

import pytest
import requests

from time import sleep
from cplib_v0.client import Session
from cplib_v0.exceptions import *

# Session tests:

@pytest.fixture
def new_session():
    print("\n Setting up stuff")
    requests.packages.urllib3.disable_warnings()
    session = Session()
    session.connect()
    return session

def test_isConnected(new_session):
    jsonData = new_session.checkConnection()
    assert jsonData['connected'] == True

def test_isAuthenticated(new_session):
    jsonData = new_session.checkConnection()
    assert jsonData['authenticated'] == True

def test_isNotCompeting(new_session):
    jsonData = new_session.checkConnection()
    assert jsonData['competing'] == False 

def test_recoverSessionFromTimeout(new_session):
    print("[+] waiting n for session to timeout")
    sleep(700)
    jsonData = new_session.checkConnection()
    assert jsonData['authenticated'] == True

def sup_test_canLogOut(new_session):
    new_session.logout()
    jsonData = new_session.checkConnection()
    assert jsonData['authenticated'] == False
