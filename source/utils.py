#! /usr/bin/env python3

import argparse
import xml.etree.ElementTree as ET
from ibapi.scanner import ScannerSubscription 
from ibapi.tag_value import TagValue

parser = argparse.ArgumentParser()
parser.add_argument('--xml', type=str, help='scanner xml template')
args = parser.parse_args()

# Converts xml templated exported from TWS to
# JSON payload that can be used with WEB API

def createScanner(xml):
    
    tree = ET.parse(xml)
    root = tree.getroot()

    scanContent = root[0].attrib
    instr = root[0][2].attrib
    scnType = root[0][3].attrib
    advFilter = root[0][5]

    scanner = ScannerSubscription()
    scanner.scanCode = scnType['scanCode']
    scanner.instrument = instr['m_type']
    scanner.locationCode = scanContent['locationText']
    fltr = [{}]

    if len(advFilter) != 0:
        for el in advFilter:
            fltr[0].update({el.tag: el.text})
        
    jsonPayload = {
            "instrument": scanner.instrument,
            "location": scanner.locationCode,
            "type": scanner.scanCode,
            "filter": fltr
            }

    return jsonPayload
