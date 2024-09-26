#! /usr/bin/env python3

orderString = """
        self.acctId = ""
        self.orderType = ""
        self.outsideRth = False 
        self.side = ""
        self.ticker = ""
        self.tif = ""
        self.quantity = ""
        self.cOID = ""
        self.referrer = ""
        self.parentId = ""
        self.price = "" 
        self.useAdaptive = False 
        self.trailingType = ""
        self.trailingAmount = ""
        self.strategy = ""
        self.strategyParameters = "" 
        self.auxPrice = ""
        self.JSON = {}
"""

# Not all tif values that are supported by TWS API are supported
# by REST API

class DefaultBaseOrder:

    def __init__(self, action, totalQuantity, tif, cOID=''):

        self.side = action
        self.quantity = totalQuantity
        self.tif = tif 
        self.cOID = cOID 

class CashQtyBaseOrder:

    def __init__(self, action, cashQty, tif):
        self.side = action
        self.cashQty = cashQty
        self.tif = tif

class MktOrder(DefaultBaseOrder):
    
    def __init__(self, action, totalQuantity, tif):
        DefaultBaseOrder.__init__(self, action, totalQuantity, tif)
        self.orderType = "MKT"

    def __repr__(self):
        return "Market order"

class LimitOrder(DefaultBaseOrder):

    def __init__(self, action, limitPrice, totalQuantity, tif, cOID):
        DefaultBaseOrder.__init__(self, action, totalQuantity, tif, cOID)
        self.orderType = "LMT"
        self.price = limitPrice

    def __repr__(self):
        return  "Limit order"

#class Trail():
    #TODO

class TrailStop(LimitOrder):
    
    def __init__(self, action, stopPrice, totalQuantity, tif, trailingType, trailingAmount):
        LimitOrder.__init__(self, action, stopPrice, totalQuantity, tif)
        self.orderType = "TRAIL"
        self.trailingType = trailingType
        self.trailingAmt = trailingAmount

class TrailLimit(LimitOrder):
    
    def __init__(self, action, price, auxPrice, totalQuantity, tif, trailingType, trailingAmount):
        LimitOrder.__init__(self, action, price, totalQuantity, tif)
        self.orderType = "TRAILLMT"
        self.trailingType = trailingType
        self.trailingAmt = trailingAmount
        self.auxPrice = auxPrice

class CashMktOrder(CashQtyBaseOrder):
    
    def __init__(self, action, cashQty, tif):
        CashQtyBaseOrder.__init__(self, action, cashQty, tif)
        self.orderType = "MKT"

class GTDLimitOrder(LimitOrder):
    def __init__(self, action, limitPrice, totalQuantity, tif, gdUntl, expTime):
        LimitOrder.__init__(self, action, limitPrice, totalQuantity, tif)
        self.goodTillDate = gdUntl 
        self.expireTime = expireTime 

class FxMktOrder(MktOrder):
    # needs isCcyConv: True
    def __init__(self):
        return

class FxLimitOrder(MktOrder):
    # isCcyConv: True and fxQty instead of totalQuantity
    def __init__(self):
        return


# IBKRATS orders, only for US stocks trading above 1$ and
# only non-marketable orders
# Order type Pegged to Mid is not supported 

class PegToMid(LimitOrder):

    def __init__(self, action, limitPrice, auxPrice, totalQuantity, tif):
        LimitOrder.__init__(self, action, limitPrice, totalQuantity, tif)
        self.orderType = 'PEG MID'
        self.auxPrice = auxPrice































