# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['warehut']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'warehut',
    'version': '3.2.1',
    'description': 'Manage producer and consumer workers',
    'long_description': '# warehut\n\n## Installation\n```sh\npip install warehut\n```\n\n## Example\n\n```py\nimport time\nimport datetime\nimport random\n\nfrom warehut import Warehut\nfrom warehut import Producer\nfrom warehut import Consumer, listen\n\n# There also exists a `Hybrid` worker,\n# that can both listen to events and\n# when responding, can forward to other consumers.\n# Use this with caution and consideration.\n\nfrom warehut.worker import Worker\n\n\n\nclass MyWarehut(Warehut):\n    def handle_error(self, worker_type: type[Worker], exception: Exception):\n        # Handle exception raised within a worker process\n        # You could launch a window, write the error to a log file, etc.\n\n        # Stopping all other workers\n        self.stop()\n\n        # And printing the error\n        print(\n            f\'\\nWorker of type {worker_type.__name__} \'\n            f\'encountered an error.\\n{exception!r}\\n\')\n\n\n\nclass MyProducer(Producer):\n\n    async def __aenter__(self):\n        print(f\'Preparing environment for {self}\')\n\n    async def __aexit__(self, exc_type, exc_value, trace):\n        print(f\'Gracefully closing environment for {self}\')\n    \n    async def update(self):\n        # Put whatever you want your producer to do, here.\n        # It can read from any source and `forward` data to consumer queues.\n        # This method is run on repeat in-between status checks of the worker.\n\n        # Forward the current timestamp to \'ping\'\n        self.forward(\'ping\', time.time())\n        print(\'Pinged!\')\n        \n        # Sleep a random amount of time to create obvious offset\n        time.sleep(random.random() * 2)\n\n        # Forward a randomly generated number to \'random\'\n        self.forward(\'random\', random.randint(0, 100))\n        print(\'Randomed!\')\n\n        # Sleep again ... same reason.\n        time.sleep(random.random() * 2)\n\n\nclass MyConsumer(Consumer):\n    \n    async def __aenter__(self):\n        print(f\'Preparing environment for {self}\')\n\n    async def __aexit__(self, exc_type, exc_value, trace):\n        print(f\'Gracefully closing environment for {self}\')\n\n\n    # `listen` defines a function to be called with data\n    # that is labeled with the specified event name.\n    \n    @listen(\'ping\')\n    async def on_ping(self, timestamp):\n        """Print the time at which a ping was sent"""        \n        timestamp = datetime.datetime.fromtimestamp(int(timestamp))\n        print(f\'Ping at {timestamp.strftime("%Y-%m-%d %H:%M:%S")}\')\n    \n    @listen(\'random\')\n    async def on_random(self, number):\n        """Print generated random numbers"""\n\n        if number > 80:\n            raise RuntimeError(\'An error to show off the `Warehut` error handler\')\n\n        print(f\'Random number generated: {number}\')\n\n\n\nif __name__ == \'__main__\':\n    \n    with MyWarehut([MyProducer, MyConsumer]):\n        # `Warehut.start` is called upon entering the context\n        input(\'\\nPress Enter to exit\\n\\n\')\n        # `Warehut.stop` is called upon exiting the context\n\n\n    # They can be called on their own with the same effect\n    # \n    # Ex.\n    # warehut = MyWarehut([MyProducer, MyConsumer])\n    # warehut.start()\n    # input(\'\\nPress Enter to exit\\n\\n\')\n    # warehut.stop()\n```',
    'author': 'Maximillian Strand',
    'author_email': 'maximillian.strand@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/deepadmax/warehut',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
