import calendar
import configparser
import hashlib
import hmac
import time
import urllib
import requests
from crypto_symbols import crypto_symbols

config = configparser.ConfigParser()
config.read("config.ini")
DISCORD_TOKEN = config["discord"]["token"]
binance_api_key = config["binance"]["api_key"]
binance_api_key_secret = config["binance"]["api_key_secret"]


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


def create_market_order(symbol, order_side, position_side, quantity, binance_api_key, binance_api_key_secret):
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)
    url = 'https://fapi.binance.com/fapi/v1/order?'

    params = {'symbol': symbol + "USDT",
              "side": order_side,
              "positionSide": position_side,
              "type": "MARKET",
              "quantity": quantity,
              "recvWindow": 10000,
              "timestamp": time_stamp * 1000}
    signature = hmac.new(
        binance_api_key_secret.encode("utf-8"), urllib.parse.urlencode(params).encode("utf-8"),
        hashlib.sha256).hexdigest()
    final_url = url + urllib.parse.urlencode(params) + "&signature=" + signature
    r = requests.post(final_url,
                      headers={"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": binance_api_key})
    return r.json()


def get_price(symbol, binance_api_key_secret):
    url = 'https://fapi.binance.com/fapi/v2/ticker/price?'
    params = {'symbol': symbol + "USDT"}

    signature = hmac.new(
        binance_api_key_secret.encode("utf-8"), urllib.parse.urlencode(params).encode("utf-8"),
        hashlib.sha256).hexdigest()
    final_url = url + urllib.parse.urlencode(params) + "&signature=" + signature
    r = requests.get(final_url,
                     headers={"Content-Type": "application/json;charset=utf-8",
                              "X-MBX-APIKEY": binance_api_key})
    return r


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


def open_positions(binance_api_key, binance_api_key_secret):
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)
    url = 'https://fapi.binance.com/fapi/v2/positionRisk?'
    params = {
        "timestamp": time_stamp * 1000}

    signature = hmac.new(
        binance_api_key_secret.encode("utf-8"), urllib.parse.urlencode(params).encode("utf-8"),
        hashlib.sha256).hexdigest()
    final_url = url + urllib.parse.urlencode(params) + "&signature=" + signature
    r = requests.get(final_url,
                     headers={"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": binance_api_key})
    all_positions = r.json()
    open_position_json = []
    for position in all_positions:
        if float(position["positionAmt"]) != 0.0:
            open_position_json.append(position)

    return open_position_json


# async def create_take_profit_order(symbol, order_side, order_type, quantity, price, stop_price, binance_api_key,
#                                    binance_api_key_secret):
current_GMT = time.gmtime()
time_stamp = calendar.timegm(current_GMT)
# url = 'https://fapi.binance.com/fapi/v1/depth?'
# params = {'symbol': "LINK" + "USDT",
#           "limit": 5}
#
url = 'https://fapi.binance.com/fapi/v2/ticker/price?'
params = {'symbol': "LINK" + "USDT"}

url = 'https://fapi.binance.com/fapi/v1/openInterest?'
params = {'symbol': "LINK" + "USDT"}



def open_interest_search(period, multiplier):
    alerted_coins = {}
    for cr in crypto_symbols:
        alerted_coins[cr] = 99
    while True:
        for cr in crypto_symbols:
            url = 'https://fapi.binance.com/futures/data/openInterestHist?'
            params = {'symbol': cr,
                      "period": period,
                      "limit": 30}

            signature = hmac.new(
                binance_api_key_secret.encode("utf-8"), urllib.parse.urlencode(params).encode("utf-8"),
                hashlib.sha256).hexdigest()
            final_url = url + urllib.parse.urlencode(params) + "&signature=" + signature
            r = requests.get(final_url,
                             headers={"Content-Type": "application/json;charset=utf-8",
                                      "X-MBX-APIKEY": binance_api_key})
            o_i_vals = []
            for a in r.json():
                o_i_vals.append(a["sumOpenInterest"])
            o_i_diff_vals = []
            for i in range(len(o_i_vals) - 1):
                o_i_diff_vals.append(float(o_i_vals[i + 1]) - float(o_i_vals[i]))
            o_i_diff_vals = [abs(float(item)) for item in o_i_diff_vals]
            oi_mult = alerted_coins[cr]
            time_mult = 99
            for i in range(5, len(o_i_diff_vals)):
                previous_values = o_i_diff_vals[i - 5:i]
                average = sum(previous_values) / len(previous_values)
                if average * multiplier < o_i_diff_vals[i]:
                    oi_mult = o_i_diff_vals[i] / average
                    time_mult = i
            if alerted_coins[cr] != oi_mult:
                print_text = cr + " " + str((30 - time_mult) * 5) + "min ago multiplier: " + format(oi_mult, ".2f")
                alerted_coins[cr] = oi_mult
        time.sleep(300)

# open_interest_search("5m", 5)

# a = r.json()["bids"]
# c = r.json()["asks"]
# for b in a:
#     print(b)
# print("--------")
# for b in c:
#     print(b)
