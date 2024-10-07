#! /usr/bin/env python3

from webapilib.endpoints import endpoints
import requests
import json
import sys


# Remember to make multiple contract classes, OPT, FOP etc...
class Contract():

    def __init__(self):
       
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
    
    def useConidex(self):
        return

    def useConidExchange(self):
        return

    def searchSymbol(self):
        endpoint = endpoints['cont_by_symbol']
        print(endpoint)
        params = {
                'symbol': self.symbol,
                'name': False,
                'secType': 'STK'
                }
        response = requests.get(endpoint, 
                verify=False, params=params)
        print(response.text)
        sys.exit()

    def fillContractDetails(self, conid):
        endpoint = endpoints['secdefid'].replace('coid', conid)
        print(endpoint)
        response = requests.get(endpoint, verify=False)
        jsonData = json.loads(response.text)
        print(jsonData)
        if 'error' not in jsonData.keys():
            self.conid = conid
            self.symbol = jsonData['symbol']
            self.secType = jsonData['instrument_type']
            self.exchange = jsonData['exchange']
            self.currency = jsonData['currency']
        else:
            print(jsonData['error'])

        return

    def fillOptDetails(self, conid):
        endpoint = endpoints['secdefid'].replace('coid', conid)
        print(endpoint)
        response = requests.get(endpoint, verify=False)
        jsonData = json.loads(response.text)
        print(jsonData)
        if 'error' not in jsonData.keys():
            self.conid = conid
            self.symbol = jsonData['symbol']
            self.secType = jsonData['instrument_type']
            self.exchange = jsonData['exchange']
            self.multiplier = jsonData['multiplier']
            self.currency = jsonData['currency']
            self.lastTradeDateOrContractMonth = jsonData['contract_month']
            self.strike = jsonData['strike']
            self.localSymbol = jsonData['local_symbol']
        print(self)
        return

    def getAvailableAlgos(self, conid):
        endpoint = endpoints['algorithms'].replace('conid', conid)
        resp = requests.get(endpoint, verify=False)
        try:
            jsonData = json.loads(resp.text)
        except Exception as err:
            print(err, '\n Shutting down')
            sys.exit()

        return jsonData['algos']

    # algos is a string delimtered by ; . Contains algosids
    def getAlgoParams(self, conid, algos):
        endpoint = endpoints['algorithms'].replace('conid', conid)
        params = {'addDescriptions': 1, 'addParams': 1, 'algos': algos}
        resp = requests.get(endpoint, verify=False, params=params)
        try:
            jsonData = json.loads(resp.text)
        except Exception as err:
            print(err, '\n Shutting down')
            sys.exit()

        return jsonData['algos']



    def _toJSON(self):
        self.JSON = {
                "conid": int(self.conid),
                "conidex": self.conidex, 
                "listingExchange": self.exchange,
                "ticker": self.ticker
                }


    def __repr__(self):
        if not self.JSON:
            self._toJSON()
        return f"Contract JSON: {self.JSON}\n"

class Order():

    def __init__(self):
        self.acctId = ""
        self.orderType = ""
        self.outsideRth = False 
        self.side = ""
        self.ticker = ""
        self.tif = ""
        self.quantity = ""
        self.cOID = ""
        self.referrer = ""
        self.parentId = ""
        self.price = "" 
        self.useAdaptive = False 
#        self.trailingType = ""
#        self.trailingAmount = ""
        self.strategy = ""
        self.strategyParameters = "" 
        self.JSON = {}

    def _toJSON(self):
        self.JSON.update({
                "acctId": self.acctId,
                "cOID": self.cOID,
                "orderType": self.orderType,
                "outsideRTH": self.outsideRth,
                "price": self.price,
                "side": self.side,
                "ticker": self.ticker,
                "tif": self.tif,
                "quantity": self.quantity,
                "referrer": self.referrer,
                "parentId": self.parentId,
                "useAdaptive": self.useAdaptive,
#                "trailingType": self.trailingType,
#                "trailingAmt": self.trailingAmount,
                "strategy": self.strategy,
                "strategyParameters": self.strategyParameters
                })

    def isMktOrder(self):
        del self.JSON['price']
        self.JSON['orderType'] = 'MKT'

    def adjustPrice(self, price):
        self.JSON['price'] = price

    def adjustSize(self, size):
        self.JSON['size'] = size

    def updateAccountId(self, acctId):
        self.acctId = acctId

    def __repr__(self):
        if not self.JSON:
            self._toJSON()
        return f"Order JSON: {self.JSON}\n"


def createSampleContract():

    contract = Contract()
    contract.conid = 570639953 
    contract.exchange = "NASDAQ"
    contract.ticker = "XCUR"

    contract.__repr__()

    return contract

def createSampleOrder():
    
    order = Order()
    order.orderType = "LMT"
    order.outsideRth = False 
    order.price = 0.5999 
    order.side = "BUY"
    order.tif = "DAY"
    order.quantity = 20
    order.referrer = 'boris'
#    order.cOID = "someuniqueORDERID"

    return order


def createBracketOrder():

    contract = createSampleContract()

    order = Order()
    order.orderType = "LMT"
    order.outsideRth = False 
    order.price = 0.63
    order.side = "BUY"
    order.tif = "GTC"
    order.quantity = 1
    order.cOID = "uniqueOrderNumber3"

    profitTaker = Order()
    profitTaker.orderType = "LMT"
    profitTaker.outsideRth = False 
    profitTaker.price = 0.63
    profitTaker.side = "SELL"
    profitTaker.tif = "GTC"
    profitTaker.referrer = "ProfitTaker"
    profitTaker.quantity = 1
    profitTaker.useAdaptive = False
    profitTaker.parentId = order.cOID

    stopLoss = Order()
    stopLoss.orderType = "LMT"
    stopLoss.outsideRth = False 
    stopLoss.price = 0.65
    stopLoss.side = "SELL"
    stopLoss.tif = "GTC"
    stopLoss.referrer = "ProfitTaker"
    stopLoss.quantity = 1
    stopLoss.useAdaptive = False
    stopLoss.parentId = order.cOID
    
    return [order, profitTaker, stopLoss] 




















