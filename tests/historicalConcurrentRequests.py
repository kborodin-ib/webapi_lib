#! /usr/bin/env python3

import requests
import ssl
import threading

sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS)
sslContext.verify_mode = ssl.CERT_NONE

requests.packages.urllib3.disable_warnings()

local_ip = "127.0.0.1:5000"
base_url = f"https://{local_ip}/v1/api"
headers = {
        "User-Agent": "python-requests/2.28.1",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Content-type": "application/json"
        }

def checkAuthStatus():
    resp = requests.get(base_url + "/iserver/auth/status", verify=False)
    print(f"[+] Auth response: {resp.text}")

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
    if response.status_code == 503:
        # Try again recursively until data is returned
        historicalData(params['conid'], params['exchange'], params['period'],
                       params['bar'], params['outsideRth'], params['startTime'])
    if response.status_code != 200:
        print(f"[{conid}] Data unavailable; HTTP status: {response.status_code}, Error: {response.text}")
    else:
        print(f"[{conid}] historical data:\n {response.text} \n")
        return

def getAllDatas(conidList):

    threads=[]

    # query params
    exchange = "SMART"
    period = "1D"
    bar = '1h'
    outsideRth = True
    startTime = ''

    for conid in conidList:
        thread = threading.Thread(target=historicalData, args=(conid,exchange,period,bar,outsideRth,startTime))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    checkAuthStatus()
    listOconnodis = [265598,14094,4350,4661,4521593,2730872]
    getAllDatas(listOconnodis)
