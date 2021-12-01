from pandas import DataFrame


class StoreDataFrame:
    df = DataFrame(
        {
            "id": [1, 2],
            "name": ["John", "Jane"],
            "description": [
                "John loves writing pytests in vscode",
                "Dit is een Nederlandse tekst",
            ],
        }
    )
    path: str = None

    def store_dataframe(self, base_path: str) -> str:
        pass


class CSVStoreDataFrame(StoreDataFrame):
    def store_dataframe(self, base_path: str) -> str:
        path = f"{base_path}/example.csv"
        self.df.to_csv(path, index=False)

        return path


class JSONStoreDataFrame(StoreDataFrame):
    def store_dataframe(self, base_path: str) -> str:
        path = f"{base_path}/example.json"
        self.df.to_json(path, orient="records", lines=True)

        return path


class PickleStoreDataFrame(StoreDataFrame):
    def store_dataframe(self, base_path: str) -> str:
        path = f"{base_path}/example.pkl"
        self.df.to_pickle(path)

        return path
