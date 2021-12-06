import pandas as pd


def merge_with_propositions_loads_then_with_shipments_loads(
    shipments_df: pd.DataFrame, propositions_loads_df: pd.DataFrame, shipments_loads_df: pd.DataFrame,
) -> pd.DataFrame:
    shipments_df = pd.merge(
        shipments_df,
        propositions_loads_df[
            [
                "total_number",
                "total_volume_in_cbm",
                "total_weight_in_kg",
                "taxable_weight_in_kg",
                "weight_measurable",
                "hazardous",
                "lithium",
                "non_stackable",
                "proposition_id",
            ]
        ],
        how="left",
        on="proposition_id",
    )

    shipments_df_with_total_weight = shipments_df[~shipments_df["total_weight_in_kg"].isnull()]
    shipments_df_without_total_weight = shipments_df[shipments_df["total_weight_in_kg"].isnull()].drop(
        [
            "total_number",
            "total_weight_in_kg",
            "total_volume_in_cbm",
            "taxable_weight_in_kg",
            "weight_measurable",
            "hazardous",
            "lithium",
            "non_stackable",
        ],
        axis=1,
    )

    shipments_df_without_total_weight = pd.merge(
        shipments_df_without_total_weight,
        shipments_loads_df[
            [
                "total_number",
                "total_volume_in_cbm",
                "total_weight_in_kg",
                "taxable_weight_in_kg",
                "weight_measurable",
                "hazardous",
                "magnetic",
                "lithium",
                "refrigerated",
                "non_stackable",
                "shipment_id",
            ]
        ],
        how="left",
        on="shipment_id",
    )

    return (
        pd.concat([shipments_df_with_total_weight, shipments_df_without_total_weight], sort=False,)
        .reset_index(drop=True)
        .rename(
            columns={
                "hazardous": "loads_hazardous",
                "magnetic": "loads_magnetic",
                "lithium": "loads_lithium",
                "refrigerated": "loads_refrigerated",
            }
        )
    )


def split_propositions_shipments_loads(loads_df: pd.DataFrame):
    propositions_loads_df = loads_df[~loads_df["proposition_id"].isnull()]
    shipments_loads_df = loads_df[~loads_df["shipment_id"].isnull()]
    return propositions_loads_df, shipments_loads_df


def merge_shipments_with_loads(shipments_df: pd.DataFrame, loads_df: pd.DataFrame, drop_duplicate_key="shipment_id"):
    (propositions_loads_df, shipments_loads_df,) = split_propositions_shipments_loads(loads_df)
    shipments_df = merge_with_propositions_loads_then_with_shipments_loads(
        shipments_df=shipments_df, propositions_loads_df=propositions_loads_df, shipments_loads_df=shipments_loads_df,
    )
    shipments_df = shipments_df.sort_values(by=["total_weight_in_kg", "total_volume_in_cbm"], ascending=False)
    shipments_df = shipments_df[
        (~shipments_df.duplicated(subset=[drop_duplicate_key])) | (shipments_df[drop_duplicate_key].isnull())
    ]  # drop duplicates without dropping nan
    return shipments_df
