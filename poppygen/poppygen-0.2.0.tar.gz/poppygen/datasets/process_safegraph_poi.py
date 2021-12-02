from pathlib import Path
import pandas as pd

poi_df = pd.DataFrame()

def process_safegraph_poi():
    here = Path(__file__).parent.resolve()
    poi = Path(here / "data/patterns-part1.csv")

    if poi.exists():
        global poi_df
        poi_df = pd.read_csv(poi)

        return poi_df
    else:
        print("POI Dataset Not Available")
        return None

