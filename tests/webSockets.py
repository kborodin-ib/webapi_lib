#! /usr/bin/env python3

import asyncio
import ssl
import json
import requests
import websockets
import urllib3
import sys
from datetime import datetime as dt
import arrow

# Uverified context is required in order to ignore certificate check
ssl_context = ssl._create_unverified_context()

local_ip = "127.0.0.1:5000"
base_url = f"https://{local_ip}/v1/api"

#Historical data payload:
def create_SMH_req(conID, period, barSize, dataType, dateFormat):
    msg = f"smh+{conID}+" + json.dumps({
        "period": period,
        "bar": barSize,
        "source": dataType,
        "format": dateFormat 
        }) 
    return msg

def authStatus():
    resp = requests.post(base_url + "/iserver/auth/status", verify=False) 
    if resp.status_code == 200:
        print(resp.text)
    else:
        raise RuntimeError(f"Received http status code: {resp.status_code}")


def getAccountId():
    resp = requests.get(base_url + "/iserver/accounts", verify=False) 
    if resp.status_code == 200:
        jsonData = json.loads(resp.text)
        accounts = jsonData['accounts']
        return accounts
    else:
        print(resp.status_code, resp.text)
        raise RuntimeError("!???")

def searchBySymbol(symbol: str, sectype: str):
    data = {
            "symbol": symbol,
            "name": True,
            "secType": sectype,
            }
    resp = requests.post(base_url + "/iserver/secdef/search", json=data, verify=False)
    if resp.status_code == 200:
        jsonData = json.loads(resp.text)
        conid = jsonData[0]['conid']
        return conid
    else:
        raise RuntimeError(f"Nothing found for symbol {symbol} because of response status code: {resp.status_code}")

def getContractDetails(conId):
    endpoint = f"/iserver/contract/{conId}/info"
    data = {"conid": conId}
    resp = requests.get(base_url + endpoint, verify=False, params=data)
    if resp.status_code == 200:
        jsonData = json.loads(resp.text)
        return jsonData
    else:
        raise RuntimeError(f"No contracts found for {conId}")

# Streaming data request, accepts comma-separated values
def create_SMD_req(conId, args: str):
    args = args.split(',')
    msg = "smd+" + conId + '+' + '{"fields":["31","83"]}'
    msg = "smd+" + conId + '+' + json.dumps({"fields":args})
    s = 'smh+265598+{\"bar\": "1min", "format": "format"}'
    print(msg)
    return msg

# Need to provide at least conId or symbol-sectype pair
def marketDepthRequest(symbol=None, secType=None, conID=None, acctID=None, exchange=None):

    if conID is None:
        conID = searchBySymbol(symbol, secType)

    if acctID is None:
        acctIDs = getAccountId()
        acctID = acctIDs[0]

    if exchange is None:
        details = getContractDetails(conID)
        exchange = details['exchange']

    msg = f"sbd+{acctID}+{conID}+{exchange}"

    return msg 


# Live order updates request
def create_SOR_req():
    msg = "sor+{}"
    return msg

def hdrMsg(conID, period, barSize, source, dateFormat):
    msg = f"hdr+{conID}+" + json.dumps({
        "period": period,
        "bar": barSize,
        "source": source,
        "format": dateFormat,
#        "startTime": startTime
        }) 
    return msg

def create_STR_req():
    msg = 'str+{\'realtimeUpdatesOnl\': true, \'days\': \'\'}'
    return msg

def unsubscibeHistoricalData(serverID):
    msg = "umh+" + serverID 
    return msg

def createRequests(conIdList=None):
    msgList = []
    if conIdList != None:
        for conid in conIdList:
            smd_req = create_SMD_req(conid, "31, 84, 86")
            msgList.append(smd_req)
#   Example of websocket messages:
    smh_req = create_SMH_req(conId, "1d", "1hour", "trades", "%o/%c/%h/%l") 
    sor_req = create_SOR_req()
    str_req = create_STR_req()
    mktDpthReq1 = marketDepthRequest(conId) 

    return msgList

