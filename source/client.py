#! /usr/bin/env python3

import requests
import logging
import json
import time
import csv
import sys

from cplib_v0.exceptions import *
from json.decoder import JSONDecodeError
from cplib_v0.orderFactory import createSampleContract, createSampleOrder, createBracketOrder, Contract, Order
from cplib_v0.endpoints import endpoints
from cplib_v0.contract import Instrument, Contract
from cplib_v0.errorParser import errorHandler
from json.decoder import JSONDecodeError
from cplib_v0.utils import createScanner
from cplib_v0.endpoints import base_url


requests.packages.urllib3.disable_warnings()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler('app.log'),
                        logging.StreamHandler()
                        ]
                    )
logger.info('Started')

#TEST

class ContractDetailsManager():

    def __init__(self):

        self.value = None
        self.contracts = {'stocks': []} 

    def stockContractsFromCompanyNames(self, pathToCsv):
        with open(pathToCsv, 'r') as csvFile:
            csvReader = csv.reader(csvFile)
            lineCount = 0
            for line in csvReader:
                if lineCount == 0:
                    lineCount += 1
                else:
                    compName = line[1]
                    symb = line[0].split(' ')[0]
                    try:
                        inst = Instrument(symbol=symb, companyName=compName)
                        inst.getContractsByName()
                        contract = inst.json
                        self.contracts['stocks'].append(contract[0])
                    except NoContractsFoundForCompany:
                        continue
                    lineCount += 1

    def stockContractsFromSymbols(self, pathToCsv):
        with open(pathToCsv, 'r') as csvFile:
            csvReader = csv.reader(csvFile)
            lineCount = 0
            for line in csvReader:
                if lineCount == 0:
                    lineCount += 1
                else:
                    symb = line[0]
                    inst = Instrument(symbol=symb, companyName='')
                    try:
                        if lineCount > 500:
                            break
                        inst.getContractsBySymbol()
                        contract = inst.json
                        print(contract[0])
                        self.contracts['stocks'].append(contract[0])
                        lineCount += 1
                    except NoContractsFoundForSymbol:
                        continue

    def stokcContractsFromXLSX(self, pathToXLXS):
        return

    def writeJSON(self, filename):
        # Should be defined as helper method as used everywhere
        filename += '.json'
        with open(filename, 'w') as jsonFile:
            json.dump(self.contracts, jsonFile, indent=4)

    def readJSON(self):
        return

    def readTXT(self):
        return

class OrderMonitor():

    def __init__(self):
        return

    def useTheForceLuke(self):
        response = requests.get(endpoints['live_orders'], params={'force': True}, verify=False)
        if response.status_code == '200':
            logging.info("Force sent succesfully")

        try:
            jsonData = json.loads(response.text)
            return jsonData
        except json.decoder.JSONDecodeError:
            logging.debug("Force is not with one :(")

    def retrieveLiveOrders(self, filters):
        print(filters)
        params = {'filters': filters}
        response = requests.get(endpoints['live_orders'], params=params, verify=False)
        try:
            jsonData = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            # Sometimes API will return an empty string which
            # json fails to parse
            loggin.debug("Empty response from /iserver/account/orders")
            jsonData = []
        return jsonData

    def retrieveTradesHistory(self, days=''):
        params = {
                "days": days 
                }
        resp = requests.get(endpoints['trades'], params=params, verify=False)
        jsonData = json.loads(resp.text)
        with open('trades.json', 'w') as outfile:
            json.dump(jsonData, outfile, indent=2)
        return jsonData 

    def __repr__(self):
        return f'class OrderMonitor'

class Account():

    def __init__(self):
        self.id = ''

    def getId(self):
        endpoint = endpoints['accounts']
        resp = requests.get(endpoint, verify=False) 
        jsonData = json.loads(resp.text)
        accounts = jsonData['accounts']
        logging.info(f"Selected account: {accounts[0]}")
        accountId = accounts[0]
        self.id = accountId
        return self.id 
