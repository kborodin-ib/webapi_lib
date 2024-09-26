#! /usr/bin/env python3

import json
import requests
import argparse
import time
import urllib
import random
import hashlib
import sys
from time import sleep
from orderPayloads import Samples 
from betaPayloads import *
import urllib
import ssl

#from filterList import fltrList

#parser = argparse.ArgumentParser()
#parser.add_argument('-a', '--address', help = "provide server ip address")
#args = parser.parse_args()

sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS)
sslContext.verify_mode = ssl.CERT_NONE

requests.packages.urllib3.disable_warnings()

local_ip = "127.0.0.1:5000"
#local_ip = "192.168.43.215:5000"
base_url = f"https://{local_ip}/v1/api"
headers = {
        "User-Agent": "python-requests/2.28.1",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Content-type": "application/json"
        }

def saveOrderRecord(orderJson):
    return

def stocksBySymbol(symbol):
    endpoint = base_url + f"/trsrv/stocks"
    data = {
            "symbols": symbol
            }
    response = requests.get(endpoint, params=data, verify=False, headers=headers)
    jsonData = json.loads(response.text)
    return jsonData

def snapShotDataSubscribe(conIds: str, fields: str, since):
    endpoint = base_url + "/iserver/marketdata/snapshot"
    data = {
            "conids": conIds,
            "fields": fields,
            "since": since
            }
    response = requests.get(endpoint, verify=False, params=data, headers=headers)
    jsonData = json.loads(response.text)
    return jsonData

def snapShotDataUnsubscribe(conid):
    endpoint = base_url + f"/iserver/marketdata/{conid}/unsubscribe"
    data = {"conid": conid}
    response = requests.get(endpoint, params=data, verify=False, headers=headers)
    if response.status_code == 200:
        print(response.text)
    else:
        print(response.status_code, ", fail")

def unsubscribeAll():
    endpoint = base_url + f"/iserver/marketdata/unsubscribeall"
    response = requests.get(endpoint, verify=False, headers=headers)
    if response.status_code == 200:
        print("Unsubscribe all: ", response.text)


def futuresContractPerSymbol(symbol: str):
    endpoint = "/trsrv/futures"
    data = {"symbols": symbol}
    resp = requests.get(base_url + endpoint, verify=False, params=data)
    if resp.status_code == 200:
        jsonData = json.loads(resp.text)
        if len(jsonData.keys()) != 0:
            validContracts = jsonData[data['symbols']]
            return validContracts

def getSpecificContractDetails(conId):
    endpoint = f"/iserver/contract/{conId}/info"
    data = {"conid": conId}
    resp = requests.get(base_url + endpoint, verify=False, params=data)
    if resp.status_code == 200:
        jsonData = json.loads(resp.text)
        return jsonData

def getOrderIds():
    resp = requests.get(base_url + "/iserver/account/orders", verify=False, 
            headers=headers)
    jsonData = json.loads(resp.text)
    ids = []
    for order in jsonData['orders']:
        prettyJson = json.dumps(order, indent=4)
        if "orderId" in order.keys():
            if order['orderId'] not in ids:
                ids.append(order['orderId'])
    return ids

def getAccounts():
    resp = requests.get(base_url + "/iserver/accounts", verify=False, 
            headers=headers)
    jsonData = json.loads(resp.text)
    try:
        accounts = jsonData['accounts']
        if 'error' in jsonData.keys():
            print("Accounts error: ", jsonData['error'])
            return
        if len(accounts) > 0:
            return accounts
        else:
            print("Go open an account, will ya.")
    except KeyError:
        print(jsonData)
        sys.exit()

def calculateCommission():

    jsonData = accountTrades()
    commission = 0
    price = 0
    for trade in jsonData:
        commission += int(float(trade['commission']))
        price += int(float(trade['price']))
    print(f"Price/Commission: {price}/{commission}")

def getPnl(accountId, writeFile=None):
    resp = requests.get(base_url + "/iserver/account/pnl/partitioned", verify=False)
    jsonData = json.loads(resp.text)
    if writeFile is not None:
        with open(writeFile, 'w') as outfile:
            json.dump(jsonData, outfile, indent=2)

    return jsonData['upnl'][f"{accountId}.Core"]['dpl']

def callPortfolioAccounts():
    resp = requests.get(base_url + "/portfolio/accounts", verify=False)
    print(resp.text)

