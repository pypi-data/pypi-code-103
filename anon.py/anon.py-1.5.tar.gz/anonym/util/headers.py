class Headers:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "X_APPLICATION_VERSION": "2",
            "User-Agent": "okhttp/3.12.0",
            "Accept-Encoding": "gzip"
        }
        self.chatHeaders = {
            "User-Agent": "",
            "Content-Type": "application/json; charset=utf-8"
        }