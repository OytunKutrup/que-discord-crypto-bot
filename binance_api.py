import calendar
import hashlib
import hmac
import time
import urllib
import requests


async def futures_create_order_with_sl_tp(symbol, order_side, price, quantity, stop_price, take_profit_price,
                                          binance_api_key, binance_api_key_secret):
    await create_limit_order(symbol=symbol, order_side=order_side, order_type="LIMIT", quantity=quantity, price=price,
                             binance_api_key=binance_api_key, binance_api_key_secret=binance_api_key_secret)
    await create_stop_order(symbol=symbol, order_side="SELL", order_type="STOP_MARKET", quantity=quantity,
                            stop_price=stop_price, binance_api_key=binance_api_key,
                            binance_api_key_secret=binance_api_key_secret)
    await create_take_profit_order(symbol=symbol, order_side="SELL", order_type="STOP", quantity=quantity,
                                   price=take_profit_price, stop_price=price, binance_api_key=binance_api_key,
                                   binance_api_key_secret=binance_api_key_secret)


async def create_limit_order(symbol, order_side, order_type, quantity, price, binance_api_key, binance_api_key_secret):
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)
    url = 'https://fapi.binance.com/fapi/v1/order?'
    params = {'symbol': symbol + "USDT",
              "side": order_side,
              "type": order_type,
              "quantity": quantity,
              "price": price,
              "timeInForce": "GTC",
              "recvWindow": 10000,
              "timestamp": time_stamp * 1000}

    signature = hmac.new(
        binance_api_key_secret.encode("utf-8"), urllib.parse.urlencode(params).encode("utf-8"),
        hashlib.sha256).hexdigest()
    final_url = url + urllib.parse.urlencode(params) + "&signature=" + signature
    r = requests.post(final_url,
                      headers={"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": binance_api_key})
    print(r.text)


async def create_stop_order(symbol, order_side, order_type, quantity, stop_price, binance_api_key,
                            binance_api_key_secret):
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)
    url = 'https://fapi.binance.com/fapi/v1/order?'
    params = {'symbol': symbol + "USDT",
              "side": order_side,
              "type": order_type,
              "quantity": quantity,
              "stopprice": stop_price,
              "timeInForce": "GTC",
              "reduceOnly": True,
              "recvWindow": 10000,
              "timestamp": time_stamp * 1000}

    signature = hmac.new(
        binance_api_key_secret.encode("utf-8"), urllib.parse.urlencode(params).encode("utf-8"),
        hashlib.sha256).hexdigest()
    final_url = url + urllib.parse.urlencode(params) + "&signature=" + signature
    r = requests.post(final_url,
                      headers={"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": binance_api_key})
    print(r.text)


async def create_take_profit_order(symbol, order_side, order_type, quantity, price, stop_price, binance_api_key,
                                   binance_api_key_secret):
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)
    url = 'https://fapi.binance.com/fapi/v1/order?'
    params = {'symbol': symbol + "USDT",
              "side": order_side,
              "type": order_type,
              "quantity": quantity,
              "price": price,
              "stopprice": stop_price,
              "timeInForce": "GTC",
              "reduceOnly": True,
              "recvWindow": 10000,
              "timestamp": time_stamp * 1000}

    signature = hmac.new(
        binance_api_key_secret.encode("utf-8"), urllib.parse.urlencode(params).encode("utf-8"),
        hashlib.sha256).hexdigest()
    final_url = url + urllib.parse.urlencode(params) + "&signature=" + signature
    r = requests.post(final_url,
                      headers={"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": binance_api_key})
    print(r.text)