#        account = input('Select account: ')
#        while account not in accounts:
#            account = input('Select valid account: ')
#        return account 

    def getWatchlistis(self):
        endpoint = endpoints['watchlists']
        resp = requests.get(endpoint, verify=False)
        print(resp.text)

    def invalidatePositions(self):
        endpoint = endpoints['inv_positions']
        invEndpoint = endpoint.replace('ACCID', self.id)
        response = requests.post(invEndpoint, verify=False)
        jsonData = json.loads(response.text)
        try:
            if jsonData['message'] == 'success':
                print('Succesfully invalidated positions')
        except KeyError as err:
            print("Invalidation failed")

    def getCurrentAccPos(self, pageId):
        self.getAccounts()
        endpoint = endpoints['acc_positions']
        print(endpoint)
        params = {"model": '', 'size': '10', 'sort': 'a', 'direction': 'a', 'period': '1D'}
        accPositions = endpoint.replace('ACCID', self.id).replace('PAGEID', str(pageId))
        print(accPositions)
        response = requests.get(accPositions, verify=False, params=params)
        jsonData = json.loads(response.text)
        print(type(jsonData))
        print(len(jsonData))
        with open('positions.json', 'w') as outFile:
            json.dump(jsonData, outFile, indent=4)
        return jsonData

    def getAccounts(self):
        response = requests.get(endpoints['portfolio_acc'], verify=False)
        jsonData = json.loads(response.text)
        print(jsonData)

    def switch(selt):
        return

class Session():

    def __init__(self):
        self.attempts = 0
        self.isConnected = False

    def logout(self):
        headers = {"accept": "application-json"}
        data = ''
        response = requests.post(endpoints['logout'], verify=False,
                headers=headers, data=data)
        jsondData = json.loads(response.text)
        return jsondData

    def checkConnection(self):
        response = requests.get(endpoints['auth_status'], verify=False)
        jsonData = json.loads(response.text)
        return jsonData

    def keepAlive(self):
        response = requests.get(endpoint['tickle'], verify=False)
        jsonData = json.loads(response.text)
        logging.info("Tickled the session")
        return jsonData

    def getSessionExpiration(self):
        response = requests.get(endpoints['validateSSO'], verify=False)
        jsonData = json.loads(response.text)
        return jsonData

    def connect(self):
        
        try:
            endpoint = endpoints['auth_status']
            response = requests.get(endpoint, verify=False)
            if response.status_code == 401:
                raise NotLoggedIn 
            jsonData = json.loads(response.text)
            self.parseAuthResponse(jsonData)

        except NotAuthenticated:
            while self.isConnected != True or self.attempts != 5:
                self.reauthenticateSession()
                self.attempts += 1

        except CompetingSessionException:
            logging.info("Only one session is allowed per username. Reauthenticating.")
            self.reauthenticateSession()

        except NotLoggedIn:
            logger.error('Local gateway is running, but user is not logged in') 
            sys.exit()

        except requests.exceptions.ConnectionError:
            logger.debug(f"Connection error. Failed to communicate with gateway at {base_url}")
            sys.exit()

        except Exception as err:
            logging.debug(f"Authentication class exception -> {err}")

    def parseAuthResponse(self, jsonData):
        
        print("Received json:", jsonData)
        
        # This needs to be reworked as connect() is being triggered
        # during session reauthentication.

        if jsonData["connected"] != True:
            # How to handle disconnectonss
            logger.info("Not connected")
            sys.exit()

        if jsonData['authenticated'] != True and jsonData['connected'] == True:
            logger.info("Not authenticated. Reauthentication attempt.")
            self.reauthenticateSession()
            sys.exit()

        if jsonData['competing'] != False:
            logger.info('Competing session')
            # Halt the execution until logged out
            sys.exit()
        
        logger.info(f'Connected: {jsonData["connected"]}')
        logger.info(f'Competing: {jsonData["competing"]}') 
        logger.info(f'Authenticated: {jsonData["authenticated"]}') 
        self.isConnected = True

    def reauthenticateSession(self):
        print('Trying to reauthenticate the session... ')
        # Deprecated, use /ssodh/init to reauthenticate session
