from browser import window, aio
import javascript


class BridgeException(Exception):
    """An exception which has been raised from the backend and arrived to the frontend."""

    def __init__(self, name, message="", condition=""):
        """

        @param name (str): full exception class name (with module)
        @param message (str): error message
        @param condition (str) : error condition
        """
        Exception.__init__(self)
        self.fullname = str(name)
        self.message = str(message)
        self.condition = str(condition) if condition else ""
        self.module, __, self.classname = str(self.fullname).rpartition(".")

    def __str__(self):
        return f"{self.classname}: {self.message or ''}"

    def __eq__(self, other):
        return self.classname == other


class Bridge:

    def __getattr__(self, attr):
        return lambda *args, **kwargs: self.call(attr, *args, **kwargs)

    async def call(self, method_name, *args, **kwargs):
        data = javascript.JSON.stringify({
            "args": args,
            "kwargs": kwargs,
        })
        url = f"/_bridge/{method_name}"
        r = await aio.post(
            url,
            headers={
                'X-Csrf-Token': window.csrf_token,
            },
            data=data,
        )

        if r.status == 200:
            return javascript.JSON.parse(r.data)
        elif r.status == 502:
            ret = javascript.JSON.parse(r.data)
            raise BridgeException(ret['fullname'], ret['message'], ret['condition'])
        else:
            print(f"bridge called failed: code: {r.status}, text: {r.statusText}")
            raise BridgeException("InternalError", r.statusText)
