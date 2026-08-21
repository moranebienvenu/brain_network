import numpy as np
import pandas as pd

from scipy.stats import spearmanr, mannwhitneyu



# ============================================================
# Filtering
# ============================================================

def get_global_values(
    dataframe,
    method,
    metric=None,
    density=None,
    group=None,
    parcellation="500.aparc",
):
    """
    Filter global individual metric values.

    Parameters
    ----------
    dataframe : pandas.DataFrame
    method : str
    metric : str or None
    density : float or None
    group : str or None
        "Control" or "Gifted"
    parcellation : str

    Returns
    -------
    pandas.DataFrame
    """

    mask = (
        (dataframe["Method"] == method)
        & (dataframe["Parcellation"] == parcellation)
    )

    if metric is not None:
        mask &= dataframe["Metric"] == metric

    if density is not None:
        mask &= np.isclose(
            dataframe["Density"],
            density,
        )

    if group is not None:
        mask &= dataframe["Group"] == group

    return dataframe.loc[mask].copy()


# ============================================================
# Spearman
# ============================================================

def compute_spearman_by_density(
    dataframe,
    method,
    metrics,
    parcellation="500.aparc",
):
    """
    Compute Spearman correlations between IQ and network metrics
    at each connection density.

    Controls and Gifted subjects are combined, reproducing the
    behavior of the original analysis.

    Returns
    -------
    pandas.DataFrame
    """

    df_method = get_global_values(
        dataframe=dataframe,
        method=method,
        parcellation=parcellation,
    )

    results = []

    densities = sorted(
        df_method["Density"]
        .dropna()
        .unique()
    )

    for metric in metrics:

        df_metric = df_method[
            df_method["Metric"] == metric
        ]

        for density in densities:

            selected = df_metric[
                np.isclose(
                    df_metric["Density"],
                    density,
                )
            ].copy()

            selected = selected.dropna(
                subset=["IQ", "Value"]
            )

            if len(selected) < 2:
                rho = np.nan
                p_value = np.nan

            else:
                rho, p_value = spearmanr(
                    selected["IQ"],
                    selected["Value"],
                )

            results.append(
                {
                    "Method": method,
                    "Parcellation": parcellation,
                    "Density": float(density),
                    "Metric": metric,
                    "N": len(selected),
                    "Spearman_rho": rho,
                    "Spearman_p_value": p_value,
                }
            )

    return pd.DataFrame(results)


# ============================================================
# IQ vs one metric
# ============================================================

def get_iq_metric_data(
    dataframe,
    method,
    metric,
    density,
    parcellation="500.aparc",
):
    """
    Return subject-level IQ and metric values at one density.
    """

    selected = get_global_values(
        dataframe=dataframe,
        method=method,
        metric=metric,
        density=density,
        parcellation=parcellation,
    )

    return selected[
        [
            "Subject",
            "Group",
            "IQ",
            "Value",
            "Age",
            "eTIV",
        ]
    ].copy()

def compute_iq_metric_statistics(
    dataframe,
):
    """
    Compute statistics for the IQ vs metric scatter plot.

    This reproduces the logic used in Gabrielle's
    plot_iq_metric_scatter_grid():

    - Spearman correlation between IQ and the metric
      using all subjects combined.
    - Mann-Whitney U test comparing metric values
      between Control and Gifted groups.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        Data already filtered for one method, metric
        and density.

        Expected columns:
            IQ
            Value
            Group

    Returns
    -------
    dict
        rho
        spearman_p
        mannwhitney_p
        n
    """

    df = dataframe.copy()

    # --------------------------------------------------------
    # Keep valid IQ / metric observations
    # --------------------------------------------------------

    valid = (
        df["IQ"].notna()
        & df["Value"].notna()
    )

    valid_df = df.loc[valid].copy()

    iq_values = valid_df[
        "IQ"
    ].astype(float).to_numpy()

    metric_values = valid_df[
        "Value"
    ].astype(float).to_numpy()

    # --------------------------------------------------------
    # Spearman correlation
    # All subjects combined
    # --------------------------------------------------------

    if (
        len(iq_values) >= 3
        and len(set(iq_values)) > 1
        and len(set(metric_values)) > 1
    ):

        rho, spearman_p = spearmanr(
            iq_values,
            metric_values,
        )

    else:

        rho = float("nan")
        spearman_p = float("nan")

    # --------------------------------------------------------
    # Mann-Whitney
    # Gifted vs Control metric values
    # --------------------------------------------------------

    control_values = (
        valid_df.loc[
            valid_df["Group"] == "Control",
            "Value",
        ]
        .dropna()
        .astype(float)
        .to_numpy()
    )

    gifted_values = (
        valid_df.loc[
            valid_df["Group"] == "Gifted",
            "Value",
        ]
        .dropna()
        .astype(float)
        .to_numpy()
    )

    if (
        len(control_values) > 0
        and len(gifted_values) > 0
    ):

        _, mannwhitney_p = mannwhitneyu(
            gifted_values,
            control_values,
            alternative="two-sided",
        )

    else:

        mannwhitney_p = float("nan")

    return {
        "rho": float(rho),
        "spearman_p": float(spearman_p),
        "mannwhitney_p": float(mannwhitney_p),
        "n": len(valid_df),
    }
# ============================================================
# Density profile
# ============================================================

def get_group_metric_profile(
    dataframe,
    method,
    metric,
    parcellation="500.aparc",
):
    """
    Compute mean metric value at each density for each group.
    """

    selected = get_global_values(
        dataframe=dataframe,
        method=method,
        metric=metric,
        parcellation=parcellation,
    )

    summary = (
        selected
        .groupby(
            ["Group", "Density"],
            as_index=False,
        )
        .agg(
            Mean=("Value", "mean"),
            SD=("Value", "std"),
            N=("Value", "count"),
        )
    )

    summary["SEM"] = (
        summary["SD"]
        / np.sqrt(summary["N"])
    )

    return summary