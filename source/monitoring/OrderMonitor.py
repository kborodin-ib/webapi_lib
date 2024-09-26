#! /usr/bin/env python3

class OrderMonitor():

    def __init__(self):
        return

    def __sampleFunction(self):
        print("This function belongs to OrderMonitor class")

    def retrieveLiveOrders(self, filters):
        print(filters)
        params = {'filters': filters}
        response = requests.get(endpoints['live_orders'], params=params, verify=False)
        try:
            jsonData = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            # Sometimes API will return an empty string which
            # json fails to parse
            print("Empty response returned, json failed to parse")
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

class AccountMonitor():

    def __init__(self):
        self.__init__ = None