#        response = requests.get(endpoints['reauth'], verify=False)
        payload = {'publish': True, 'compete': True}
        response = requests.post(endpoints['ssodh_init'], json=payload, verify=False)
        try:
            jsonData = json.loads(response.text)
            self.parseAuthResponse(jsonData)
        except json.decoder.JSONDecodeError:
            if response.status_code == 401:
                logging.info('Session timeout, reauthenticate manually')
                sys.exit()


    def __repr__(self):
        return f'class Authentication'

    def keepAlive(self):
        endpoint = endpoints['tickle']
        response = requests.get(endpoint, verify=False)
        jsonData = json.loads(response.text)
        return jsonData

class MarketDataManager():

    def __init__(self):
        self.param = None

class Broker(Session, Account, OrderMonitor):

    def __init__(self):
        OrderMonitor.__init__(self)
        Session.__init__(self)
        Account.__init__(self)
        self.replies = []
        self.acctId = '' 
        self.contracts = {}
        self.orderQeue = []

    def check(self):
        Order()._Order__sampleFunction()
        OrderMonitor()._OrderMonitor__sampleFunction()

    def isAuthenticated(self):
        print('Triggered')
        data = self.checkAuthStatus()
        print(data)
        return True 

    def showLiveOrders(self, filters=''):
        orders = self.monitor.retrieveLiveOrders(filters)
        jsonRepr = json.dumps(orders, indent=4)
        with open('liveOrders.json', 'w') as outFile:
            outFile.write(jsonRepr)

                

    def secDefParams(self, symbol, secType):
        inst = Instrument(symbol)
        inst.getContractsBySymbol(symbol)
        inst.assignConid()
        inst.setChainsJSON(secType)
        inst.futSecDefInfo()
        sys.exit()
        
    #accept comma-delimeted string of id's
    #Messages are supressed during active session
    def suppressPrecautions(self, ids: str):
        print("SUPPRESS")
        jsonData = {"messageIds": ids.split(',')}
        print(jsonData)
        respose = requests.post(endpoints['suppress'], verify=False,
                json=jsonData)
        try:
            jsonResp = json.loads(respose.text)
            print(jsonResp)
            return jsonResp
        except Exception as e:
            print(e)

    def resetAllSuppressed(self):
        print("Resetting suppressed")
        response = requests.post(endpoints['resetSuppress'], verify=False)
        print(response.text)

    def showTrades(self, days=''):
        self.retrieveTradesHistory(days)

    def setAccountId(self):
        self.acctId = self.getId() 

    def showPositions(self, pageId):
        self.getCurrentAccPos(pageId)

    def processOrderResponse(self, orderData):

        for el in orderData: 

            if el == 'error':
                print(el, orderData)
                sys.exit()

            if 'error' in el.keys():
                print(f"---> Error while placing order: {jsonData['error']}")
                sys.exit()

            if type(el) == dict and "id" in el.keys():
                print("Order requires confirmation")
                time.sleep(1)
                print(orderData)
                orderData = self.confirmOrder(el['id'])
                print("Confirmation 1: ", orderData)

        return orderData 

    def __createJsonPayload(self, contract, order):
        contract.__dict__.update(order.__dict__)
        return contract.__dict__

    def placeSingleOrder(self, contract, order):
