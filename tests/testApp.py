#! /usr/bin/env python3

import json
import sys
import time
import random
from cplib_v0.client import Broker, ContractDetailsManager
from cplib_v0.orderFactory import Contract, Order
from cplib_v0.orders import MktOrder, LimitOrder, CashMktOrder, TrailLimit, TrailStop, PegToMid
from cplib_v0.contract import Contract as BaseContract, Instrument
from cplib_v0.exceptions import * 
    
def basicConnectionTest():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()

def testOrderOperations():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()

    broker.showLiveOrders('PreSubmitted')

    contract = createSampleContract() 
    order = createSampleOrder()
    order.updateAccountId(broker.acctId)
    order._toJSON()
    order.JSON.update(contract.JSON)
    orderPayload = {'orders': [order.JSON] }

    json = broker.placeOrder(orderPayload)
    oid = json['order_id']
    broker.modifySingleOrder(oid, orderPayload, price=0.845, size=2) 

    broker.showLiveOrders('')

def testSnapshotFields(conids: int, flds: str):

    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    broker.unsubscribeAll()
    if broker.isAuthenticated() == True:
        broker.setAccountId()
        broker.makeMdSnapshot(conids, flds)
    else:
        print("Not authenticated")

def testTrailStopOrder():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    contract = Contract()
    contract.fillOptDetails('679322318')

    order = Order()
    order.price = 11
    order.orderType = 'TRAIL'
    order.side = 'BUY'
    order.trailingType = 'amt'
    order.trailingAmount = 2
    order.quantity = 1
    order.tif = 'GTC'
    order._toJSON()

    order.updateAccountId(broker.acctId)
    order._toJSON()
    order.JSON.update(contract.JSON)
    del order.JSON['cOID']
    del order.JSON['ticker']
    del order.JSON['referrer']
    del order.JSON['parentId']
    del order.JSON['conidex']
    order.JSON['conid'] = 679322318
    orderPayload = {'orders': [order.JSON] }
    jsonFile = json.dumps(orderPayload, indent=4)
    with open('stpPayload.txt', 'w') as outfile:
        outfile.write(jsonFile)
        outfile.close()
    print(jsonFile)
    jsonReply = broker.placeOrder(orderPayload)
    print(jsonReply)
    print(type(jsonReply))

def fillStrategyParams(algos, conid):
    return
    

def testAlgoOrder(conid):
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    contract = Contract()
    contract.fillContractDetails(conid)
    algos = contract.getAvailableAlgos(conid)
    print(f"Available algorithms for {contract.symbol}")
    for i in range(len(algos)):
        print(f'{i+1}. {algos[i]["name"]}')
    choises= [i for i in range(1, len(algos)+1)]
    choise = int(input(f"Please select algo. Available choices: {choises}"))
    print(choise)
    while choise not in choises:
        print(f"{choise} should be one of {choises}")
        choise = int(input("Please select algo: "))
    algoIdx = choise - 1
    algo = algos[algoIdx]
    print(f"You have chosen {algos[algoIdx]}")
    algoParams = contract.getAlgoParams(conid, algo['id'])
    strategyParameters = {}
    for param in algoParams[0]['parameters']:
        print("Current parameter: ", param['id'], param['valueClassName'])
        value = input(f"Specify values for {param['id']}: ")
        pair = { param['id']: value }
        strategyParameters.update(pair)

    order = Order()
    order.price = 11
    order.orderType = 'LMT'
    order.side = 'BUY'
#    order.trailingType = 'amt'
#    order.trailingAmount = 2
    order.quantity = 1
    order.tif = 'DAY'
    order.strategy = "Adaptive"
    order.cOID = 'null'
    order.strategyParameters = strategyParameters 
    order.updateAccountId(broker.acctId)
    order._toJSON()
    contract.exchange = ""
    contract._toJSON()
    print(contract.exchange)
    print(contract.JSON)
    order.JSON.update(contract.JSON)
    print(order.JSON['listingExchange'])
    orderPayload = {'orders': [order.JSON] }
    jsonFile = json.dumps(orderPayload, indent=4)
    print(jsonFile)
    with open('algoPayload.txt', 'w') as outfile:
        outfile.write(jsonFile)
        outfile.close()
    jsonReply = broker.placeOrder(orderPayload)
    print(jsonReply)
    print(type(jsonReply))

    orders = broker.showLiveOrders()

