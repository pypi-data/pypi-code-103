import pandas as pd


def merge_with_propositions_containers(
    propositions_df: pd.DataFrame, propositions_containers_df: pd.DataFrame,) -> pd.DataFrame:
    propositions_df = pd.merge(
        propositions_df,
        propositions_containers_df[["teus", "tc", "hazardous", "refrigerated", "proposition_id"]],
        how="left",
        on="proposition_id",
    ).reset_index(drop=True).rename(columns={"hazardous": "containers_hazardous",
                                             "refrigerated": "containers_refrigerated"})
    return propositions_df


def merge_propositions_with_containers(
    propositions_df: pd.DataFrame, propositions_containers_df: pd.DataFrame, drop_duplicate_key="proposition_id",
):
    propositions_df = merge_with_propositions_containers(
        propositions_df=propositions_df,
        propositions_containers_df=propositions_containers_df
    )
    propositions_df = propositions_df.sort_values(by=["teus", "tc"], ascending=False)
    propositions_df = propositions_df[
        (~propositions_df.duplicated(subset=[drop_duplicate_key])) | (propositions_df[drop_duplicate_key].isnull())
    ]  # drop duplicates without dropping nan
    return propositions_df
