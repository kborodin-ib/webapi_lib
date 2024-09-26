#! /usr/bin/env python3

local_ip = "127.0.0.1"
port = 5000
base_url = f"https://{local_ip}:{port}/v1/api"

# Static and dynamic endpoints

endpoints = {
        'reauth': base_url + '/iserver/reauthenticate',
        'auth_status': base_url + '/iserver/auth/status',
        'accounts': base_url + '/iserver/accounts',
        'place_order': base_url + f'/iserver/account/accountId/orders',
        'reply': base_url + f'/iserver/reply/replyId',
        'cancel_order': base_url + f'/iserver/account/ACCID/order/OID', 
        'trades': base_url + '/iserver/account/trades',
        'modify': base_url + '/iserver/account/aid/order/oid',
        'snapshot': base_url + '/iserver/marketdata/snapshot',
        'unsubscribe': base_url + '/iserver/marketdata/unsubscribe',
        'unsubAll': base_url + '/iserver/marketdata/unsubscribeall',
        'live_orders': base_url + '/iserver/account/orders',
        'watchlists': base_url + '/iserver/watchlists',
        'secdefid': base_url + '/iserver/contract/coid/info',
        'algorithms': base_url + '/iserver/contract/conid/algos',
        'cont_by_symbol': base_url + '/iserver/secdef/search',
        'secDef_by_cid': base_url + '/iserver/secdef/info',
        'strikes': base_url + '/iserver/secdef/strikes',
        'portfolio_acc': base_url + '/portfolio/accounts',
        'acc_positions': base_url + '/portfolio/ACCID/positions/PAGEID',
        'inv_positions': base_url + '/portfolio/ACCID/positions/invalidate',
        'whatif': base_url + '/iserver/account/ACCID/orders/whatif',
        'history': base_url + '/iserver/marketdata/history',
        'historybeta': base_url + '/hmds/history',
        'tradingSchedule': base_url + '/trsrv/secdef/schedule',
        'ssodh_init': base_url + '/iserver/auth/ssodh/init',
        'tickle': base_url + '/tickle',
        'suppress': base_url +'/iserver/questions/suppress',
        'resetSuppress': base_url + '/iserver/questions/suppress/reset',
        'scanner': base_url + "/iserver/scanner/run",
        'hmds_scanner': base_url + "/hmds/scanner/run",
        }
