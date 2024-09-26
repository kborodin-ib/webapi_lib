#! /usr/bin/env python3

from sqlalchemy import create_engine, text

class dB():

    def __init__(self):
        self.engine = None

    def createEngine(self):
        self.engine = create_engine("sqlite:///ordersDb.db:", echo=True)

    def createOrdersTable(self):
        statement = """
        CREATE TABLE IF NOT EXISTS orders(
        orderId INTEGER PRIMARY KEY,
        orderRef TEXT UNIQUE NOT NULL,
        orderStatus TEXT NOT NULL CHECK(orderStatus IN ('Submitted',
        'PreSubmitted', 'Cancelled', 'Rejected'))
        );
        """
        sqlStatement = text(statement)
        
        conn = self.engine.connect()
        conn.execute(sqlStatement)
        conn.commit()
        conn.close()

    def writeOrder(sel, orderData):

if __name__ == "__main__":
    db = dB()
    db.createEngine()
    db.createOrdersTable()
