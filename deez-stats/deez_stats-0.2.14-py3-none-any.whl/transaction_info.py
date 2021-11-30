from yahoo_fantasy_api import yhandler
import deez_stats.helpers.json_query as jq
import objectpath


class TransactionInfo:
    def __init__(self, sc, league_key):
        self.sc = sc
        self.league_key = league_key
        self.yhandler = yhandler.YHandler(sc)
        self.latest_transaction_key = None
        self.latest_transaction_id = None
        self._get_latest_transation_key_id()

    def _get_latest_transation_key_id(self):
        tx = self.yhandler.get_transactions_raw(self.league_key, '', 1)
        tree = objectpath.Tree(tx)
        self.latest_transaction_key = list(tree.execute('$..transaction_key'))[0]
        self.latest_transaction_id = int(self.latest_transaction_key.split('.').pop())

    def get_transaction_info(self, transaction_id):
        uri = 'transaction/' + self.league_key + '.tr.' + str(transaction_id)
        print(uri)
        self.yhandler.get(uri)
