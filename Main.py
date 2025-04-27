import asyncio
from asyncio import sleep
import discord
import aiohttp
from discord.ext import commands
from discord.utils import get
from binance import AsyncClient, BinanceSocketManager
from tradingview_ta import TA_Handler
from crypto_symbols import crypto_symbols
from binance_api import *

config = configparser.ConfigParser()
config.read("config.ini")
DISCORD_TOKEN = config["discord"]["token"]
binance_api_key = config["binance"]["api_key"]
binance_api_key_secret = config["binance"]["api_key_secret"]
birdeye_token = config["birdeye"]["token"]

BOT_PREFIX = '*'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)
client = discord.Client(intents=intents)
alerts = {}
solana_alerts = {}
active_solana_alerts = set()
rsi_flag = True
oi_flag = True


@bot.event
async def on_ready():
    print("Bot is ready.")


@bot.command()
async def ping(ctx):
    await ctx.send(f"Bot ping: {round(bot.latency * 1000)} ms")


@bot.command()
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)


@bot.command(aliases=["clearall"])
async def clear_all(ctx):
    await ctx.channel.purge()


@bot.command(aliases=["j"])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await ctx.send("Que bot joined your channel.")


@bot.command(aliases=["l"])
async def leave(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send("Que left your server.")
    else:
        await ctx.send("Que bot is not already on the channel.")


@bot.command(aliases=[])
async def commands(ctx):
    await ctx.send(
        "```*price(p) 'symbol' --> Learn the price of symbol\n*alert(a) 'symbol' 'price' --> Set alert\n*activealerts(aa)"
        " --> List active alerts\n*clear 'count' --> Clear last 'count' messages```")


@bot.command(aliases=["p"])
async def price(ctx, symbol: str):
    client = await AsyncClient.create()
    symbol = symbol.upper()
    symbol = symbol + 'USDT'
    symbolTicker = await client.get_symbol_ticker(symbol=symbol)
    symbolPrice = '{0:g}'.format(float(symbolTicker['price']))
    await ctx.send(f"{symbol} = {symbolPrice} !!!")
    await client.close_connection()


@bot.command(aliases=["a"])
async def alert(ctx, symbol: str, alert_price: float):
    client = await AsyncClient.create()
    bsm = BinanceSocketManager(client)
    symbol = symbol.upper()
    symbol = symbol + 'USDT'
    alerts.setdefault(symbol, [])
    alert_duo = [alert_price, client]
    alerts[symbol].append(alert_duo)
    await ctx.send(f"ALERT SET {symbol} : {alert_price}")
    first_price = 0
    async with bsm.symbol_ticker_socket(symbol=symbol) as stream:
        while True:
            res = await stream.recv()
            price = res['c']
            price = float(price)
            if first_price == 0:
                first_price = price
            if first_price < alert_price:
                if price >= alert_price:
                    await ctx.send(f"ALERT {symbol} = {alert_price} !!!")
                    for x in range(len(alerts.get(symbol))):
                        if alerts[symbol][x][0] == alert_price:
                            await alerts[symbol][x][1].close_connection()
                            del alerts[symbol][x]
                            if len(alerts[symbol]) == 0:
                                alerts.pop(symbol)
                            break
                    break
            else:
                if price <= alert_price:
                    await ctx.send(f"ALERT {symbol} = {alert_price} !!!")
                    for x in range(len(alerts.get(symbol))):
                        if alerts[symbol][x][0] == alert_price:
                            await alerts[symbol][x][1].close_connection()
                            del alerts[symbol][x]
                            if len(alerts[symbol]) == 0:
                                alerts.pop(symbol)
                            break
                    break


@alert.error
async def alert_error(ctx, error):
    await ctx.send(error + 'There are missing values for the command.')


@bot.command(aliases=['aa', 'activealerts'])
async def active_alerts(ctx):
    if len(alerts.items()) != 0:
        for key in alerts:
            prices = []
            for i in range(len(alerts.get(key))):
                prices.append(alerts.get(key)[i][0])
            await ctx.send(f"{key} : {prices}")

    else:
        await ctx.send(f"There is no active alert!")


@bot.command(aliases=['deletealert', 'da'])
async def delete_alert(ctx, symbol: str, alert_price: float):
    symbol = symbol.upper()
    symbol = symbol + 'USDT'
    for x in range(len(alerts.get(symbol))):
        if alerts[symbol][x][0] == alert_price:
            await alerts[symbol][x][1].close_connection()
            del alerts[symbol][x]
            if len(alerts[symbol]) == 0:
                alerts.pop(symbol)
            break
    await ctx.send(f"ALERT DELETED {symbol} = {alert_price} !!!")


@delete_alert.error
async def delete_alert_error(ctx, error):
    await ctx.send(error + 'There are missing values for the command.')


@bot.command(aliases=['rsi', 'rsibot'])
async def rsi_bot(ctx, time_frame: str):
    global rsi_flag
    rsi_flag = True
    await ctx.send("RSI scan started")
    while rsi_flag:
        for crypto_symbol in crypto_symbols:
            crpyto_coin = TA_Handler(
                symbol=crypto_symbol,
                screener="crypto",
                exchange="BINANCE",
                interval=time_frame
            )
            rsi_value = 0
            try:
                rsi_value = int(crpyto_coin.get_analysis().indicators.get("RSI"))
            except Exception:
                pass
            print(f"{crypto_symbol} - {time_frame} RSI: {rsi_value} !")
            if rsi_value >= 80 or rsi_value <= 15:
                await ctx.send(f"{crypto_symbol} - {time_frame} RSI: {rsi_value} !")
        if time_frame != "1m":
            await sleep(60 * 1)
        else:
            await sleep(1)


@bot.command(aliases=['rsistop', 'rsibotstop'])
async def rsi_bot_stop(ctx):
    global rsi_flag
    rsi_flag = False
    await ctx.send("RSI scan stopped")


@bot.command(aliases=['order', 'o'])
async def futures_order_open(ctx, symbol: str, size: float):
    price = get_price(symbol, binance_api_key_secret).json()["price"]
    quantity = abs(size / float(price))
    if quantity < 1:
        quantity = round(quantity, 3)
    else:
        quantity = quantity // 1
    if size > 0:
        msg = create_market_order(symbol, "BUY", "LONG", float(quantity), binance_api_key, binance_api_key_secret)
    else:
        msg = create_market_order(symbol, "SELL", "SHORT", float(quantity), binance_api_key, binance_api_key_secret)
    if len(msg.keys()) > 5:
        await ctx.send("Position opened")
    else:
        txt = "Error creating order: " + msg['msg']
        await ctx.send(txt)


@bot.command(aliases=['openpositions', 'op'])
async def print_open_positions(ctx):
    open_position_json = open_positions(binance_api_key, binance_api_key_secret)
    for position in open_position_json:
        txt = position["symbol"] + "-" + position["positionSide"] + "= " + str(
            round(float(position["unRealizedProfit"]), 2)) + "$"
        await ctx.send(txt)
    if len(open_position_json) == 0:
        await ctx.send("There are no open positions.")


@bot.command(aliases=['openinterest', 'oi'])
async def open_interest_start(ctx, period: str, multiplier: int):
    global oi_flag
    oi_flag = True
    alerted_coins = {}
    await ctx.send("Open interest scan started")
    for cr in crypto_symbols:
        alerted_coins[cr] = 99
    while oi_flag:
        for cr in crypto_symbols:
            url = 'https://fapi.binance.com/futures/data/openInterestHist?'
            params = {'symbol': cr,
                      "period": period,
                      "limit": 30}

            signature = hmac.new(
                binance_api_key_secret.encode("utf-8"), urllib.parse.urlencode(params).encode("utf-8"),
                hashlib.sha256).hexdigest()
            final_url = url + urllib.parse.urlencode(params) + "&signature=" + signature
            async with aiohttp.ClientSession() as session:
                async with session.get(final_url, headers={"Content-Type": "application/json;charset=utf-8",
                                                           "X-MBX-APIKEY": binance_api_key}) as resp:
                    r = await resp.json()
            o_i_vals = []
            for a in r:
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
                await ctx.send(print_text)
                print(print_text)
                alerted_coins[cr] = oi_mult
            await session.close()
        await sleep(300)


@bot.command(aliases=['openintereststop', 'oistop'])
async def open_interest_stop(ctx):
    global oi_flag
    oi_flag = False
    await ctx.send("Open interest scan stopped")


@bot.command(aliases=["sola"])
async def sol_alert(ctx, address: str, alert_price: float):
    solana_alerts.setdefault(address, [])
    solana_alerts[address].append(alert_price)

    alert_key = (address, alert_price)
    active_solana_alerts.add(alert_key)

    await ctx.send(f"Alert set for {address} price: {alert_price}")
    first_price = 0
    while alert_key in active_solana_alerts:
        url = 'https://public-api.birdeye.so/defi/price?'
        final_url = url + "include_liquidity=true&" + "address=" + address

        async with aiohttp.ClientSession() as session:
            async with session.get(final_url,
                                   headers={"accept": "application/json", "x-chain": "solana",
                                            "X-API-KEY": birdeye_token}) as resp:
                response = await resp.json()
            await session.close()
        price = response["data"]["value"]
        print(price)
        if first_price == 0:
            first_price = price
        if first_price < alert_price:
            if price >= alert_price:
                await ctx.send(f"!!! ALERT {address} = {alert_price} !!!")
                solana_alerts[address].remove(alert_price)
                if not solana_alerts[address]:
                    solana_alerts.pop(address)
                break
        else:
            if price <= alert_price:
                await ctx.send(f"!!! ALERT {address} = {alert_price} !!!")
                solana_alerts[address].remove(alert_price)
                if not solana_alerts[address]:
                    solana_alerts.pop(address)
                break
        await asyncio.sleep(10)


@bot.command(aliases=['solaa', 'solactivealerts'])
async def solana_active_alerts(ctx):
    if not solana_alerts:
        await ctx.send("No active alerts.")
    else:
        message = "Active alerts:\n"
        for address, prices in solana_alerts.items():
            if prices:
                message += f"{address}:\n"
                for token_price in prices:
                    message += f"  - Price: {token_price}\n"
        await ctx.send(message)


@bot.command(aliases=['deletesolalert', 'solda'])
async def delete_sol_alert(ctx, address: str, alert_price: float):
    alert_key = (address, alert_price)
    if alert_key in active_solana_alerts:
        active_solana_alerts.remove(alert_key)
        solana_alerts[address].remove(alert_price)
        if not solana_alerts[address]:
            solana_alerts.pop(address)
        await ctx.send(f"Alert for {address} at price {alert_price} has been stopped.")
    else:
        await ctx.send(f"No active alert for {address} at price {alert_price} found.")


@delete_sol_alert.error
async def delete_alert_error(ctx, error):
    await ctx.send(error + 'There are missing values for the command.')


bot.run(DISCORD_TOKEN)
