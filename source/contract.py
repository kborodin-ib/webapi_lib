#! /usr/bin/env python3

import requests
import sys
import json
from cplib_v0.endpoints import endpoints
from cplib_v0.exceptions import NoContractsFoundForSymbol

contractString = """
        # Provide only conid or conidex field
        self.conid = ''
        self.conidex = ''
        self.symbol = ''
        self.secType = ''
        self.currency = ''
        self.exchange = ''
        self.ticker = ''
        self.multiplier = int() 
        self.lastTradeDateOrContractMonth = ''
        self.locaSymbol = ''
        self.JSON = {}
        """
class Contract:

    def __init__(self, conid):
        self.conid = conid

    def __repr__(self):
        return f"Conid: {self.conid}"

class FutContract(Contract):
    
    def __init__(self, conid, month, exchange):
        Contract.__init__(self, conid)
        self.secType = 'FUT'
        self.month = month
        self.exchange = exchange

class OptContract(FutContract):
    
    def __init__(self, conid, month, exchange, strike, right):
        FutContract.__init__(self, conid, month, exchange)
        self.secType = 'OPT'
        self.right = right
        selt.strike = strike

class Instrument:

    def __init__(self, symbol='', companyName=''):
        self.symbol = symbol
        self.companyName = companyName
        self.json = [] # because of reasons 
        self.conid = 0

    def assignbyCompName(self, companyName):
        return

    def assignBySymbol(self, sumbol):
        return

    def getContractsByName(self):
        params = {
                'symbol': self.companyName, 
                'name': True,
                'secType': ''
                }
        response = requests.get(endpoints['cont_by_symbol'],
                params=params, verify=False)
        jsonData = json.loads(response.text) 
        if type(jsonData) != list:
            print("Returned unexpected format: ", jsonData)
            print(self.companyName, self.symbol)
        self.json = jsonData

    def getContractsBySymbol(self):
        params = {
                'symbol': self.symbol,
                'name': False,
                'secType': ''
                }
        response = requests.get(endpoints['cont_by_symbol'],
                params=params, verify=False)
        jsonData = json.loads(response.text) 
        if type(jsonData) != list:
            raise NoContractsFoundForSymbol
        self.json = jsonData
    
    def getContractByConid(self, conid):
        endpoint = endpoints['secdefid']
        print(endpoint)
        endpoint = endpoint.replace('coid', conid)
        response = requests.get(endpoint, verify=False)
        print(response.text)


    def setStockContract(self):
        # Parses self.json for sectype STK, matches by company name
        return

    def showFoundContracts(self):
        for el in self.json:
            print(el, '\n')
    
    def getCFDContractId(self, exchange):
        for el in self.json:
            if el['description'] == exchange:
                try:
                    sections = el['sections']
                    for sec in sections:
                        if sec['secType'] == 'CFD':
                            self.conid = sec['conid']
                            break
                except KeyError:
                    print(f"No CFD's for {self.symbol} at {exchange}")


    def assignConid(self):
        conids = []
        for el in self.json:
            try:
                if el['conid'] != '-1':
                    cmpStr = f"{el['conid']} - {el['companyHeader']}"
                    conids.append(el['conid'])
                    print(cmpStr)
            except KeyError:
                continue 
        if len(conids) < 1:
            print("No conids were obtained for this instrument")
            pass
        if len(conids) > 1:
            conid = input("Please input conid: ")
            while conid not in conids:
                conid = input("Please input valid conid: ")
        else:
            conid = conids[0]

        print(f"Chosen conid: {conid}")

        self.conid = conid

    def setChainsJSON(self, secType):
        # We only need part of JSON that contains
        # data required for chains building
        print(self.json)
        for el in self.json:
            for sec in el['sections']:
                if sec['secType'] == secType:
                    self.json = sec
                    return
        print(f"No {secType} data") 
        sys.exit()

    def getStrikes(self, conid, month, exchange, secType):
        params = {
                "conid": conid, 
                "sectype": secType,
                "month": month,
                "exchange": exchange, 
                }
        print(params)
        contract = SecDefContract(conid, secType, month, exchange,
                strike = '', right = '')
        response = requests.get(endpoints['strikes'], 
                params=params, verify=False)
        jsonData = json.loads(response.text)
        return jsonData

    def getContractDetails(self, contract):
        print(contract.__dict__)
        response = requests.get(endpoints['secDef_by_cid']
                , params=contract.__dict__, verify=False)
        self.json = json.loads(response.text)

    def getTradingSchedule(self,assetClass, symbol, exchange, exhchangeFilter=''):
        endpoint = endpoints['tradingSchedule']
        params = {
                'assetClass': assetClass,
                'exchange': exchange,
                'symbol': symbol,
                'exhchangeFilter': exhchangeFilter,
                }
        resp = requests.get(endpoint, params=params, verify=False)
        jsonData = json.loads(resp.text)
        for el in jsonData:
            print(el)


    def futSecDefInfo(self):
        # Will build chains from JSON that is assigned per secType on class level
        print("Current values of self.json: \n", self.json)
        try:
            months = self.json['months'].split(';')
            print(months)
            exchange = self.json['exchange']
            secType = self.json['secType']
            contract = FutContract(self.conid, '', exchange)
            contract.exchange = self.json['exchange']
            for m in months:
                contract.month = m
                self.getContractDetails(contract) 
        except KeyError as err:
            print(err, ' while building chains')

    def optSecDefInfo(self):
        return