def checkAuthStatus():
    resp = requests.get(base_url + "/iserver/auth/status", verify=False)
    if resp.status_code == 200:
        jsonData = json.loads(resp.text)
        if jsonData['authenticated'] == True:
            print("---> Succesfully authenticated")
        if jsonData['competing'] == False:
            print("---> No competing sessions")
        return jsonData
    else:
        print(resp.status_code, "--> Something went wrong: ")
        if resp.status_code == 401:
            raise Exception("Unauthorized, please login via web interface")

def accountTrades():
    data = {
            "days": 2
            }
    resp = requests.get(base_url + "/iserver/account/trades", params=data, verify=False,
            headers=headers)
    jsonData = json.loads(resp.text)
    with open('trades.json', 'w') as outfile:
        json.dump(jsonData, outfile, indent=2)
    return jsonData 

def getCommissionsAndPositinos():
    trades = accountTrades()
    entryOrders = {"price": 0, "commission": 0}
    exitOrders = {"price": 0, "commission": 0}
    for trade in trades:
        try:
            if '20231108' in trade['trade_time']:

                if trade['side'] == "B":
                    entryOrders['price'] += float(trade['price'])
                    entryOrders['commission'] += float(trade['commission'])

                if trade['side'] == "S":
                    exitOrders['price'] += float(trade['price'])
                    exitOrders['commission'] += float(trade['commission'])

        except KeyError:
            continue
    
    return entryOrders, exitOrders

def checkTypes(jsonData):
    for element in jsonData:
        for k,v in element.items():
            if type(k) == bytes or type(v) == bytes:
                print(f"some exception occured - {type(k)}: {type(v)}")
    print("Done comparing")

    
def placeOrder(accId: str, orderDict: dict):
    endpoint = f'/iserver/account/{accId}/orders'
    data = { "orders": [
        orderDict 
        ]
        
    }
    resp = requests.post(base_url + endpoint, verify=False, json=data,
            headers=headers)
    jsonData = json.loads(resp.text)
    print("/iserver/account/{accountid}/orders response: ", jsonData)
    for el in jsonData:
        if 'error' in el:
            print(f"---> Error while placing order: {jsonData['error']}")
            sys.exit()
             
        if type(el) == dict and "id" in el.keys():
            jsonData = orderReply(el['id'])
    return jsonData[0] 


def getContractRules(conID):
    print("is called")
    endpoint = '/iserver/contract/rules'
    data = {'conid': conID, "isBuy": True}
    response = requests.post(base_url + endpoint, json=data, verify=False,
            headers=headers)
    print(response.text)

# Available assetClass values: STK, OPT, FUT, CFD, WAR, SWP, FND, BND, ICS
def getTradingSchedule(assetClass, symbol, exchange=None, exchangeFilter=None):
    endpoint = base_url + "/trsrv/secdef/schedule"
    data = {"assetClass": assetClass, 
            "symbol": symbol,
            "exchange": exchange if exchange is not None else "",
            "exchangeFilter": exchangeFilter if exchangeFilter is not None else ""
            }
    respose = requests.get(endpoint, verify=False, params=data, headers=headers) 
    print(respose.text)

def getSecDefPerConId(conids: list):
    endpoint = base_url + "/trsrv/secdef"
    data={"conids": conids}
    print(data)
    respose = requests.post(endpoint, verify=False, json=data, headers=headers)
    jsonData = json.loads(respose.text)['secdef']
    return jsonData

def getFuturesData(sym: str, icludeExp: bool):
    endpoint = base_url + "/trsrv/futures"
    data={
            'symbols': sym,
            'Expired': icludeExp
            }
    print(data)
    respose = requests.get(endpoint, verify=False, params=data, headers=headers)
    jsonData = json.loads(respose.text)
    print(len(jsonData[sym]))
    writeJson(jsonData, f'test/{sym}' + '_Expired=' + str(icludeExp))
    for i in range(len(jsonData[sym])):
        print(jsonData[sym][i]['expirationDate'])


def createComboLeggedPayload(accId):
    # buy MSFT sell AAPL
    data = { 
            "acctId": accId,
            "conidex":"634662618;;;661395167/1,619333053/0", 
            "orderType": "LMT",
            "listingExchange": "",
            "outsideRTH": False,
            "price": 100,
            "side": "BUY",
            "ticker": "",
            "quantity": 1,
            "tif": "DAY",
            "cOID": "Custom ID",
            "isClose": False
            }

    return data