def placeAlgoOrder():

    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    vwapAlgoPayload = { 
                "acctId": "U10412366",
                "conid": 265598,
                "cOID": "MY_VERY_UNIQUE_VWAP_ORDER_FULL_PARAMS",
                "secType": "265598@STK",
                "price": 186.20,
                "orderType": "LMT",
                "outsideRTH": False,
                "side": "BUY",
                "ticker": "AAPL",
                "tif": "DAY",
                "quantity": 1,
                "strategy": "Vwap",
                "strategyParameters": {
                    "maxPctVol": 10,
                    "startTime": "14:00:00 US/Eastern",
                    "endTime": "10:00:00 US/Eastern",
                    "allowPastEndTime": True,
                    "noTakeLiq": True,
                    "speedUp": True,
                    "conditionalPrice": 180.21
                    }
                }
    twapAlgoPayload = { 
                "acctId": "U10412366",
                "conid": 265598,
                "cOID": "MY_VERY_UNIQUE_TWAP_ORDER_FULL_PARAMS",
                "secType": "265598@STK",
                "price": 186.20,
                "orderType": "LMT",
                "outsideRTH": False,
                "side": "BUY",
                "ticker": "AAPL",
                "tif": "DAY",
                "quantity": 1,
                "strategy": "Twap",
                "strategyParameters": {
                    "startTime": "14:00:00 US/Eastern",
                    "endTime": "10:00:00 US/Eastern",
                    "allowPastEndTime": True,
                    "catchUp": True,
                    "conditionalPrice": 180.21
                    }
                }
                

    payload = {
            "acctId": "U10412366",
            "conid": 265598,
            "orderType": "LMT",
            "price": 110,
            "listingExchange": "SMART",
            "side": "BUY",
            "ticker": "AAPL",
            "tif": "GTC",
            "quantity": 200,
            "outsideRTH": True 
            }
    
    orderPayload = {'orders': [twapAlgoPayload]}
    jsonData = json.dumps(orderPayload, indent=4)
    with open('validAlgoPayload.json', 'w') as outFile:
        outFile.write(jsonData)
        outFile.close()
    broker.placeOrder(orderPayload)

def placeSimpleOrder(conid):
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    payload = {
            'acctId': 'U10412366',
            'conid': int(conid),
            'orderType': 'LMT',
            'price': 110,
            'listingExchange': 'SMART',
            'side': 'BUY',
            'ticker': 'AAPL',
            'tif': 'GTC',
            'quantity': 200,
            'outsideRTH': True 
            }
    print(payload) 
    with open('randomConid.json', 'w') as outFile:
        json.dump(payload, outFile, indent=4)
    broker.placeOrder(payload)


def testWatchlists():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    broker.showWatchlists()

def testSymbolSearch():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    contract = Contract()
    contract.symbol = "AAPL"
    contract.searchSymbol()

def testOrderObject():
    mktOrder = MktOrder("BUY", 1)
    print(mktOrder)
    print(mktOrder.__dict__)

    lmtOrder = LimitOrder("BUY", 1, 1) 
    print(lmtOrder)
    print(lmtOrder.__dict__)

def testContractObject():
    contract = BaseContract("265598")
    print(contract)
    print(contract.__dict__)

def testPayload():
    contract = BaseContract("265598").__dict__
    mktOrder = MktOrder("BUY", 1).__dict__
    contract.update(mktOrder)
    print(contract)

def testChangeTif():
    mktOrder = MktOrder("BUY", 1)
    mktOrder.tif = "GTC"
    print(mktOrder)
    print(mktOrder.__dict__)

