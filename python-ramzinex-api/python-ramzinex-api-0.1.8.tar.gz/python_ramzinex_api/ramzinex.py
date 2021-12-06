# # # # -------------------------------------------------------------------------------- # # # #
"""
This is the official python library for Ramzinex.com Cryptocurrency Exchange
Author: Mohammadreza Mirzaei
Email: mirzaeimohammadreza98@gmail.com
LinkedIn: https://www.linkedin.com/in/mohammad-reza-mirzaei/
"""
# # # # -------------------------------------------------------------------------------- # # # #
import json
from venv import logger
import pandas as pd
from datetime import datetime
import cloudscraper


# # # # -------------------------------------------------------------------------------- # # # #


class Client:
    """
    This is the official python library for Ramzinex.com Cryptocurrency Exchange
    Author: Mohammadreza Mirzaei
    Email: mirzaeimohammadreza98@gmail.com
    LinkedIn: https://www.linkedin.com/in/mohammad-reza-mirzaei/
    """

    def __init__(self, api=None):
        if api is not None:
            self.api = api  # client Ramzinex API
        else:
            pass
        self.scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        self.response_ramzinex = None

    # # # # -------------------------------------------------------------------------------- # # # #
    # # # # Public API
    # # # # -------------------------------------------------------------------------------- # # # #

    def get_prices(self):
        try:
            url = "https://publicapi.ramzinex.com/exchange/api/exchange/prices"
            self.response_ramzinex = self.scraper.get(url)
            check_response_ramzinex = json.loads(self.response_ramzinex.text)
            return check_response_ramzinex
        except Exception as e:
            return Client.error_result(self, e=e, fname="get_prices", response=self.response_ramzinex)

    def get_markets(self, pair_id=None):
        try:
            url = "https://publicapi.ramzinex.com/exchange/api/v1.0/exchange/pairs"
            if pair_id is not None:
                url += "/" + str(pair_id)
            self.response_ramzinex = self.scraper.get(url)
            check_response_ramzinex = json.loads(self.response_ramzinex.text)
            return check_response_ramzinex
        except Exception as e:
            return Client.error_result(self, e=e, fname="get_markets", response=self.response_ramzinex)

    def get_markets_turnover(self):
        gmarkets = Client.get_markets(self)
        pairs_volume, usdt_pairs_volume, irr_pairs_volume = [], [], []
        tether_price = 0
        try:
            for market in gmarkets["data"]:
                try:
                    pair_dict = {"pair": market["tv_symbol"]["ramzinex"],
                                 "base_currency_symbol": market['base_currency_symbol']["en"],
                                 "quote_currency_symbol": market['quote_currency_symbol']["en"],
                                 "quote_volume": str(market["financial"]["last24h"]['quote_volume']),
                                 "base_volume": str(market["financial"]["last24h"]['base_volume']),
                                 "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    pairs_volume.append(pair_dict)
                    if market['tv_symbol']['ramzinex'] == "usdtirr":
                        tether_price = market['sell']
                except Exception as e:
                    return Client.error_result(self, e=e, fname="get_markets_turnover")

            df = pd.DataFrame(pairs_volume)
            df_irr = df[df["quote_currency_symbol"] == "irr"]
            df_usdt = df[df["quote_currency_symbol"] == "usdt"]

            irr_markets_turnover = df_irr[['quote_volume']].astype(float).sum()['quote_volume']
            usdt_markets_turnover = df_usdt[['quote_volume']].astype(float).sum()['quote_volume']

            df_irru = df_irr[df_irr['base_currency_symbol'].isin(df_usdt['base_currency_symbol'])]
            df_irru = df_irru.reset_index(drop=True)

            iu_markets_turnover = df_irru[['quote_volume']].astype(float).sum()['quote_volume']
            percent = 100 * (usdt_markets_turnover * tether_price) / irr_markets_turnover
            percent_iu = 100 * (usdt_markets_turnover * tether_price) / iu_markets_turnover

            result_data = {"irr_MT": round(irr_markets_turnover),
                           "usdt_MT": round(usdt_markets_turnover, 2),
                           "common_irrusdt_MT": round(iu_markets_turnover, 2),
                           "percent": round(percent, 2),
                           "common_irrusdt_percent": round(percent_iu, 2),
                           "tether_price": tether_price,
                           "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           "pairs_volume": pairs_volume,
                           }
            
            result = {"status": 0, "message": "ok", "data": result_data}
            return result
        except Exception as e:
            return Client.error_result(self, e=e, fname="get_markets_turnover")

    def get_orderbooks(self):  # get ramzinex orderbook for pair
        try:
            url = "https://publicapi.ramzinex.com/exchange/api/v1.0/exchange/orderbooks/buys_sells"
            self.response_ramzinex = self.scraper.get(url=url)
            check_response_ramzinex = json.loads(self.response_ramzinex.text)
            return check_response_ramzinex
        except Exception as e:
            return Client.error_result(self, e=e, fname="get_orderbook", response=self.response_ramzinex)

    # # # # -------------------------------------------------------------------------------- # # # #
    # # # # Private API
    # # # # -------------------------------------------------------------------------------- # # # #

    def order_limit(self, price, amount, pair_id, order_type):
        try:
            url = "https://ramzinex.com/exchange/api/v1.0/exchange/users/me/orders/limit"
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.api)}
            params = {"pair_id": pair_id, "price": price, "amount": amount, "type": order_type}
            self.response_ramzinex = self.scraper.post(url=url, headers=headers, data=json.dumps(params))
            check_response_ramzinex = json.loads(self.response_ramzinex.text)
            return check_response_ramzinex
        except Exception as e:
            return Client.error_result(self, e=e, fname="order_limit", response=self.response_ramzinex)

    def order_detail(self, order_id):
        try:
            url = "https://ramzinex.com/exchange/api/v1.0/exchange/users/me/orders2/" + str(order_id)
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.api)}
            response_ramzinex = self.scraper.get(url=url, headers=headers)
            check_response_ramzinex = json.loads(response_ramzinex.text)
            return check_response_ramzinex
        except Exception as e:
            return Client.error_result(self, e=e, fname="order_detail", response=self.response_ramzinex)

    def cancel_order_ramzinex(self, order_id, api_cancel=self.api):
        try:
            url = "https://ramzinex.com/exchange/api/v1.0/exchange/users/me/orders/{0}/cancel".format(str(order_id))
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(api_cancel)}
            response_ramzinex = self.scraper.post(url=url, headers=headers)
            check_response_ramzinex = json.loads(response_ramzinex.text)
            return check_response_ramzinex
        except Exception as e:
            return Client.error_result(self, e=e, fname="order_detail", response=self.response_ramzinex)

    def close_all_open_orders(self):
        open_orders = Client.get_orders(api=self.api, states=[1])
        df = pd.DataFrame(open_orders)
        for order in df['id'].tolist():
            try:
                return Client.cancel_order_ramzinex(order_id=order)
            except Exception as e:
                return Client.error_result(self, e=e, fname="close_all_open_orders", response=self.response_ramzinex)

    def get_orders(self, limit=200, offset=0, types=None, pairs=None, currencies=None, states=None, isBuy=False):
        try:
            if states is None:
                states = []
            if currencies is None:
                currencies = []
            if pairs is None:
                pairs = []
            if types is None:
                types = []
            url = "https://ramzinex.com/exchange/api/v1.0/exchange/users/me/orders2"
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.api)}
            params = {"limit": limit, "offset": offset, "types": types, "pairs": pairs, "currencies": currencies,
                      "states": states, "isBuy": isBuy}
            response_ramzinex = self.scraper.post(url=url, headers=headers, data=json.dumps(params))
            check_response_ramzinex = json.loads(response_ramzinex.text)
            return check_response_ramzinex
        except Exception as e:
            return Client.error_result(self, e=e, fname="get_orders", response=self.response_ramzinex)

    def get_balance(self):  # check ramzinex balance
        try:
            url = "https://ramzinex.com/exchange/api/v1.0/exchange/users/me/funds/details"
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.api)}
            response_ramzinex = self.scraper.get(url=url, headers=headers)
            check_response_ramzinex = json.loads(response_ramzinex.text)
            return check_response_ramzinex
        except Exception as e:
            return Client.error_result(self, e=e, fname="get_balance", response=self.response_ramzinex)

    # # # # -------------------------------------------------------------------------------- # # # #
    # # # # Others
    # # # # -------------------------------------------------------------------------------- # # # #

    def error_result(self, e, fname, response=None):
        try:
            logger.exception(str(e))
            err = "#error #" + fname
            if response is not None:
                err += "\nstatus_code:\n" + str(response.status_code) + \
                       "\nreason:\n" + str(response.reason)
            err += "\n" + str(e)
            result = {"status": -1, "error": err, "data": None}
            return result
        except:
            result = {"status": -1, "error": "Unknown Error", "data": None}
            return result
