import os

import pandas as pd
from zipline.data.bundles import ingest

if __name__ == "__main__":
    ingest("yahoo_demo_bundle", os.environ, pd.Timestamp.utcnow(), [], True)
