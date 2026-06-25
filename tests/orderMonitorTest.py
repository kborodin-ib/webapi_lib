#! /usr/bin/env python3

# TODO:
# 1. Get live orders for the current day
# 2. Stream live order updates
# 3. Loop order placement
# 4. Get live order updates from HTTP endpoint
# 5. Restore streaming updates


import requests
import time
import sys
import websockets
import json
import urllib3
import logging
import ssl
import asyncio
import threading

ssl_context = ssl._create_unverified_context()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(filename='orderMon.log', format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    encoding='utf-8', level=logging.DEBUG)

base_url = "https://172.23.208.1:5000/v1/api"
local_ip = "172.23.208.1:5000"
ws_topic = 'sor'
accountId = "DU6036902"

def checkAuthStatus():

    url = base_url + '/iserver/auth/status'
    response = requests.get(url, verify=False)
    print(response)
    if response.status_code == 200:
        response_json = json.loads(response.text)
        try:
            auth_status = response_json['authenticated']
            con_status = response_json['connected']
            competing = response_json['competing']
        except Exception as err:
            print(f'[+] Error: {err}')
            logging.debug(f"Failed auth: {response_json}")
            sys.exit()
        if auth_status and con_status and not competing:
            print('[+] Session established')
            logging.debug(f"Authenticated successfully")
            return True
    if response.status_code == 404:
        print(f"[+] this url {url} is invalid; 404")
        sys.exit()
    if response.status_code == 401:
        print("[+] Authenticate session first")
        sys.exit()

def getLiveOrders():
    url = '/iserver/account/orders'
    response = requests.get(base_url + url, verify=False)
    if response.status_code == 200:
        print(response.text)

async def sorLiveOrders():
    messages = ['sor']
    async with websockets.connect("wss://" + local_ip + "/v1/api/ws", ssl=ssl_context) as websocket:

        rst = await websocket.recv()
        print("Initial message: ", rst)

        msg = messages.pop(0)
        await asyncio.sleep(1)
        await websocket.send(msg)
        while True:
            rst = await websocket.recv()
            print(rst)

def run_sor_in_thread():
    asyncio.run(sorLiveOrders())


def orderLoop():
    url = base_url + f"/iserver/account/{accountId}/orders"
    order_payload = {
            "orders": [
                {
                    "conidex": "793175227",
                    "orderType": "LMT",
                    "side": "SELL",
                    "tif": "DAY",
                    "quantity": 1,
                    "price": 0.05,
                    "outsideRth": True,
                    }
                ]
            }
    while True:
        response = requests.post(url, json=order_payload, verify=False)
        if response.status_code == 200:
            print(response.text)
            resp_json = json.loads(response.text)
            if 'id' in resp_json[0].keys():
                print("requires confirmation")
                loggin.debug("Order was not submitted due to: resp_json[0]['message']")
        time.sleep(2)

def cancelAll():
    url = f"/iserver/account/{accountId}/order/-1"
    response = requests.delete(base_url + url, verify=False)
    if response.status_code == 200:
        print(response.text)

if __name__ == "__main__":
    authStatus = checkAuthStatus()
    print(authStatus)
    if authStatus:
        try:
            monitor_thread = threading.Thread(target=run_sor_in_thread)
            order_thread = threading.Thread(target=orderLoop)
            monitor_thread.start()
            time.sleep(0.5)
            order_thread.start()
            order_thread.join()
            monitor_thread.join()
        except KeyboardInterrupt as err:
            cancelAll()


#        getLiveOrders()