def createLimitOrderPayload(accId: str, conId: int, exchange: str,
        orth, price: int, action, symbol, quantity, tif, cOID=""):
    data = { 
            "acctId": accId,
            "conid": conId,
            "secType": f"secType = {conId}:STK",
            "orderType": "LMT",
            "listingExchange": exchange,
            "outsideRTH": orth,
            "price": price,
            "side": action,
            "ticker": symbol,
            "quantity": quantity,
            "tif": tif,
            "cOID": cOID 
            }

    return data

def createMarketOrderPayload(accId: str, conId: int, exchange: str,
        orth, action, symbol, quantity, tif, cOID):
    data = { 
            "acctId": accId,
            "conid": conId,
            "secType": f"secType = {conId}:STK",
            "orderType": "MKT",
            "listingExchange": exchange,
            "outsideRTH": orth,
            "side": action,
            "ticker": symbol,
            "quantity": quantity,
            "tif": tif,
            "cOID": cOID 
            }

    return data

def createMutliplePayloads(accId, conDefList):
    payloads = []
    for con in conDefList:
        payload = createLimitOrderPayload(
                accId=accId,
                conId=con['conid'],
                exchange=con['listingExchange'],
                orth=False,
                price=1,
                action="BUY",
                symbol=con['ticker'],
                quantity=1,
                tif="DAY"
                 )
        payloads.append(payload)
    return payloads

def orderReply(replyID):
    print("Reply id: ", replyID)
    endpoint = base_url + f"/iserver/reply/{replyID}"
    data = {'confirmed': True}
    response = requests.post(endpoint, verify=False, json=data, headers=headers)
    if len(response.text) != 0:
        jsonData = json.loads(response.text)
        for e in jsonData:
            if 'id' in e.keys():
                print(f"Confirmation: {e['id']}")
                orderReply(e['id'])
        return jsonData
    else:
        print("Nothing left to confirm")

def getOrderStatus(orderId):
    endpoint = base_url + f"/iserver/account/order/status/{orderId}"
    data = {'orderId': orderId}
    response = requests.get(endpoint, verify=False, params=data, headers=headers)
    jsonData = json.loads(response.text)
    print(jsonData)

def invalidatePositions(accId):
    endpoint = base_url + f"/portfolio/{accId}/positions/ivalidate"
    data = {"accountId": accId}
    response = requests.post(endpoint,json=data, verify=False, headers=headers)
    print(response.text)

def getPortfolioPositionsByPage(accId, pageId):
    endpoint = base_url + f"/portfolio/{accId}/positions/{pageId}"
    response = requests.get(endpoint, verify=False, headers=headers)

    if response.status_code == 200:
        jsonData = json.loads(response.text)
    else:
        raise RuntimeError("")

    return jsonData

def getPortfolioPositions(accId):
    data = {
            "accountId": accId,
            "model": "",
            "sort": "",
            "direction": "",
            "period": ""
            }
    endpoint = base_url + f"/portfolio/{accId}/positions"
    response = requests.get(endpoint, params=data, verify=False, headers=headers)

    if response.status_code == 200:
        jsonData = json.loads(response.text)
        print(jsonData)

    else:
        raise RuntimeError("")

def genRef(q, s):
    rand = random.randint(0, 999)
    string = str(rand) + '/' + str(q) + '/' + s
    result = hashlib.md5(string.encode()).hexdigest()
    return result 

def getOrderByCOID(cOID):
    trades = accountTrades()
    for trade in trades:
        try:
            if trade['order_ref'] == cOID:
                return trade
        except KeyError:
            continue


def placeSingleOrder(symbol, exchange, action, orderType, tif, orth, quantity, 
        price=None, orderRef=None):
    contract = searchBySymbol(symbol, "STK")