def testPlaceMktOrder(conid):
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    contract = BaseContract(conid)
    mktOrder = MktOrder("BUY", 1, tif='DAY')
    contract.__dict__.update(mktOrder.__dict__)
    payload = contract.__dict__ 
    print(payload)
    broker.placeOrder({'orders': [payload]})

def testPlaceLmtGtcOrthOrder(conid):
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    contract = BaseContract(conid)
    lmtOrder = LimitOrder("BUY",limitPrice=18, totalQuantity= 1)
    lmtOrder.tif = "GTC"
    lmtOrder.outsideRTH = True 
    contract.__dict__.update(lmtOrder.__dict__)
    payload = contract.__dict__
    print(payload)
    try:
        broker.placeOrder(payload)
    except NotAllowedOutsideRTH:
        print("this order cannot be placed with outsideRTH=True")
        response = input('Check contracts trading schedule? yes/no')
        if response == 'yes':
            inst = Instrument()
            inst.conid = conid
            inst.getContractDetails(contract)
            # Check if contract is FUT - most futures do not have
            # an outsideRTH parameter
            symbol = inst.json['ticker']
            assetClass = inst.json['secType']
            exchange = inst.json['exchange']
            # Parse response pls.
            inst.getTradingSchedule(symbol=symbol,
                    assetClass=assetClass, exchange=exchange)

def testOrderPlacementLogic():
    testOrderObject()
    testContractObject()
    testChangeTif()
    testPayload()
    testPlaceOrder()

def testPositionsPerAccount(pageid):
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    broker.showAccounts()
#    broker.account.invalidatePositions()
    broker.showPositions(pageId=pageid)

def testCanStoreStkContractsFromCompNamesJSON():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    conMan = ContractDetailsManager()
    stkContractList = conMan.stockContractsFromCompanyNames('contractCsvData/worst20SPversion2.csv')
    conMan.writeJSON('worst20SPContracts')

def testStoreContractsFromSymbol():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    conMan = ContractDetailsManager()
    stkContractList = conMan.stockContractsFromSymbols('contractCsvData/EU_tickers.csv')
    conMan.writeJSON('EU_tickers_500')

def testPlaceMultipleOrders():
    #readContactJSON useses search by company name
    # Need to count orders that were not placed due to
    # reasonse ...
    # Add 500 http error message exception
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    broker.readContactJSON('EU_tickers_500.json')
    counter = 0
    if len(broker.contracts['stocks']) != 0:
        order = MktOrder("BUY", 3)
        for stock in broker.contracts['stocks']:
            contract = BaseContract(int(stock['conid']))
            contract.__dict__.update(order.__dict__)
            try:
                broker.placeOrder(contract.__dict__)
                counter += 1
            except NoTradingPermissionError:
                print(f"---> Skipping: No trading permissions for {contract.conid}")
                continue
            except OrderRejectedDueToReasons:
                print(f"---> Skipping: Order rejected by the system {contract.conid}")
                continue

            except InternalServerError:
                print("---> Skipping Internal Server Error raised by {contract}")
                print("---> Writing faulty contract json to output")
                with open('errors/500ErrorPayload.json', 'a') as outfile:
                    outfile.dump(contract, outfile, indent=4)
                time.sleep(5)
                # Try placing same order again
                # java.lang error is returned on some occasion
                continue

            except JavaLangException:
                print(f"---> Skipping due to no contract details {contract.conid}")
                # Write the faulty contract
                with open('javaLangException.json', 'w') as outFile:
                    json.dump(contract, outfile, indent=4)
                    outfile.close()
                continue
    print(f"Placed {counter} orders")
    
def contractDetailsBySymbol():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()

def testCFDfromSymbol():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    inst = Instrument("AAPL")
    inst.getContractsBySymbol()
    inst.showFoundContracts()
    inst.getCFDContractId("NASDAQ")
    if inst.conid:
        contract = BaseContract(int(inst.conid))
        order = MktOrder("BUY", 3)
        contract.__dict__.update(order.__dict__)
        print(contract.__dict__)
        try:
            broker.placeOrder(contract.__dict__)
        except OrderRejectedDueToReasons:
            print("KONIEC")
        sys.exit()
    else:
        print("no cfd found")


