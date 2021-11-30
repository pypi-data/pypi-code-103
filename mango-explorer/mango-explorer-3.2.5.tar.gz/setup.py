# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mango',
 'mango.calculators',
 'mango.hedging',
 'mango.layouts',
 'mango.marketmaking',
 'mango.marketmaking.orderchain',
 'mango.oracles',
 'mango.oracles.ftx',
 'mango.oracles.market',
 'mango.oracles.pythnetwork',
 'mango.oracles.stub',
 'mango.simplemarketmaking']

package_data = \
{'': ['*']}

install_requires = \
['Rx>=3.2.0,<4.0.0',
 'jsons>=1.6.0,<2.0.0',
 'numpy>=1.21.4,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'pyserum>=0.5.0a0,<0.6.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.22.0,<3.0.0',
 'rxpy-backpressure>=1.0.0,<2.0.0',
 'solana>=0.18.2,<0.19.0',
 'websocket-client>=1.2.1,<2.0.0',
 'zstandard>=0.16.0,<0.17.0']

setup_kwargs = {
    'name': 'mango-explorer',
    'version': '3.2.5',
    'description': 'Python integration for https://mango.markets',
    'long_description': '# 🥭 Mango Explorer\n\n## ⚠ Warning\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n\n\n## Introduction\n\n`mango-explorer` provides Python code to interface with [Mango Markets](https://mango.markets), along with a functional [marketmaker]](docs/MarketmakingQuickstart.md).\n\nHere\'s a brief but complete example of how to place and cancel an order. [This example is runnable in your browser](https://mybinder.org/v2/gh/blockworks-foundation/mango-explorer-examples/HEAD?labpath=PlaceAndCancelOrders.ipynb)!\n\n```\nimport decimal\nimport mango\nimport os\nimport time\n\n# Load the wallet from the environment variable \'KEYPAIR\'. (Other mechanisms are available.)\nwallet = mango.Wallet(os.environ.get("KEYPAIR"))\n\n# Create a \'devnet\' Context\ncontext = mango.ContextBuilder.build(cluster_name="devnet")\n\n# Load the wallet\'s account\ngroup = mango.Group.load(context)\naccounts = mango.Account.load_all_for_owner(context, wallet.address, group)\naccount = accounts[0]\n\n# Load the market\nstub = context.market_lookup.find_by_symbol("SOL-PERP")\nmarket = mango.ensure_market_loaded(context, stub)\n\nmarket_operations = mango.create_market_operations(context, wallet, account, market, dry_run=False)\n\nprint("Orders (initial):")\nfor order in market_operations.load_orders():\n    print(order)\n\n# Go on - try to buy 1 SOL for $10.\norder = mango.Order.from_basic_info(side=mango.Side.BUY,\n                                    price=decimal.Decimal(10),\n                                    quantity=decimal.Decimal(1),\n                                    order_type=mango.OrderType.POST_ONLY)\nplaced_order = market_operations.place_order(order)\nprint("\\n\\nplaced_order\\n\\t", placed_order)\n\nprint("\\n\\nSleeping for 10 seconds...")\ntime.sleep(10)\n\nprint("\\n\\nOrders (including our new order):")\nfor order in market_operations.load_orders():\n    print(order)\n\ncancellaton_signatures = market_operations.cancel_order(placed_order)\nprint("\\n\\ncancellaton_signatures:\\n\\t", cancellaton_signatures)\n\nprint("\\n\\nSleeping for 10 seconds...")\ntime.sleep(10)\n\nprint("\\n\\nOrders (without our order):")\nfor order in market_operations.load_orders():\n    print(order)\n\n```\n\nMany more examples are provided in a separate [Github repo](https://github.com/blockworks-foundation/mango-explorer-examples) and can be [run in your browser (no installation required!) at Binder](https://mybinder.org/v2/gh/blockworks-foundation/mango-explorer-examples/HEAD).\n\n\n## Running the marketmaker\n\nThere is a [Marketmaking Quickstart](docs/MarketmakingQuickstart.md) - a walkthrough of setting up and running the marketmaker on devnet, from setting up the account, depositing tokens, to running the marketmaker itself.\n\nIt can take around 30 minutes to run through.\n\nRequirements:\n* A server with docker installed\n\n**Note** This walkthrough is devnet-only so no actual funds are used or at-risk.\n\n## References\n\n* [SolanaPy](https://github.com/michaelhly/solana-py/)\n* [PySerum](https://github.com/serum-community/pyserum/)\n* [Python Decimal Class](https://docs.python.org/3/library/decimal.html)\n* [Python Construct Library](https://construct.readthedocs.io/en/latest/)\n* [Python Observables](https://rxpy.readthedocs.io/en/latest/)\n* [RxPy Backpressure](https://github.com/daliclass/rxpy-backpressure)\n\n\n# Support\n\n[🥭 Mango Markets](https://mango.markets/) support is available at: [Docs](https://docs.mango.markets/) | [Discord](https://discord.gg/67jySBhxrg) | [Twitter](https://twitter.com/mangomarkets) | [Github](https://github.com/blockworks-foundation) | [Email](mailto:hello@blockworks.foundation)',
    'author': 'Geoff Taylor',
    'author_email': 'geoff@mango.markets',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://mango.markets',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