#    contract = searchBySymbol(symbol, "FUT")
    accId = getAccounts()[0]
    if orderType == "LMT":
        ref = genRef(quantity, symbol) 
        orderPayload = createLimitOrderPayload(
                accId = accId,
                conId=int(contract['conid']),
                exchange=exchange,
                orth=orth,
                price=price if price is not None else 0,
                action=action,
                symbol=contract['symbol'],
                quantity=quantity,
                tif=tif,
                cOID=ref if orderRef == None else orderRef
                )
        print("orderRef: ", ref)

    if orderType == "MKT":
        ref = genRef(quantity, symbol)
        orderPayload = createMarketOrderPayload(
                accId = accId,
                conId=int(contract['conid']),
                exchange=exchange,
                orth=orth,
                action=action,
                symbol=contract['symbol'],
                quantity=quantity,
                tif=tif,
                cOID=ref if orderRef == None else orderRef
                )
        print("orderRef: ", ref)
    message = placeOrder(accId, orderPayload)
    if type(message) is dict and "id" in message.keys():
        replyId = message['id']
        print(f"---> Confirmation is required for replyId {replyId}")
        # orderReply function implements recursive call so
        # all queries have relevant reply.
        orderReply(replyId)
    else:
        print(message)

    return ref



def placesFutOrders(symbol):
    contracts = futuresContractPerSymbol(symbol)
    contract = getSpecificContractDetails(contracts[0]['conid'])
    conIdList = [con['conid'] for con in contracts]
    conDefList = getSecDefPerConId(conIdList)
    # Take one contract from a list and place order for it
    curCon = conDefList[0]
    accountId = getAccounts()[0]
    print("Current accountID: ", accountId)
    print("Current contract: ", curCon) 
    singlePayload = createLimitOrderPayload(
            accId=accountId,
            conId=curCon['conid'],
            exchange=curCon['listingExchange'],
            orth=False,
            price=4430,
            action="SELL",
            symbol=curCon['ticker'],
            quantity=5,
            tif="DAY"
             )
    print("Current payload:", singlePayload)
    payloads = createMutliplePayloads(accountId, conDefList)
    for p in payloads:
        messages = placeOrder(accountId, p)

def getLiveOrderIds():
    endpoint = base_url + "/iserver/account/orders"
    response = requests.get(endpoint, verify=False, headers=headers)
    jsonData = json.loads(response.text)
    print('Orders response ----> \n  ', jsonData)
    if 'error' in jsonData.keys():
        print(jsonData['error'])
        return
    orderIds = []
    for order in jsonData['orders']:
        orderIds.append(order['orderId'])

    return orderIds

def getLiveOrders():
    endpoint = base_url + "/iserver/account/orders"
    response = requests.get(endpoint, verify=False, headers=headers)
    jsonData = json.loads(response.text)
    print('Orders response ----> \n  ', jsonData)
    if 'error' in jsonData.keys():
        print(jsonData['error'])
        return
    return jsonData 

def getOrderIdByOrderRef(order_ref):
    trades = accountTrades()
    
    return

def checkExecutionByOrderRef(order_ref):
    trades = accountTrades() 
    for trade in trades:
        try:
            if order_ref == trade['order_ref']:
                print(f"Execution: \n {trade}")
        except KeyError:
            continue

def getOrderRefs():
    orders = getLiveOrders()
    for el in orders['orders']:
        try:
#            print(f"{el['orderId']} -> {el['order_ref']}")
            # Check if order_ref is in trades:
            checkExecutionByOrderRef(el['order_ref']) 
        except KeyError:
            print(str(el['orderId']) + ' has no cOID assigned')
            continue

def retrieveOrderStatuses():

    orders = getLiveOrderIds()
    for orderId in orders:
        status = checkOrderStatus(orderId)
        with open('orderStatuses.json', 'a') as outfile:
            json.dump(status, outfile, indent=2)

def searchBySymbol(symbol: str, sectype: str):
    data = {
            "symbol": symbol,
            "name": True,
            "secType": sectype,
            }
    resp = requests.post(base_url + "/iserver/secdef/search", json=data, verify=False)
    if resp.status_code == 200:
        jsonData = json.loads(resp.text)
        contract = jsonData[0]
        print(f"---> Received contract details for {symbol}")
        return contract 
    else:
        raise RuntimeError(f"Nothing found for symbol {symbol}")

def getContractByConid(conid: str):
    print("Conid: ", conid)
    url = f"/iserver/contract/{conid}/info"
    print(url)
    resp = requests.get(base_url + url, verify=False)
    print(resp.text)
    print(resp.status_code)
    if resp.status_code == 200:
        jsonData = json.loads(resp.text)
    else:
        raise RuntimeError(f"Nothing found for conid {conid}")
    return jsonData


