import os
import sys
import toml
import shutil
import asyncio
from decimal import Decimal

# to import binance.py from the dev directory
sys.path.append("../")
import binance


class Config:
    def __init__(self, file_name, template_name):
        config_file = self.extract_config(file_name, template_name)
        self.load_config(config_file)

    def get_path(self, name):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

    def extract_config(self, file_name, template_name):
        config_file = self.get_path(file_name)
        if not os.path.isfile(config_file):
            print("config file doesn't exist, copying template!")
            shutil.copyfile(self.get_path(template_name), config_file)
        return config_file

    def load_config(self, config_file):
        config = toml.load(config_file)

        binance = config["binance"]
        self.api_key = binance["api_key"]
        self.api_secret = binance["api_secret"]


async def main(loop):
    # /!\ Never hardcode your api secrets, prefer to use a config (I love toml, yaml is fine, json works)
    # Don't forget to add your config to .gitignore and give a template
    config = Config("config.toml", "config.template.toml")
    client = binance.Client(config.api_key, config.api_secret)
    await client.load()

    order = await client.create_order(
        symbol="BTCUSDT",
        side=binance.Side.SELL,
        order_type=binance.OrderType.LIMIT,
        time_in_force=binance.TimeInForce.GTC,
        quantity=Decimal("0.0012"),  # you can use Decimals
        price="15100.00",  # or directly a string
        test=False,
    )
    print(order)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
