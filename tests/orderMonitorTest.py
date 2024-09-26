#! /usr/bin/env python3

import time
import logging
from cplib_v0.client import Broker 
from cplib_v0.orders import LimitOrder
from cplib_v0.contract import Contract
import random
import sys

class Bot(Broker):

    def __init__(self):
        Broker.__init__(self)
        Broker.suppressPrecautions(self, 'o354,o163')

    def placeSingleLmtOrder(self, conid, action,
            price, quantity, tif, cOID=''):
        contract = Contract(conid)
        order = LimitOrder(action=action, limitPrice=price, 
                totalQuantity=quantity, tif=tif, cOID=cOID)
        response = self.placeSingleOrder(contract, order)
        return response['order_id']

    def modifyOrder(self):
        return

    def matchLiveOrderByCOID(self, orderRef, status=''):
        liveOrders = self.retrieveLiveOrders(filters=status)
        
        if len(liveOrders['orders']) != 0:
            logging.info(f"{len(liveOrders['orders'])} orders in total")
            for order in liveOrders['orders']:

                try:
                    if order['order_ref'] == orderRef:
                        logging.info(f"Retrieved order: {order['orderId']}, {order['status']}, {order['order_ref']}")
                        orderId = order['orderId']
                        return orderId

                except KeyError:
                    continue
        else: 
            logging.info("No live orders")

    def matchLiveOrderByOID(self, oid, status=''):
        liveOrders = self.retrieveLiveOrders(filters=status)
        logging.info(f"{len(liveOrders['orders'])} orders in total")
        print(len(liveOrders['orders']))
        if len(liveOrders['orders']) == 1000:
            # Filtering orders out might be a thing
            self.useTheForceLuke()
            time.sleep(5)
            liveOrders = self.retrieveLiveOrders(filters=status)
        if len(liveOrders['orders']) != 0:
            for order in liveOrders['orders']:

                try:
                    if order['orderId'] == oid:
                        logging.info(f"Retrieved order: {order['orderId']}, {order['status']}")
                        orderId = order['orderId']
                        return int(orderId)

                except KeyError:
                    continue
        else: 
            logging.info("No live orders")


    def getAllLiveOrders(self):
        liveOrders = self.retrieveLiveOrders(filters='')
        return liveOrders

    def checkLiveOrderUpdates(self, cOID=''):
        response = self.placeSingleLmtOrder(conid=265598, action="SELL", price=10,
                quantity=2, tif='GTC', cOID=cOID)
        print(f"placeSingleLmtOrder response: {response}")
#        time.sleep(2)
        oid = int(response)
        orderId = self.matchLiveOrderByOID(oid=oid, status='')
        print(type(orderId))
        logging.info(f'Attempting to cancel order with id {orderId}')
        self.cancelOrder(orderId)
        logging.info(f'Requesting the order with id {orderId} after cancellation')
#        time.sleep(2)
        orderId = self.matchLiveOrderByOID(oid=orderId, status='')
        print(f"Order id: {orderId}")
        if orderId == None:
            print("Whoopsie")
            sys.exit()

    def run(self):
        self.connect()
        # Assigns the account id of currently logged in username
        self.setAccountId()
        cOID = random.randint(0, 99999)
        while True:
            self.checkLiveOrderUpdates()
            time.sleep(1)

if __name__ == "__main__":
    bot = Bot()
    bot.run()
