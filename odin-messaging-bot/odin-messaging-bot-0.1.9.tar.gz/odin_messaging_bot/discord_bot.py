import aiohttp
import logging
import datetime

from typing import List
from dataclasses import dataclass

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s:%(asctime)s:%(message)s")

COLOR_PALLETE = {
    "red": 0xFD0061,
    "green": 0x00D166,
    "blue": 0x0099E1,
    "orange": 0xF93A2F,
    "gray": 0x979C9F,
    "purple1": 0xA652BB,
    "purple2": 0x7A2F8F,
}


def get_embed(title: str, color: str, fields: List):
    embed = {
        "title": title,
        "timestamp": str(datetime.datetime.utcnow()),
        "color": COLOR_PALLETE[color],
        "fields": fields,
    }
    return embed


@dataclass
class DiscordBot:
    botname: str
    url: str

    async def send_discord_message(self, embeds: List):
        try:

            payload = {
                "username": self.botname,
                "embeds": embeds,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=payload) as resp:
                    logging.info(f"Sending Payload To Discord - {resp.status}")
                    text = await resp.text()
                    logging.debug(text)
        except Exception as err:
            logging.debug(err)
            raise err

    async def send_embeded_field(self, field_name: str, field_value: str,  description: str):
        try:
            field = [
                {
                    "name": field_name,
                    "value": field_value,
                }
            ]
            embed = get_embed(title=description, color="orange", fields=field)
            await self.send_discord_message(embeds=[embed])
            logging.info("Sent New Transaction to discord")
        except Exception as err:
            logging.debug(err)
            raise err

    # async def send_balance(self, wallets: List[Wallet], balance: Balance):
    #     try:
    #         fields = []
    #         balance_field = {"name": "General Balance", "value": str(balance)}
    #         fields.append(balance_field)

    #         for wallet in wallets:
    #             wallet_field = {
    #                 "name": wallet.exchange.upper(), "value": str(wallet)}
    #             fields.append(wallet_field)

    #         embed = get_embed(title="New Balance",
    #                           color="purple2", fields=fields)

    #         await self.send_discord_message(embeds=[embed])
    #         logging.info("Sent Balance to Discord")
    #     except Exception as err:
    #         logging.debug(err)
    #         raise err

    # async def send_error_message(self, microservice: str, error_message: str):
    #     try:
    #         fields = [
    #             {
    #                 "name": f"Error in {microservice}",
    #                 "value": f" Message: {error_message}",
    #             }
    #         ]

    #         embed = get_embed(title="Error Message",
    #                           color="red", fields=fields)
    #         await self.send_discord_message(embeds=[embed])
    #         logging.info("Sent Error Message")

    #     except Exception as err:
    #         logging.debug(err)
    #         raise err

    # async def send_unbalance(self, unbalanced_field: str, target_exchange: str):
    #     try:
    #         fields = [
    #             {
    #                 "name": f"Unbalanced in { target_exchange.upper() }",
    #                 "value": unbalanced_field,
    #             }
    #         ]
    #         embed = get_embed(title="Unbalanced Wallet",
    #                           color="red", fields=fields)
    #         await self.send_discord_message(embeds=[embed])
    #         logging.info(f"Sent unbalance to discord")
    #     except Exception as err:
    #         logging.debug(err)
    #         raise err