def checkOrderStatus(orderId):
    endpoint = f'/iserver/account/order/status/{orderId}'
    resp = requests.get(base_url + endpoint, verify=False)
    resp = json.loads(resp.text)
    return resp


def cancelOrder(accountID, orderID):
    endpoint = f'/iserver/account/{accountID}/order/{orderID}'
    if type(orderID) == list:
        orderID = ','.join(str(i) for i in orderID)
        orderID = f'[{orderID}]'
    data = {"accountId": accountID, "orderId": orderID}
    resp = requests.delete(base_url + endpoint, params=data, verify=False, headers=headers)
    jsonData = json.loads(resp.text)
    print("Cancellation message: ", jsonData)

def cancelAllOrders():
    # to cancel all orders send -1 as ID value
    orderIds = getLiveOrderIds()
    accId = getAccounts()[0]
#    cancelOrder(accId, orderIds)

    print("Cancelling orders")
    while len(orderIds) != 0:
        toCancelId = orderIds.pop(0)
        print("Cancelling order: ", toCancelId)
        cancelOrder(accId, toCancelId)

def historicalData(conid, exchange, period, bar, outsideRth, startTime): 
    params = {
            "conid": conid,
            "exchange": exchange,
            "period": period,
            "bar": bar,
            "outsideRth": outsideRth,
            "startTime": startTime
            }

    response = requests.get(base_url + '/iserver/marketdata/history', params=params, verify=False)
    print(response.status_code)
    print(response.text)

def urllLibhistoricalData(conid, exchange, period, bar, outsideRth, startTime): 
    params = {
            "conid": conid,
            "exchange": exchange,
            "period": period,
            "bar": bar,
            "outsideRth": outsideRth,
            "startTime": startTime
            }
    params1 = {
            'conid': '15016062',
            'bar': '1min',
            'startTime': '20231129-19:00:00'
            }
    endpoint = "/iserver/marketdata/history"
    url_with_params = f"{base_url}{endpoint}?{'&'.join(f'{key}={value}' for key, value in params1.items())}"
    with urllib.request.urlopen(url_with_params, context=sslContext, timeout=60) as response:
        print(response.read().decode('utf-8'))

def betaHistoricalDataQuery(conid, period, bar, outsideRTH, barType):

    endpoint = base_url + "/hmds/history"

    url = "https://localhost:5000/v1/api/hmds/history?conid=265598&period=w&bar=d&outsideRth=false" 

    payloads = [validPayload, payloadErr, payloadEmpty, payloadInvalid, payloadInvalid2, payloadInvalid3, 
            payloadInvalid4, payload2, payload3, payload4, payload5,
            payload6, payload7, payload8, payload9, payload10,
            payload11, validPayload, validPayload2, validPayload2,
            validPayload3, 
            validPayload4, validPayload5, 
            validPayload5, validPayload6]

    for p in payloads:
        response = requests.get(endpoint, params=p, verify=False)
        print("Payload: ",  p , "\n" + "Response: " + response.text + "\n")

def betaSnaphsotQuery():

    endpoint = base_url + "/md/snapshot"
    fields = "31,70,6509"

    testPatloadi0 = { 
            "conids": "14094@EUREX:CS",
            "fields": fields
            }
    testPatloadi1 = {
            "conids": "14094@EUREX:CS,265598@SMART:CS",
            "fields": fields
            }

    testPatload2 = {
            "conids": "265598",
            "fields": fields
            }

    response0 = requests.get(endpoint, params=testPatloadi0, verify=False)
    response1 = requests.get(endpoint, params=testPatloadi1, verify=False)
    response2 = requests.get(endpoint, params=testPatload2, verify=False)
    print(f"beta snapshot 0: ", response0.status_code)
    print(f"beta snapshot content: ", response0.text)
    print("\n")
    print(f"beta snapshoti 1: ", response1.status_code)
    print(f"beta snapshot content 1: ", response1.text)
    print("\n")
    print(f"beta snapshot 2: ", response2.status_code)
    print(f"beta snapshot content 2: ", response2.text)