def conditionalOrder():
    return


async def sendMessages(msgList):

    messages = msgList 
    mktDepthUnsubscribed = False
    historicalDataUnsubscribed = False

    async with websockets.connect("wss://" + local_ip + "/v1/api/ws", ssl=ssl_context) as websocket:
        # Session can be initialized here by using the websocket object 

        rst = await websocket.recv()
        jsonData = json.loads(rst.decode())
        try:
            if jsonData['message'] == 'waiting for session':
                print('No active sessions found. Are you logged in?')
                sys.exit()
        except KeyError:
            print(f"First received message: {jsonData}")
            pass

        while True:
            if len(messages) != 0:
                # *Imitates queue* 
                currentMsg = messages.pop(0)
                await asyncio.sleep(1)
                await websocket.send(currentMsg)

            rst = await websocket.recv()
            jsonData = json.loads(rst.decode())
            
            print(jsonData)
            if 'topic' in jsonData.keys():
                
                if jsonData['topic'] == 'str':
                    with open('tradesData.json', 'w') as file:
                        json.dump(jsonData, file, indent=4)
                    print(jsonData)

                if jsonData['topic'].startswith("smh+") and historicalDataUnsubscribed == False:
                    serverID = jsonData['serverId']
                    msg = unsubscibeHistoricalData(serverID)
                    messages.append(msg)
                    historicalDataUnsubscribed = True
                    print("historical data should be unsubscribed now")

                if jsonData['topic'].startswith("sbd"):
                    print("market depth --> ", jsonData['topic'])

                if jsonData['topic'] == 'sor':
                    response = f"{jsonData['topic']} -->{jsonData}" 
                    print(response)
                    

                if jsonData['topic'] == "sbd" and mktDepthUnsubscribed == False:
                    print(jsonData)
                
                if jsonData['topic'].startswith('smd'):
                    timestamp = jsonData['_updated']
                    updateTime = arrow.get(timestamp).datetime
                    timeNow = dt.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    print("INCOMING")
                    print(f'Updated at: {updateTime}')
                    print(f'Received at: {timeNow}')
                    print(f'tick: {jsonData}')
                    print("END")


                if jsonData['topic'] == "system": 
                    # Keep session alive 
                    messages.append('tic')

                if 'hdr' in jsonData['topic']:
                    print("what")
                    print(jsonData)

            if 'error' in jsonData.keys():
                print(jsonData['error'])

def testMktDepthRequests():
    symbols = [("BMW", "STK"),("AAPL", "STK")]
    messages = []
    for s in symbols:
        msg = marketDepthRequest(symbol=s[0], secType=s[1])
        messages.append(msg)
    asyncio.get_event_loop().run_until_complete(sendMessages(messages))

def testHdrRequest():
    hdr = hdrMsg('265598', period = '5min', barSize='5min', source='trades',
            dateFormat='%o/%c/%h/%l')
    messages = [hdr]
    asyncio.get_event_loop().run_until_complete(sendMessages(messages))

def liveOrderUpdates():
    msg = create_STR_req()
    print(type(msg))
    messages = [msg]
    asyncio.get_event_loop().run_until_complete(sendMessages(messages))

def liveMarketData():
    msg = create_SMD_req('380912689', '6509,7308,7309,7310,7311')
    print(type(msg))
    messages = [msg]
    asyncio.get_event_loop().run_until_complete(sendMessages(messages))

def tesLiveOrderUpdates():
    msg = create_SOR_req()
    messages = [msg]
    asyncio.get_event_loop().run_until_complete(sendMessages(messages))

def testSMHrequest():
    smh_req = create_SMH_req(265598, "1d", "1hour", "trades", "%o/%c/%h/%l") 
    messages = [smh_req]
    asyncio.get_event_loop().run_until_complete(sendMessages(messages))


def main():
    testSMHrequest()

if __name__ == "__main__":
    urllib3.disable_warnings()
    try:
        main()
    except ConnectionRefusedError:
        print(f"Connection refused at {local_ip}, is the gateway running?")
