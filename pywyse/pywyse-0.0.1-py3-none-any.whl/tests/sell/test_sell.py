from pywyse.sell import Sell
from pywyse.project import Project
import pytest 

def test_sell():

    quotes = Sell().get_quotes(pageSize=10)
    assert isinstance(quotes, list)
    assert len(quotes) == 10

    project = Project().get_open_projects()
    sell_id = Sell().translate(project[10]['opportunity'].get('id', ''))
    assert isinstance(sell_id, list)
    assert len(sell_id) == 1

    sell_quote = Sell().get_quote(id = sell_id[0]['id'])
    assert isinstance(sell_quote, dict)
    
