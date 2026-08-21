import re


# ============================================================
# AVAILABLE STATIC MNE VISUALIZATIONS
# ============================================================

MNE_STATIC_DENSITY = 0.15
MNE_STATIC_PARCELLATION = "500.aparc"

MNE_STATIC_METRICS = [
    "Clustering Coefficient",
    "Node Versatility",
]


# ============================================================
# IMAGE PATH
# ============================================================

def get_mne_image_path(
    method,
    feature,
    density=0.15,
    parcellation="500.aparc",
):
    """
    Return the path to the static MNE PNG corresponding to
    the selected parameters.

    These images were generated beforehand using the original
    MNE analysis pipeline.

    Parameters
    ----------
    method : str
        maxSW, MIND or MSN

    feature : str
        Clustering Coefficient or Node Versatility

    density : float
        Currently only 0.15 is available.

    parcellation : str
        Currently only 500.aparc is available.

    Returns
    -------
    str
        Dash asset URL.
    """

    safe_feature = re.sub(
        r"[^A-Za-z0-9]+",
        "_",
        feature,
    ).strip("_")

    filename = (
        f"brain_{safe_feature}_"
        f"density_{density:.2f}_"
        f"{method}_"
        f"{parcellation}.png"
    )

    return f"/assets/mne/{filename}"