def scannerRun(instr: str, tp: str, location: str, fltr: list):

    endpoint = base_url + "/iserver/scanner/run"

    payload = {
            "instrument": instr,
            "type": tp,
            "location": location,
            "filter": fltr
            }

    response = requests.post(endpoint, json=payload, verify=False)

    print(response.status_code)
    print(response.text)


def testPnl():

    # + 1. Start with no open positions
    # + 2. Open and close two or more positions
    # + 3. Get endDay pnl and startDay pnl
    # 4. Get realizedPnl
    # + 5. Get commissions

    accountId =  getAccounts()[0]
    # + 1. Start with no open positions
    cancelAllOrders()
    # Get start of the day pnl
    startPnl = getPnl(accountId, 'preOrdePlacement.json')
    print(startPnl)
    calculateCommission()
    # + 2. Open and close two or more positions
    ref1 = placeSingleOrder("BMW", "SMART", "BUY", "MKT", 'DAY', False, 1, 
            orderRef="BMW_BUY")

    ref2 = placeSingleOrder("BMW", "SMART", "SELL", "LMT", 'DAY', False, 1, 
            price=80, orderRef="BMW_SELL")
    # Get commisions
    commission1 = getOrderByCOID(ref1)['commission']
    executionPrice1 = getOrderByCOID(ref1)['price']
    commission2 = getOrderByCOID(ref2)['commission']
    executionPrice2 = getOrderByCOID(ref2)['price']
    print(f"Commission/Price BUY: {commission1}/{executionPrice1} ")
    print(f"Commission/Price SELL:{commission2}/{executionPrice2} ") 
    realizedPnl = (int(float(executionPrice1)) + int(float(commission1))) - (int(float(executionPrice2)) + int(float(commission2)))
    print(realizedPnl)
    calculateCommission()
    # get end of the day pnl
    endPnl = getPnl(accountId, 'afterOrderPlacement.json')
    print(endPnl)

def overallRealizedPnl():
    entryOrders, exitOrders = getCommissionsAndPositinos()
    print(entryOrders, exitOrders)
    result = (entryOrders['price'] + entryOrders['commission'] - (exitOrders['price'] + exitOrders['commission']))
    result = (exitOrders['price'] - entryOrders['price']) - (entryOrders['commission'] + exitOrders['commission']) 
    print(result)            

def realizedPnlPerTrade(buyRef, selRef):

    # to be able to calculate PNL properly 
    # Entry and close order's should carrie noteable identifiers.

    # Or sum up all BUY order prices and SELL order prices
    # Sum up all commissions 

    buyOrder = getOrderByCOID(buyRef)
    sellOrder = getOrderByCOID(selRef)

    realizedPnl = float(sellOrder['price']) - float(buyOrder['price'])
    commission = float(sellOrder['commission']) + float(buyOrder['commission'])
    netRealizedPnl = realizedPnl - commission

    altRealizedPnl = (float(sellOrder['price']) + float(sellOrder['commission'])) - (float(buyOrder['price']) + float(buyOrder['commission']))

    print("Formulas retunr same value: ", realizedPnl == altRealizedPnl)

    return netRealizedPnl 

def extractConids(portfolio: list):
    conidList = []
    for e in portfolio:
#        print(e['conid'], e['putOrCall'], e['multiplier'], e['strike'])
        conidList.append(e['conid'])
    return conidList

def getHistoricalData(conid: str, exchange=None, period=None,
        bar=None, startTime=None, outsideRth=False):

    url = "/iserver/marketdata/history"
    params = {
            'conid': conid,
            'exchange': '' if exchange is None else exchange,
            'period': '' if period is None else period,
            'bar': '' if bar is None else bar,
            'startTime': '' if startTime is None else startTime,
            'outsideRth': '' if outsideRth is None else outsideRth
            }

    response = requests.get(base_url + url, params=params, verify=False)
    print(response.text)


def getOptionStrikes(conid, month, exchange=None, secType=None):
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

def testOptionsContrac(conid, month, right, strike, exchange=None, secType=None):
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


def getOptionsContract(conid, month, right, strike, exchange=None, sectype=None):
    # Test what values are not required - sectype can be ommitted, for example.
    url = "/iserver/secdef/info"
    params = {
            "conid": conid,
            "month": month,
            "sectype": "OPT" if sectype is None else sectype, 
            "exchange": 'SMART' if exchange is None else exchange,
            "strike": strike,
            "right": right 
            }
    response = requests.get(base_url + url, params=params, verify=False)
    jsonData = json.loads(response.text)
    return jsonData

