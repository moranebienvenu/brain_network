import pandas as pd

from config import (
    DATA_DIR,
    METHODS,
    IQ_CONTROL,
    IQ_GIFTED,
)


# ============================================================
# IQ mapping
# ============================================================

def build_iq_mapping():
    """
    Build the subject -> IQ mapping used in the original analysis.

    Returns
    -------
    dict
        Dictionary such as:
        {
            "Subject Control_1": 118,
            ...
            "Subject Gifted_1": 149,
            ...
        }
    """

    iq_mapping = {}

    for index, iq in enumerate(IQ_CONTROL, start=1):
        iq_mapping[f"Subject Control_{index}"] = iq

    for index, iq in enumerate(IQ_GIFTED, start=1):
        iq_mapping[f"Subject Gifted_{index}"] = iq

    return iq_mapping


def add_iq_column(df):
    """
    Add IQ values to a global individual-values DataFrame.
    """

    df = df.copy()

    iq_mapping = build_iq_mapping()

    df["IQ"] = df["Subject"].map(iq_mapping)

    missing_subjects = (
        df.loc[df["IQ"].isna(), "Subject"]
        .drop_duplicates()
        .tolist()
    )

    if missing_subjects:
        raise ValueError(
            "No IQ value found for the following subjects: "
            f"{missing_subjects}"
        )

    return df


# ============================================================
# Global data
# ============================================================

def load_global_data():
    """
    Load and concatenate global individual metric CSV files.

    Returns
    -------
    pandas.DataFrame
    """

    dataframes = []

    for method in METHODS:

        file_path = (
            DATA_DIR
            / f"global_individual_values_{method}_500.aparc.csv"
        )

        df = pd.read_csv(file_path)

        dataframes.append(df)

    global_df = pd.concat(
        dataframes,
        ignore_index=True,
    )

    global_df["Density"] = pd.to_numeric(
        global_df["Density"],
        errors="coerce",
    )

    global_df["Value"] = pd.to_numeric(
        global_df["Value"],
        errors="coerce",
    )

    global_df = add_iq_column(global_df)

    return global_df


# ============================================================
# Nodal data
# ============================================================

def load_nodal_data():
    """
    Load and concatenate nodal metric CSV files.

    Returns
    -------
    pandas.DataFrame
    """

    dataframes = []

    for method in METHODS:

        file_path = (
            DATA_DIR
            / (
                "nodal_feature_values_all_densities_"
                f"{method}_500.aparc.csv"
            )
        )

        df = pd.read_csv(file_path)

        dataframes.append(df)

    nodal_df = pd.concat(
        dataframes,
        ignore_index=True,
    )

    numeric_columns = [
        "Density",
        "Control_normalized",
        "Gifted_normalized",
        "Diff_gifted_minus_controls",
    ]

    for column in numeric_columns:

        nodal_df[column] = pd.to_numeric(
            nodal_df[column],
            errors="coerce",
        )

    return nodal_df