def testWhatIfTimeouts():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    contract = BaseContract(265598)
    mktOrder = MktOrder("BUY", 1)
    mktOrder.tif = "GTC"
    contract.__dict__.update(mktOrder.__dict__)
    payload = contract.__dict__
    broker.whatIfplaceOrder(payload)
    broker.readContactJSON('EU_tickers_500.json')
    counter = 0
    if len(broker.contracts['stocks']) != 0:
        order = MktOrder("BUY", 3)
        while True:
            for stock in broker.contracts['stocks']:
                contract = BaseContract(int(stock['conid']))
                contract.__dict__.update(order.__dict__)
                try:
                    broker.whatIfplaceOrder(contract.__dict__)
                    counter += 1
                except InternalServerError:
                    print('Internal server error')
                    continue
                except TimeoutError:
                    print(f'timed out with {counter} whatifs')
                    sys.exit()
    print(f"finished going through {counter} whatif's")

def testHistoricalData():
    # blah
    conid = sys.argv[1]
    exchange = sys.argv[2]
    period = sys.argv[3]
    barSize = sys.argv[4]
    # Format YYYYMMDD-HH:MM:SS
    startTime = sys.argv[5]
    print(period)
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    try:
        # Check if JSON has not retured an error
        broker.getHistory(conid, exchange=exchange, period=period, 
                bar=barSize, startTime=startTime, outsideRth=True)
    except TooManyHistoricalRequests:
        print("Too many historical requests, please wait and try again later")
        sys.exit()

def testSilltStringsOfFields():
    with open('sillyTests/sillyStringOfFields.txt', 'r') as inpFile:
        fields = inpFile.read()
        print(fields)
    testSnapshotFields(fields)

def testTickleUpdatesSSOExpires():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    while True:
        sessionData = broker.keepAlive()
        print("Session will expire in: ", sessionData["ssoExpires"])
        time.sleep(60)
        broker.checkAuthStatus()
        if sessionData["ssoExpires"] == 0:
            broker.checkAuthStatus()
            print("KONIEC")
            sys.exit()
#        broker.reauthenticateSession()
    return

def testCanPlaceForexOrder(forexPair):
    # fxQty and isCcconv fields are required
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    inst = Instrument(forexPair)
    inst.getContractsBySymbol()
    inst.showFoundContracts()
    inst.assignConid()
    print(inst.conid)
    contract = BaseContract(int(inst.conid))
    contract.listingExchange = "IDEALPRO"
    contract.secType = f"{inst.conid}@IDEALPRO"
    mktOrder = LimitOrder(action="BUY", totalQuantity=1, tif="DAY", limitPrice=1.1234)
    del mktOrder.__dict__['quantity']
    mktOrder.tif = "GTC"
    mktOrder.fxQty = 25000
    mktOrder.isCcyConv = True
    contract.__dict__.update(mktOrder.__dict__)
    payload = contract.__dict__ 
    with open('fxConversionSample.json', 'w') as outFile:
        json.dump(payload, outFile, indent=4)
    print(payload)
    broker.placeOrder(payload)

def testGTDlimitOrder():
    # GTD is not a valid tif value in context of CP API
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    contract = BaseContract(143916318)
    contract.listingExchange = 'SMART'
    order = GTDLimitOrder(action='BUY', limitPrice=1.035,
            totalQuantity=20, tif="GTD", goodTillDate='20240404 16:00:00',
            expTime='20240404 17:00:00')
    contract.__dict__.update(order.__dict__)
    print(contract.__dict__)
    broker.placeOrder(contract.__dict__)

def testContractJSON(pathToJSON):
    with open(pathToJSON, 'r') as InputFile:
        contracts = json.load(InputFile)
    return contracts

