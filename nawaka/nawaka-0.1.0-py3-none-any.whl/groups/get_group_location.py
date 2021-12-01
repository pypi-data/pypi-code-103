import pandas as pd
import argparse
import requests
from fuzzywuzzy import process
from loguru import logger
from tqdm import tqdm
import simplekml


def get_group_api(url="https://www.scouting.nl/api/groups"):
    r = requests.get(url)
    return pd.json_normalize(r.json()["entries"])


def save_kml(groups):
    # Iterate over speltakken
    for speltak in ["Welpen", "Scouts", "Explorers"]:
        # Select groups for distinct speltakken
        speltak_groups = groups[
            groups["Formuliernaam"] == f"2022 - Groepsinschrijving {speltak}"
        ]

        # Create and save KML for each speltak
        kml = simplekml.Kml()
        for i, group in speltak_groups.iterrows():
            kml.newpoint(
                name=group["title"],
                coords=[(group["adres.lng"], group["adres.lat"])],
            )
        kml.save(f"output/groepen-{speltak}.kml")
        logger.info(f"Saved KML with {speltak} with {len(speltak_groups)} groups.")


def get_groups(excel_file):
    # Read excel file
    df = pd.read_excel(excel_file)
    df["title.city"] = df["Organisatie"] + " " + df["Organisatie plaats"]
    logger.info(f"Loaded file with {len(df)} groups")

    # Retrieve groups from Scouting API
    groups = get_group_api()
    groups["title.city"] = groups["title"] + " " + groups["adres.city"]
    logger.info(f"Retrieved {len(groups)} groups")

    # Finding combinations
    for i, row in tqdm(df.iterrows(), total=len(df)):
        location = process.extractOne(row["title.city"], groups["title.city"])

        # Check if at least one group is found
        if location is None:
            logger.error(
                f"Group {row['Organisatie']} in {row['Organisatie plaats']} not found"
            )
            break

        # Get index of group
        group = groups.iloc[location[2]]

        # Assign groups to original dataframe
        for param in group.index:
            df.at[i, param] = group[param]

    save_kml(df)
    logger.info("Done.")


def cli():
    parser = argparse.ArgumentParser(
        description="Get location of Nawaka participating groups."
    )
    parser.add_argument(
        "--excel",
        type=str,
        help="Excel file containing participating groups.",
        required=True,
    )

    args = parser.parse_args()
    get_groups(args.excel)
