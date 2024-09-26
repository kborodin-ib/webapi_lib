#! /usr/bin/env python3

from cplib_v0.client import Session
import time
import logging

class MyBot(Session):

    def __init__(self):
        Session.__init__(self)
        self.session = Session()

def connectSession(bot):
    bot.connect()

def msToMins(t):
    expMins = int(t) / 1000 / 60
    return expMins

def msToSec(t):
    expSeconds = int(t) / 1000
    return expSeconds

def sessionExpirationTest2(bot):
    logging.info("Session expiration test")
    while True:
        sessionData = bot.getSessionExpiration()
        if len(str(sessionData['EXPIRES'])) > 6:
            logging.debug(f"SESSION: Epoch timestamp: {sessionData['EXPIRES']}")
            bot.keepAlive()
            logging.info('SESSION: Sleeping 5')
            time.sleep(5)
            continue
        ms = sessionData['EXPIRES']
        logging.debug(f"SESSION: Miliseconds till expiration: {sessionData['EXPIRES']}")
        sec = msToSec(ms)
        mins = msToMins(ms)
        logging.info(f"SESSION: Sleeping {mins} minutes")
        time.sleep(sec)



def sessionTest(bot):
    return

if __name__ == "__main__":
    bot = MyBot()
#    connectSession(bot)
    sessionExpirationTest2(bot)