def testShortableCheck():
    contracts = testContractJSON('EU_tickers_500.json')
    conids = ','.join([con['conid'] for con in contracts['stocks']][:20])
    fields = '7636,7644'
    testSnapshotFields(conids, fields)

def testPlaceCashQtyOrders(conid):
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    contract = BaseContract(conid)
    order = CashMktOrder(action="SELL", cashQty=500, tif="DAY")
#    order = MktOrder(action="SELL", totalQuantity=1, tif="DAY")
    print(contract.__dict__)
    print(order.__dict__)
    contract.__dict__.update(order.__dict__)
    print(contract.__dict__)
    broker.placeOrder({'orders': [contract.__dict__]}) 

def testTrailLimitOrder(conid):
    # Check if the fields syntax is correct "Invalid order price fields"
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    inst = Instrument('AAPL')
    inst.getContractsBySymbol()
    inst.showFoundContracts()
    inst.assignConid()
    contract = BaseContract(int(inst.conid))
    order = TrailStop(action="SELL", totalQuantity=1, tif="DAY", 
            stopPrice=1.62, trailingType='amt', trailingAmount=0.02)
    print(contract.__dict__)
    print(order.__dict__)
    contract.__dict__.update(order.__dict__)
    print(contract.__dict__)
    broker.placeOrder({'orders': [contract.__dict__]}) 


def testBracketOrder():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    instrument = Instrument('AAPL')
    instrument.getContractsBySymbol()
    instrument.assignConid()
    contract = BaseContract(int(instrument.conid))
    print(contract.__dict__)
    randomid = random.randint(1, 999)
    parentOrder = MktOrder('BUY', 1, 'DAY')
    parentOrder.outsideRth = 1
    parentOrder.__dict__.update(contract.__dict__)
    coidString = f'My_very_unique_bracket_order_{randomid}'
    parentOrder.cOID = coidString
    print("Parent order: ", parentOrder.__dict__)
    childOrder1 = TrailLimit('SELL', 170.33, 170, 1, 'GTC', '%', 10) 
    childOrder1.parentId = coidString 
    childOrder1.outsideRth = 1
    childOrder1.__dict__.update(contract.__dict__)
    print("Child order uno: ", childOrder1.__dict__)
    orderLst = [parentOrder.__dict__, childOrder1.__dict__]
    payload = {'orders': orderLst}
    broker.placeOrder(payload)
    return

def testBracketOrder():
    # Need to track confimation messages in order not to
    # confirm same one on occasion when multiple orders
    # of the same type are being placed simultaneously
    # in context of one session.
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    instrument = Instrument('AAPL')
    instrument.getContractsBySymbol()
    instrument.assignConid()
    contract = BaseContract(int(instrument.conid))
    print(contract.__dict__)
    randomid = random.randint(1, 999)
    parentOrder = LimitOrder('BUY', 170.33, 1, 'DAY')
    parentOrder.outsideRth = 1
    parentOrder.__dict__.update(contract.__dict__)
    coidString = f'My_very_unique_bracket_order_{randomid}'
    parentOrder.cOID = coidString
    print("Parent order: ", parentOrder.__dict__)
    childOrder1 = TrailLimit('SELL', 170.33, 170, 1, 'GTC', '%', 10) 
    childOrder1.parentId = coidString 
    childOrder1.outsideRth = 1
    childOrder1.__dict__.update(contract.__dict__)
    print("Child order uno: ", childOrder1.__dict__)
    childOrder2 = TrailStop('BUY', 170.33, 1, 'GTC', '%', 10)
    childOrder2.parentId = coidString
    childOrder2.outsideRth = 1
    childOrder2.__dict__.update(contract.__dict__)
    orderLst = [parentOrder.__dict__, childOrder1.__dict__, childOrder2.__dict__]
    payload = {'orders': orderLst}
    broker.placeOrder(payload)
    return

def supressMessage(mid):
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
#    broker.resetAllSuppressed()
    broker.suppressPrecautions(mid)
    return
    

