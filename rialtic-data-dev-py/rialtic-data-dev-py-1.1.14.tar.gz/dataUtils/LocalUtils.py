class LocalUtils:
    @staticmethod
    def api_key_from_file(filename: str):
        with open(filename, 'r') as keyfile:
            return keyfile.read().strip()
