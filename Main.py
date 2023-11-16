from asyncio import sleep
import discord
import configparser
from discord.ext import commands
from discord.utils import get
from binance import AsyncClient, BinanceSocketManager
from tradingview_ta import TA_Handler

from binance_api import *

config = configparser.ConfigParser()
config.read("config.ini")
DISCORD_TOKEN = config["discord"]["token"]
binance_api_key = config["binance"]["api_key"]
binance_api_key_secret = config["binance"]["api_key_secret"]

BOT_PREFIX = '*'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)
client = discord.Client(intents=intents)
alerts = {}
rsi_flag = True
crypto_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT", "ADAUSDT", "DOGEUSDT", "TRXUSDT", "LINKUSDT",
                  "MATICUSDT", "DOTUSDT", "LTCUSDT", "BCHUSDT", "SHIBUSDT", "AVAXUSDT", "XLMUSDT", "XMRUSDT",
                  "ATOMUSDT", "UNIUSDT", "ETCUSDT", "FILUSDT", "HBARUSDT", "ICPUSDT", "APTUSDT", "LDOUSDT", "VETUSDT",
                  "MKRUSDT", "QNTUSDT", "AAVEUSDT", "OPUSDT", "NEARUSDT", "ARBUSDT", "INJUSDT", "GRTUSDT", "RNDRUSDT",
                  "STXUSDT", "RUNEUSDT", "ALGOUSDT", "IMXUSDT", "AXSUSDT", "EGLDUSDT", "SANDUSDT", "MANAUSDT",
                  "XTZUSDT", "EOSUSDT", "THETAUSDT", "FTMUSDT", "NEOUSDT", "SNXUSDT", "MINAUSDT", "KAVAUSDT",
                  "FLOWUSDT", "XECUSDT", "CFXUSDT", "APEUSDT", "CHZUSDT", "GALAUSDT", "PEPEUSDT", "IOTAUSDT", "ZECUSDT",
                  "DYDXUSDT", "FXSUSDT", "TWTUSDT", "CRVUSDT", "KLAYUSDT", "GMXUSDT", "WOOUSDT", "SUIUSDT", "COMPUSDT",
                  "LUNCUSDT", "FLOKIUSDT", "ROSEUSDT", "ARUSDT", "GASUSDT", "LOOMUSDT", "TRBUSDT", "ARKUSDT",
                  "POLYXUSDT", "FETUSDT", "UNFIUSDT", "BLZUSDT"]


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
    # async with bsm.symbol_ticker_futures_socket(symbol=symbol) as stream:
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
    await ctx.send('There are missing values for the command.')


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
    await ctx.send(f"ALERT DELETED {symbol} = {alert_price}  !!!")


@delete_alert.error
async def delete_alert_error(ctx, error):
    await ctx.send('There are missing values for the command.')


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


@bot.command(aliases=['orderinfo'])
async def order(ctx):
    await ctx.send("*long/short symbol price quantity stop_price take_profit_price")


@bot.command(aliases=['long'])
async def futures_long_order(ctx, symbol: str, price: float, quantity: float, stop_price: float,
                             take_profit_price: float):
    await futures_create_order_with_sl_tp(symbol, "BUY", price, quantity, stop_price, take_profit_price,
                                          binance_api_key, binance_api_key_secret)
    await ctx.send("Order created")


bot.run(DISCORD_TOKEN)