def testSupressMessage():
    # "You are about to submit a stop order ..."
    # is suppressed o10331
    supressMessage('o10331')
    testBracketOrder()

def testHistoryBeta():
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    # This is the only query that works atm
    broker.getHistoryBeta(conid=265598, period='3w', bar='1d',
            outsideRth=True, barType='inventory')

def testMarketDataStuff():
    optid = '699241007'
    aapl = '265598'
    eurUSD = ' 12087792'
    bmw = '140997'
    conid = '756733'
    bmwOpt = '697011911'
    conidex = '54740723@OTCLNKECN'
    # 698514091
    testSnapshotFields(conids=f"{conidex}", flds='86,87,85,7310,7311,7308,7309')
#    testHistoricalData()
#    testHistoryBeta()

def testPegToMidOrder(conid):
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    contract = BaseContract(conid)
    mktOrder = PegToMid(
            action="BUY",
            limitPrice=1,
            totalQuantity=1,
            tif='DAY',
            auxPrice=1
            )
    mktOrder.conidex = "265598@IBKRATS"
    contract.__dict__.update(mktOrder.__dict__)
    del contract.__dict__['conid']
    payload = {'orders': [contract.__dict__]} 
    print(payload)
    broker.placeOrder(payload)

def testOCAOrder():
    broker = Broker()
    broker.isAuthenticated()
    # Pre-flight request to not use a loop
    broker.retrieveLiveOrders(filters=[])
    broker.setAccountId()
    instrument = Instrument('AMZN')
    instrument.getContractsBySymbol()
    instrument.assignConid()
    contract = BaseContract(int(instrument.conid))
    print(contract.__dict__)
    randomid = random.randint(1, 999)
    parentOrder = LimitOrder('BUY', 200, 1, 'DAY')
    parentOrder.outsideRth = 1
    parentOrder.__dict__.update(contract.__dict__)
    coidString = f'My_very_unique_bracket_order_{randomid}'
    parentOrder.cOID = coidString
    print("Parent order: ", parentOrder.__dict__)
    childOrder1 = TrailLimit('SELL', 200, 170, 1, 'GTC', '%', 10) 
    childOrder1.parentId = coidString 
    childOrder1.outsideRth = 1
    childOrder1.isSingleGroup = True
    childOrder1.__dict__.update(contract.__dict__)
    print("Child order uno: ", childOrder1.__dict__)
    childOrder2 = TrailStop('BUY', 200, 1, 'GTC', '%', 10)
    childOrder2.parentId = coidString
    childOrder2.outsideRth = 1
    childOrder2.isSingleGroup = True
    childOrder2.__dict__.update(contract.__dict__)
    orderLst = [parentOrder.__dict__, childOrder1.__dict__, childOrder2.__dict__]
    payload = {'orders': orderLst}
    broker.placeOrder(payload)

    time.sleep(2)
    print(coidString)

    orders = broker.retrieveLiveOrders(filters='')
    for o in orders['orders']:
        try:
            if o['order_ref'] == coidString:
                prntOrderId = o['orderId']
                cld1orderId = prntOrderId + 1
                cld2orderId = prntOrderId + 2
                childOrder1.price = 177
                childOrder1.size = 12
                payload = {'orders': [childOrder1.__dict__]}
                broker.modifySingleOrder(orderId=str(childOrder1), orderPayload=payload, price=175.45, size=12)
            else:
                print(coidString, o['order_ref'])
        except KeyError:
            continue
    sys.exit()

def testScanner(xml):
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    broker.scannerRun(xml)

def testContractDetailsConid(conid):
    broker = Broker()
    broker.isAuthenticated()
    broker.setAccountId()
    contract = Instrument().getContractByConid(conid)
    print(contract)
# A thingy that resolves the contract by id and subscribes to market data

def testReauth():
    broker = Broker()
    broker.connect()
    broker.setAccountId()


if __name__ == "__main__":
#    testScanner('japaneseStock.xml')
    testReauth()

    
