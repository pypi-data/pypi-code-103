from browser import window
import javascript


class Bridge:

    def __getattr__(self, attr):
        return lambda *args, **kwargs: self.call(attr, *args, **kwargs)

    def on_load(self, xhr, ev, callback, errback):
        if xhr.status == 200:
            ret = javascript.JSON.parse(xhr.response)
            if callback is not None:
                if ret is None:
                    callback()
                else:
                    callback(ret)
        elif xhr.status == 502:
            # PROXY_ERROR is used for bridge error
            ret = javascript.JSON.parse(xhr.response)
            if errback is not None:
                errback(ret)
        else:
            print(f"bridge called failed: code: {xhr.response}, text: {xhr.statusText}")
            if errback is not None:
                errback({"fullname": "BridgeInternalError", "message": xhr.statusText})

    def call(self, method_name, *args, callback, errback, **kwargs):
        xhr = window.XMLHttpRequest.new()
        xhr.bind('load', lambda ev: self.on_load(xhr, ev, callback, errback))
        xhr.bind('error', lambda ev: errback(
            {"fullname": "ConnectionError", "message": xhr.statusText}))
        xhr.open("POST", f"/_bridge/{method_name}", True)
        data = javascript.JSON.stringify({
            "args": args,
            "kwargs": kwargs,
        })
        xhr.setRequestHeader('X-Csrf-Token', window.csrf_token)
        xhr.send(data)
