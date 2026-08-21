import numpy as np
import pandas as pd


def get_nodal_values(
    dataframe,
    method,
    feature,
    density,
    parcellation="500.aparc",
):
    """
    Select nodal values for one method, density and feature.
    """

    mask = (
        (dataframe["Method"] == method)
        & (dataframe["Parcellation"] == parcellation)
        & (dataframe["Feature"] == feature)
        & np.isclose(
            dataframe["Density"],
            density,
        )
    )

    selected = dataframe.loc[mask].copy()

    return selected


def get_top_regions(
    dataframe,
    method,
    feature,
    density,
    n_regions=15,
    parcellation="500.aparc",
):
    """
    Return regions showing the largest absolute differences
    between Gifted and Controls.
    """

    selected = get_nodal_values(
        dataframe=dataframe,
        method=method,
        feature=feature,
        density=density,
        parcellation=parcellation,
    )

    selected["Absolute_difference"] = (
        selected[
            "Diff_gifted_minus_controls"
        ].abs()
    )

    selected = selected.sort_values(
        "Absolute_difference",
        ascending=False,
    )

    return selected.head(n_regions)


def get_region_density_profile(
    dataframe,
    method,
    feature,
    region,
    parcellation="500.aparc",
):
    """
    Return Gifted-Control differences across densities
    for one selected cortical region.
    """

    mask = (
        (dataframe["Method"] == method)
        & (dataframe["Parcellation"] == parcellation)
        & (dataframe["Feature"] == feature)
        & (dataframe["Region"] == region)
    )

    selected = (
        dataframe.loc[mask]
        .copy()
        .sort_values("Density")
    )

    return selected

# ============================================================
# GLOBAL SED
# ============================================================

def compute_global_sed(
    control_values,
    gifted_values,
):
    """
    Compute the signed Euclidean distance (Global SED)
    between the normalized Control and Gifted nodal vectors.

    This reproduces the original analysis:

        sign(mean_gifted - mean_control)
        *
        || gifted - control ||_2
    """

    control = np.asarray(
        control_values,
        dtype=float,
    )

    gifted = np.asarray(
        gifted_values,
        dtype=float,
    )

    if control.shape != gifted.shape:
        raise ValueError(
            "Control and Gifted vectors must have "
            "the same shape."
        )

    valid = (
        np.isfinite(control)
        & np.isfinite(gifted)
    )

    control = control[valid]
    gifted = gifted[valid]

    if len(control) == 0:
        return np.nan

    mean_control = np.mean(control)
    mean_gifted = np.mean(gifted)

    euclidean_distance = np.linalg.norm(
        gifted - control
    )

    sed = (
        np.sign(
            mean_gifted
            - mean_control
        )
        * euclidean_distance
    )

    return float(sed)


def compute_global_sed_by_density(
    dataframe,
    method,
    parcellation="500.aparc",
):
    """
    Compute Global SED for every nodal feature and density
    for one network construction method.

    Returns
    -------
    pandas.DataFrame

    Columns:
        Method
        Parcellation
        Density
        Feature
        Global_SED
    """

    selected = dataframe[
        (dataframe["Method"] == method)
        & (
            dataframe["Parcellation"]
            == parcellation
        )
    ].copy()

    results = []

    for (
        density,
        feature
    ), group in selected.groupby(
        [
            "Density",
            "Feature",
        ]
    ):

        sed = compute_global_sed(
            control_values=group[
                "Control_normalized"
            ],
            gifted_values=group[
                "Gifted_normalized"
            ],
        )

        results.append(
            {
                "Method": method,
                "Parcellation": parcellation,
                "Density": float(density),
                "Feature": feature,
                "Global_SED": sed,
            }
        )

    result_df = pd.DataFrame(
        results
    )

    result_df = result_df.sort_values(
        [
            "Feature",
            "Density",
        ]
    )

    return result_df