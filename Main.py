import discord
from discord.ext import commands
from discord.utils import get
from binance import AsyncClient, BinanceSocketManager
from music_cog import music_cog

DISCORD_TOKEN = "YOUR_DISCORD_TOKEN"
BOT_PREFIX = '*'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

alerts = {}


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
        " --> List active alerts```")


@bot.command(aliases=["p"])
async def price(ctx, symbol: str):
    client = await AsyncClient.create()
    symbol = symbol.upper()
    symbol = symbol + 'USDT'
    symbolTicker = await client.get_symbol_ticker(symbol=symbol)
    symbolPrice = '{0:g}'.format(float(symbolTicker['price']))
    await ctx.send(f"ALERT {symbol} = {symbolPrice} !!!")
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


bot.add_cog(music_cog(bot))

bot.run(DISCORD_TOKEN)
