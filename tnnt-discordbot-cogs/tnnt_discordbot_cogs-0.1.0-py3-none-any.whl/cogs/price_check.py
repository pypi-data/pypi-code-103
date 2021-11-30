"""
Market Price Checks
"""

import logging

import requests
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands

logger = logging.getLogger(__name__)


class PriceCheck(commands.Cog):
    """
    Price checks on Jita and Amarr markets
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def price(self, ctx):
        """
        Check an item price on Jita and Amarr market
        :param ctx:
        :return:
        """

        markets = [
            {"name": "Jita", "api_key": "jita"},
            {"name": "Amarr", "api_key": "amarr"},
        ]

        await ctx.trigger_typing()

        item_name = ctx.message.content[7:]

        await self.price_check(ctx=ctx, markets=markets, item_name=item_name)

    @commands.command(pass_context=True)
    async def jita(self, ctx):
        """
        Check an item price on Jita market
        :param ctx:
        :return:
        """

        markets = [
            {"name": "Jita", "api_key": "jita"},
        ]

        await ctx.trigger_typing()

        item_name = ctx.message.content[6:]

        await self.price_check(ctx=ctx, markets=markets, item_name=item_name)

    @commands.command(pass_context=True)
    async def amarr(self, ctx):
        """
        Check an item price on Amarr market
        :param ctx:
        :return:
        """

        markets = [
            {"name": "Amarr", "api_key": "amarr"},
        ]

        await ctx.trigger_typing()

        item_name = ctx.message.content[7:]

        await self.price_check(ctx=ctx, markets=markets, item_name=item_name)

    async def price_check(self, ctx, markets, item_name: str = None):
        """
        Do the price checks and post to Discord
        :param ctx:
        :param markets:
        :param item_name:
        :return:
        """

        has_thumbnail = False

        await ctx.trigger_typing()

        if item_name != "":
            embed = Embed(
                title=f"Price Lookup for {item_name}",
                color=Color.green(),
            )

            for market in markets:
                embed.add_field(
                    name="{market_name} Market".format(market_name=market["name"]),
                    value="Prices for {item_name} on the {market_name} Market.".format(
                        item_name=item_name, market_name=market["name"]
                    ),
                    inline=False,
                )

                market_data = requests.post(
                    "https://evepraisal.com/appraisal/structured.json",
                    json={
                        "market_name": market["api_key"],
                        "items": [{"name": item_name}],
                    },
                )

                if market_data.status_code == 200:
                    market_json = market_data.json()

                    if has_thumbnail is False:
                        embed.set_thumbnail(
                            url=(
                                "{imageserver_url}/types/{type_id}/icon?size=64"
                            ).format(
                                imageserver_url="https://images.evetech.net",
                                type_id=market_json["appraisal"]["items"][0]["typeID"],
                            )
                        )

                        has_thumbnail = True

                    # Sell order price
                    market_api_sell_price = market_json["appraisal"]["items"][0][
                        "prices"
                    ]["sell"]["min"]
                    market_sell_order_price = f"{market_api_sell_price:,} ISK"

                    if (
                        market_json["appraisal"]["items"][0]["prices"]["sell"][
                            "order_count"
                        ]
                        == 0
                    ):
                        market_sell_order_price = "No sell orders found"

                    embed.add_field(
                        name="Sell Order Price",
                        value=market_sell_order_price,
                        inline=True,
                    )

                    # Buy order price
                    market_api_buy_price = market_json["appraisal"]["items"][0][
                        "prices"
                    ]["buy"]["max"]
                    market_buy_order_price = f"{market_api_buy_price:,} ISK"

                    if (
                        market_json["appraisal"]["items"][0]["prices"]["buy"][
                            "order_count"
                        ]
                        == 0
                    ):
                        market_buy_order_price = "No buy orders found"

                    embed.add_field(
                        name="Buy Order Price",
                        value=market_buy_order_price,
                        inline=True,
                    )
                else:
                    embed.add_field(
                        name="API Error",
                        value=(
                            "Couldn't not fetch the price for the {market_name} market."
                        ).format(market_name=market["name"]),
                        inline=False,
                    )
        else:
            embed = Embed(
                title="Price Lookup",
                color=Color.red(),
            )

            embed.add_field(
                name="Error",
                value=(
                    "You forget to enter an item you want to lookup the price for ..."
                ),
                inline=False,
            )

        return await ctx.send(embed=embed)


def setup(bot):
    """
    Add the cogg
    :param bot:
    :return:
    """

    bot.add_cog(PriceCheck(bot))
