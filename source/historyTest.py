#! /usr/bin/env python3

import requests
import json

# Disable SSL Warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def historicalData():
    base_url = "https://localhost:5000/v1/api/"
    endpoint = "hmds/history"

    conid="conid=47511905"
    period="period=1m"
    bar="bar=1d"
    outsideRth="outsideRth=true"
    barType="barType=inventory"

    params = "&".join([conid, period, bar,outsideRth, barType])
    request_url = "".join([base_url, endpoint, "?", params])

    hd_req = requests.get(url=request_url, verify=False)
    print(hd_req.text)
    return
    hd_json = json.dumps(hd_req.json(), indent=2)

    print(hd_req)
    print(hd_json)

if __name__ == "__main__":
    historicalData()
