
API_BASE_ADDR = 'https://api.odriverobotics.com'

class APIBase():
    def __init__(self, session, api_base_addr: str = API_BASE_ADDR):
        self._session = session
        self._api_base_addr = api_base_addr

    async def call(self, method: str, endpoint: str, inputs=None):
        async with self._session.request(method, self._api_base_addr + endpoint, json=inputs or {}) as response:
            if response.status != 200:
                try:
                    ex_data = await response.json()
                except:
                    ex_raw = await response.read()
                    raise Exception(f"Server failed with {response.status} ({response.reason}): {ex_raw}")
                else:
                    tb = ''.join(ex_data['traceback'])
                    raise Exception(f"Server failed with {response.status} ({response.reason}): {ex_data['message']} in \n{tb}")

            return await response.json()

    async def download(self, url: str):
        async with self._session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Server failed with {response.status} ({response.reason})")
            return await response.read()