def writeJson(inp: dict, name):
    with open(f'{name}.txt', 'w') as file:
        json.dump(inp, file, indent=4)

def getUniques(rights: list, rightType: str, month, conid):
    hashMap = {}
    for r in rights:
        contract = getOptionsContract(conid, month, rightType, r) 
        if contract is not None:
            uniqueId = contract[0]['conid']
            print(uniqueId)
            #Rework pls
#            if r not in hashMap[uniqueId]:
#                hashMap[uniqueId].append(r)

        else:
            continue
    name = "puts" if rightType == "P" else "calls"        
    name += month
    writeJson(hashMap, name) 

def getOptionsChains(symbol: str):
    data = searchBySymbol(symbol, "OPT")
    conid = data['conid']
    print(conid)
    hashMap = {}
    for section in data['sections']:
        if section['secType'] == 'OPT':
            months = section['months'].split(';')
            for m in months:
                strikes = getOptionStrikes(conid, m)
                if "call" and "put" in strikes.keys():
                    print(f"Call's and Put's for {symbol}/{m}")
                    calls = [call for call in strikes['call']]
                    puts = [put for put in strikes['put']]
                    getUniques(calls, "C", m, conid)
                    getUniques(puts, "P", m, conid)
#                    print(f"Calls: \n{calls}\nPuts: \n{puts}")
#                    for c in calls:
#                        print(c)
#                        contract = getOptionsContract(conid, m, "C", c) 
#                        if contract is None:
#                            continue
#                        uniqueId = contract[0]['conid']
#                        hashMap[uniqueId] = [c] 
#                        if uniqueId in hashMap.keys():
#                            hashMap[uniqueId].append(c)

                else:
                    print("NO :(")
            print(months)
    print(hashMap)
    return hashMap

def uniqueOrderId():
    # Get portfolio details from /portfolio/positions/accountid/pageid
    accId = getAccounts()[0]
    portfolio = getPortfolioPositionsByPage(accId=accId , pageId=0)
    # Parse the response to obtain unique conids
    conidList =  extractConids(portfolio)
#    for conid in conidList:
#       getContractByConid(int(conid))
    # Close existing position using obtained conids
    print(getContractByConid("265598"))
    print(getContractByConid("0000000"))
    print(getContractByConid("658135376"))
    return

def calculatePnlPerTrade(stockSymbol: str, identifier: int):

    # Description:
    # query start of the day pnl
    # Place any BUY-SELL
    # Get end of the day pnl
    # Get netRealizedPnl of two orders
    # Run a conditional (start of the day pnl - end of the day pnl) == netRealizedPnl
    # Expected: Receive True

    accountId = getAccounts()[0]
    startPnl = getPnl(accountId)
    # Cancel all just in case
    cancelAllOrders()
    placeSingleOrder(f"{stockSymbol}", "SMART", "BUY", "MKT", 'DAY', False, 1, 
            orderRef=f"TEST{identifier}_{stockSymbol}_BUY")

    placeSingleOrder(f"{stockSymbol}", "SMART", "SELL", "LMT", 'DAY', False, 1, 
            price=60, orderRef=f"TEST{identifier}_{stockSymbol}_SELL")

    endPnl = getPnl(accountId)
    netRealizedPnl  = realizedPnlPerTrade(f"TEST{identifier}_{stockSymbol}_BUY", f"TEST{identifier}_{stockSymbol}_SELL")
    print(int(endPnl - startPnl) ==  int(netRealizedPnl))
    print(endPnl, startPnl, netRealizedPnl)

def liveOrdersDontUpdateTest():
    orders = getLiveOrderIds()
    print("Initial amount: ", len(orders))
    placeSingleOrder("GOOG", "SMART", "SELL", "MKT", "DAY", False, 1, price="", orderRef="")
    placeSingleOrder("GOOG", "SMART", "SELL", "MKT", "DAY", False, 1, price="", orderRef="")
    orders = getLiveOrderIds()
    print("After two orders were placed: ", len(orders))
    placeSingleOrder("GOOG", "SMART", "SELL", "MKT", "DAY", False, 1, price="", orderRef="")
    orders = getLiveOrderIds()
    print("One more order was placed: ", len(orders))
    cancelAllOrders()