#        Expected payload:
        payload = self.__createJsonPayload(contract, order)
        ordersJSON = {'orders': [payload]}
        logging.debug(f"Sending order: {ordersJSON}")
        endpoint = endpoints['place_order'].replace('accountId', self.acctId)
        resp = requests.post(endpoint, verify=False, json=ordersJSON)
        logging.debug(resp.text)

        if resp.status_code == 200:
            order = json.loads(resp.text)
            try:
                if order['error']:
                    # Parse the error JSON here
                    errorHandler(order)

            except DuplicateOrderReference:
                logging.debug(f"{order['error']}")
                sys.exit()

            except JSONDecodeError:
                logging.debug('Rresponse object that raised JSONDecodeError: ')
                logging.debug(response.text)
                sys.exit()
                
            except TypeError:
               # Process response if no error in payload keys
               logger.debug(f"Processing the order: {payload}")
               orderData = self.processOrderResponse(order)
               try:
                   return orderData[0]
               except KeyError:
                   logging.debug(f"placeSingleOrder: empty orderData: {orderData}")

        if resp.status_code == 400:
            logging.debug(f"Failed to parse JSON: {payload}")
            sys.exit()

        if resp.status_code == 500:
            logging.debug("Writing JSON that triggered 500")
            logging.debug(contractJSON)
            time.sleep(10)
            with open('errors/500ErrorPayload.json') as outfile:
                outfile.dump(contractJSON, outfile, indent=4)
            raise IntenalServerError

        if resp.status_code == 405:
            logging.debug("Received 405. Check if session has not gone stale")
            time.sleep(5)

    def confirmOrder(self, replyId):
        data = {'confirmed': True}
        message = {}
        print("REPLY ID: ", replyId)
        endpoint = endpoints['reply'].replace('replyId', replyId)
        while 'order_id' not in message.keys():
            print("Incoming: ", message)
            response = requests.post(endpoint, verify=False, json=data)
            try:
                jsonData = json.loads(response.text)
                print("Outcoming reply endpoint response: ", jsonData)
                if type(jsonData) == list and 'id' in jsonData[0].keys():
                    print("Multiple orders payload requires confiramtions")
                    rid = jsonData[0]['id']
                    endpoint = endpoint.replace(replyId, rid)
                if jsonData['error']:
                    # Parse the error JSON here
                    errorHandler(jsonData)

            except TypeError:
                message = jsonData[0]
            except json.decoder.JSONDecodeError:
                print('Faulty response object that raised JSONDecodeError: ')
                print(response.text)
                sys.exit
    
        return message

    def modifySingleOrder(self, orderId, orderPayload, price, size):

#        if len(orderPayload['orders']) > 1:
#            print("Cant handle multiple orders at once")
#            sys.exit()
        
