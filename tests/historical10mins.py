#! /usr/bin/env python3

import websockets
import requests
import logging
import urllib3
import asyncio
import ssl
import json
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.StreamHandler()
                        ]
                    )

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

def unsubscibeHistoricalData(serverID):
    msg = "umh+" + serverID 
    return msg

async def sendMessages(historicalQuery):

    queue = [] 

    try:

        async with websockets.connect("wss://" + local_ip + "/v1/api/ws", ssl=ssl_context) as websocket:
            # Session can be initialized here by using the websocket object 

            rst = await websocket.recv()
            jsonData = json.loads(rst.decode())

            # Initial request
            if queue == []:
                logging.info("Adding historical data request to queue")
                queue.append(historicalQuery)
            
            while True:
                logging.info(f"Messages queue: {queue}")

                # Sending in all messages from queue
                while len(queue) != 0:
                    currentMsg = queue.pop(0)
                    await asyncio.sleep(1)
                    await websocket.send(currentMsg)

                rst = await websocket.recv()
                jsonData = json.loads(rst.decode())
                if 'topic' in jsonData.keys():
                    
                    if 'error' in jsonData.keys() and jsonData['topic'] == 'smh':
                        logging.info(jsonData['error'])
                        sys.exit()
                    
                    if jsonData['topic'].startswith("smh+"):
                        # Server id is taken from the response
                        serverID = jsonData['serverId']
                        logging.info(f'{serverID} - Received historical data')
                        unsubHistMsg = unsubscibeHistoricalData(serverID)
                        # Since we are using pop() unsibscribe message should go first
                        # Python's list's pop() method withdraws element at index 0
                        # removing it from the list. 
                        queue.append(unsubHistMsg)
                        logging.info(f"{serverID} - Cancel historical data request added to queue")
                        logging.info(f'New historical data request added to queue')
                        queue.append(historicalQuery)
                        logging.info("Sleeping 10")
                        await asyncio.sleep(10)

    except Exception as e:
        logging.error(f"Error in websocket communication: {e}")
    
    finally:
        if websocket.open():
            websocket.close()

def testSMHrequest():
    smh_req = create_SMH_req(265598, "1d", "1hour", "trades", "%o/%c/%h/%l") 
    messages = [smh_req]
#    asyncio.get_event_loop().run_until_complete(sendMessages(messages))
    loop = asyncio.get_event_loop()
    task = loop.create_task(sendMessages(messages))
    loop.run_until_complete(task)


def main():
    testSMHrequest()

if __name__ == "__main__":
    urllib3.disable_warnings()
    try:
        main()
    except ConnectionRefusedError:
        print(f"Connection refused at {local_ip}, is the gateway running?")