def testOrderCancel():

    # place -> order id -> status -> order cancel -> status
    # Check if any there are any live orders and cancel them if true
    cancelAllOrders()
    placeSingleOrder("GOOG", "SMART", "SELL", "MKT", "DAY", False, 1, price="", orderRef="")
    placeSingleOrder("BMW", "SMART", "SELL", "MKT", "DAY", False, 1, price="", orderRef="")
    placeSingleOrder("GOOG", "SMART", "SELL", "MKT", "DAY", False, 1, price="", orderRef="")
    placeSingleOrder("GOOG", "SMART", "SELL", "MKT", "DAY", False, 1, price="", orderRef="")
    placeSingleOrder("BMW", "SMART", "SELL", "MKT", "DAY", False, 1, price="", orderRef="")
    placeSingleOrder("BMW", "SMART", "SELL", "MKT", "DAY", False, 1, price="", orderRef="")
    getLiveOrderIds()
    cancelAllOrders()
    print("here")
    time.sleep(5)
    getLiveOrderIds()

def testTsrvFutures():
    symbols = ['NG', 'SI', 'GD']
    booleans = ['1', 'true', 'True','0', 'false', 'False', '', '\'']
    for s in symbols:
        for b in booleans:
            getFuturesData(s, b)

def testExpiredFOPHistoricalData():
    details = getSpecificContractDetails("660316450")
    print(details)
    getHistoricalData(
            conid="660316450",
            exchange="CME",
            period="1y",
            bar="1d",
            startTime="20221201-19:00:00",
            outsideRth=False
            )

def getFOPcontracts():
    details = searchBySymbol("ES", "STK")
    sections = details['sections']
    for s in sections:
        if s['secType'] == "FOP":
            fopMonths = s['months']
            print(fopMonths)
            for m in fopMonths:
                strikesPerMonth = getOptionStrikes(conid=details['conid'], month=m, exchange="CME", 
                        secType="FOP")
                for s in strikesPerMonth['call']:
                    print(s)
                    testOptionsContrac(conid=details['conid'], right='C',
                            month=m, strike=s, exchange="CME", secType="FOP")

                for s in strikesPerMonth['put']:
                    print(s)
                    testOptionsContrac(conid=details['conid'], right='P',
                            month=m, strike=s, exchange="CME", secType="FOP")
            break
        else:
            print('Not FOP :(')

def getWARcontracts():
    details = searchBySymbol("AAPL", "STK")
    sections = details['sections']
    for s in sections:
        if s['secType'] == "WAR":
            warMonths = s['months']
            warExchanges = s['exchange']
            print(warExchanges)
            print(warMonths)
            for m in warMonths:
                strikesPerMonth = getOptionStrikes(conid=details['conid'], month=m, exchange="FWB", 
                        secType="WAR")
                print(strikesPerMonth)
                for s in strikesPerMonth['call']:
                    print(s)
                    testOptionsContrac(conid=details['conid'], right='C',
                            month=m, strike=s, exchange="FWB", secType="WAR")

                for s in strikesPerMonth['put']:
                    print(s)
                    testOptionsContrac(conid=details['conid'], right='P',
                            month=m, strike=s, exchange="FWB", secType="WAR")
            break
        else:
            print('Not WAR :(')
    return

def checkSnapshotData(conid, fields, since):
    #unsubscribe
    unsubscribeAll()
    snapShotDataSubscribe(conid, fields, since)
    try:
        while True:
            data = snapShotDataSubscribe(conid, fields, since)
            print("Data: ", data)
            if 'error' in data[0].keys():
                getAccounts()
            try:
                quotes = {
                        'bidPrice': data[0]['84'],
                        'askSize': data[0]['85'],
                        'askPrice': data[0]['86'],
                        'bidSize': data[0]['88']
                        }
                print(quotes)
            except KeyError as err:
                print("Absent value: ", err)

                continue 
            sleep(1)
    except KeyboardInterrupt:
        #unsubscribe
        sys.exit()

def helperFunction():
    trades = accountTrades()
    orderIds = []
    for el in trades:
        if "GBP.USD" in el['contract_description_1']:
            print(el)
    print(len(trades))

def main():
    checkAuthStatus()
    getWARcontracts()



if __name__ == "__main__":
    main()
