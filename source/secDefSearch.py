#! /usr/bin/env python3

import argparse
import requests
import json
import urllib
import sys

requests.packages.urllib3.disable_warnings()

local_ip = "127.0.0.1"
port = 5000
base_url = f"https://{local_ip}:{port}/v1/api"


def checkAuthStatus():
    resp = requests.get(base_url + "/iserver/auth/status", verify=False)
    if resp.status_code == 200:
        jsonData = json.loads(resp.text)
        if jsonData['authenticated'] == True:
            print("---> Succesfully authenticated")
            print(jsonData)
    if resp.status_code == 401:
        print(jsonData)
        raise Exception("Unauthenticated, please login")

def searchBySymbol(symbol: str, sectype: str):
    data = {
            "symbol": symbol,
            "name": True,
            "secType": "STK",
            }
    resp = requests.post(base_url + "/iserver/secdef/search", json=data, verify=False)
    if resp.status_code == 200:
        jsonData = json.loads(resp.text)
        contract = jsonData[0]
        print(f"---> Received contract details for {symbol}")
        return contract 
    else:
        raise RuntimeError(f"Nothing found for symbol {symbol}")

def getStrikes(conid, month, exchange=None, secType=None):
    url = "/iserver/secdef/strikes"
    params = {
            "conid": conid, 
            "sectype": secType,
            "month": month,
            "exchange":  exchange
            }
    response = requests.get(base_url + url, params=params, verify=False)
    jsonData = json.loads(response.text)
    return jsonData

def getContract(conid, month, right, strike, exchange=None, secType=None):
    url = "/iserver/secdef/info"
    params = {
            "conid": conid,
            "secType": "OPT" if secType is None else secType, 
            "month": month,
            "exchange": 'SMART' if exchange == None else exchange,
            "strike": strike,
            "right": right 
            }
    response = requests.get(base_url + url, params=params, verify=False)
    print(response.text)

def checkSecType(sections, secType):
    allowedList = ["WAR", "OPT", "FOP"]
    availableSecTypes = []
    for s in sections:
        if s['secType'] in allowedList:
            availableSecTypes.append(s['secType'])

    if len(availableSecTypes) != 0:
        while secType not in availableSecTypes:
            print(f"Available sectypes: {availableSecTypes}")
            secType = input("Input: ")
        return secType

    print(f"No {' '.join(allowedList)} for this instrument")
    sys.exit()

def setExchange(exchanges):
    print(f"Please select one of the exchanges: {exchanges}")
    exchange = input("Type in the exchange: ")
    while exchange not in exchanges:
        print("Invalid exchange")
        exchange = input("Please input exchange: ")

    return exchange
            
def secDefParams(symbol, secType):

    details = searchBySymbol(symbol, secType)
    sections = details['sections']
    print(sections)
    secType = checkSecType(sections, secType)
    for s in sections:
        if s['secType'] == secType:
            months = s['months']
            exchanges = s['exchange'].split(';')
            exchange = setExchange(exchanges)
            try:
                for m in months:
                    strikesPerMonth = getStrikes(conid=details['conid'], month=m, exchange=exchange, 
                            secType=secType)
                    print(strikesPerMonth)
                    for s in strikesPerMonth['call']:
                        print(s)
                        getContract(conid=details['conid'], right='C',
                                month=m, strike=s, exchange=exchange, secType=secType)

                    for s in strikesPerMonth['put']:
                        print(s)
                        getContract(conid=details['conid'], right='P',
                                month=m, strike=s, exchange=exchange, secType=secType)

            except KeyboardInterrupt:
                sys.exit()

def run():

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symbol', help = "symbol of the instrument")
    parser.add_argument('-sec', '--sectype', help = "security type - either WAR, OPT or FOP")
    args = parser.parse_args()

    if not args.symbol or not args.sectype:
        parser.print_help()
        sys.exit()
        
    symbol = args.symbol 
    sectype = args.sectype 
    secDefParams(symbol, sectype)

def main():
    run()

if __name__ == "__main__":
    main()