#        orderPayload['orders'][0]['price'] = price 
#        orderPayload['orders'][0]['size'] = size
#        del orderPayload['orders'][0]['acctId']
#        modPayload = orderPayload['orders'][0]
        endpoint = endpoints['modify'].replace('oid', orderId).replace('aid', self.acctId)
        print(orderPayload)
        for o in orderPayload['orders']:
            print(o)
            response = requests.post(endpoint, verify=False, json=o)
            order = json.loads(response.text)
            orderData = self.processOrderResponse(order)
            print("Modification: ", orderData)

    def whatIfplaceOrder(self, orderJson):
        payload = {'orders': [orderJson]}
        endpoint = endpoints['whatif'].replace('ACCID', self.acctId)
        resp = requests.post(endpoint, verify=False, json=payload)
        if resp.status_code == 200:
            order = json.loads(resp.text)
            try:
                if order['error']:
                    # Parse the error JSON here
                    errorHandler(order)
            except JSONDecodeError:
                print('Faulty response object that raised JSONDecodeError: ')
                print(response.text)
                sys.exit
            except TypeError:
                # Process response if no error in payload keys
                orderData = self.processOrderResponse(order)
                return orderData
        if resp.status_code == 500:
            print(f'[ERROR 500] {resp.text} - {orderJson}')
            errorObject = json.loads(resp.text)
            if errorObject['error'] == 'TIMEOUT':
                print('TIMEOUT HAS REACHED')
                raise TimeoutError
            with open('errors/500ErrorPayload.json', 'a') as outfile:
                json.dump(orderJson, outfile, indent=4)

    def makeMdSnapshot(self, conids, fields, since=""):
        params = {
                "conids": conids,
                "fields": fields.split(','),
                "since": since
                }
        snapshot = [] 
        while True:
            time.sleep(1)
            response = requests.get(endpoints['snapshot'], params=params, verify=False)
            jsonData = json.loads(response.text)
            ticks = jsonData[0]
            for el in jsonData:
                if el['conid'] not in snapshot:
                    snapshot.append(el)
                    print(el)
                
    def unsubscribeAll(self):
        response = requests.get(endpoints['unsubAll'], verify=False)
        print(response.text)
                        
    def unsubscribeMd(self, conid):
        data = { 'conid': conid }
        response = requests.post(endpoints['unsubscribe'], data=data, verify=False)
        print("Unsubscribed: ", response.text)

    def getHistory(self, conid, exchange, period, bar, startTime, outsideRth):
        endpoint = endpoints['history']
        params = {
                'conid': conid,
                'exchange': exchange,
                'period': period,
                'bar': bar,
                'startTime': startTime,
                'outsideRth': outsideRth
                }
        response = requests.get(endpoint, params=params, verify=False)
        try:
            jsonData = json.loads(response.text)
            if 'error' in jsonData.keys():
                errorHandler(jsonData) 
            with open('historicalSample.json', 'w') as outfile:
                json.dump(jsonData, outfile, indent=4)
                print('data stored')
                outfile.close()
        except JSONDecodeError:
            print('---> Empty response')
            print(f'---> Response length: {len(response.text)}')

    def getHistoryBeta(self, conid, period, bar, outsideRth, barType):
        endpoint = endpoints['historybeta']
        print(endpoint)
        params = {
                'conid': conid,
                'period': period,
                'bar': bar,
                'outsideRth': outsideRth,
                'barType': barType
                }
        print(params)
#        params_url = "https://localhost:5000/v1/api/hmds/history?conid=265598&period=1d&bar=1hour&outsideRth=false&barType=last"
        response = requests.get(endpoint, params=params, verify=False)
        print(response.text)
        print(response.status_code)
        try:
            jsonData = json.loads(response.text)
            print(jsonData)
        except Exception as e:
            print(e)
            sys.exit()

    def scannerRun(self, xml):
        endpoint = endpoints['scanner']
        endpoint = endpoints['hmds_scanner']
        print(endpoint)
#        scannerDict = createScanner(xml)
#        print(scannerDict)
        scannerDict = {
                'instrument': 'BOND',
                'locations': 'BOND.US',
                'scanCode': 'HIGH_BOND_ASK_YIELD_ALL',
                'secType': 'BOND',
                'delayedLocations': 'SMART',
                'filters': [{
                    'bondAskYieldAbove': 1000.00
                    }]
                }
        response = requests.post(endpoint, json=scannerDict, verify=False)
        result = json.loads(response.text)
        print(len(result['contracts']))
#        print(response.text)

    def showWatchlists(self):
        self.account.getWatchlistis()

    def showAccounts(self):
        self.account.getAccounts()

    def cancelOrder(self, orderId):
        endpoint = endpoints['cancel_order'].replace('ACCID', self.acctId).replace('OID', str(orderId))
        logging.info(f"Calling {endpoint} for cancellation")
        response = requests.delete(endpoint, verify=False)
        print(response.text)
        try:
            jsonData = json.loads(response.text)
            error = jsonData['error']
            logging.debug(f"{error}")
            raise NotFoundError
            sys.exit()
        except KeyError:
            logging.info(f"order {orderId} succesfully cancelled")


    def readContactJSON(self, pathToJSON):

        with open(pathToJSON, 'r') as InputFile:
            contracts = json.load(InputFile)

        self.contracts = contracts 

if __name__ == "__main__":
    testAlgoOrder()
