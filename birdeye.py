import requests


url = 'https://public-api.birdeye.so/defi/price?'

coin_address = "3WKzqdh3ZW3tP2PhAtAuDu4e1XsEzFhk7qnN8mApm3S2"
final_url = url + "include_liquidity=true&" + "address=" + coin_address

r = requests.get(final_url,
                 headers={"accept": "application/json", "x-chain": "solana",
                          "X-API-KEY": "##koy"})

response = r.json()
print(response["data"]["value"])
