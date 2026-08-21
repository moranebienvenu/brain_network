from pathlib import Path
import json
import re

import numpy as np
import plotly.graph_objects as go


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PREPARED_DIR = (
    BASE_DIR
    / "brain_data"
    / "prepared"
)

MESH_PATH = (
    PREPARED_DIR
    / "brain_mesh_500_aparc.npz"
)

REGION_PATH = (
    PREPARED_DIR
    / "brain_regions_500_aparc.json"
)


# ============================================================
# LOAD PRECOMPUTED BRAIN DATA ONCE
# ============================================================

MESH = np.load(MESH_PATH)

with open(
    REGION_PATH,
    "r",
    encoding="utf-8",
) as file:
    REGION_METADATA = json.load(file)


LH_VERTICES = MESH["lh_vertices"]
LH_FACES = MESH["lh_faces"]
LH_VERTEX_REGION = MESH["lh_vertex_region"]

RH_VERTICES = MESH["rh_vertices"]
RH_FACES = MESH["rh_faces"]
RH_VERTEX_REGION = MESH["rh_vertex_region"]

LH_REGIONS = REGION_METADATA["lh"]
RH_REGIONS = REGION_METADATA["rh"]


# ============================================================
# REGION LOOKUP
# ============================================================

REGION_LOOKUP = {}

for region_idx, region_name in enumerate(LH_REGIONS):
    REGION_LOOKUP[region_name] = (
        "lh",
        region_idx,
    )

for region_idx, region_name in enumerate(RH_REGIONS):
    REGION_LOOKUP[region_name] = (
        "rh",
        region_idx,
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_key(name):
    """
    Normalize region names for CSV <-> annotation matching.
    """

    return re.sub(
        r"[^a-z0-9]",
        "",
        str(name).lower(),
    )


# ============================================================
# BUILD CSV REGION -> VALUE LOOKUP
# ============================================================

def build_region_value_lookup(
    dataframe,
    value_column,
):
    """
    Build:
        normalized region name -> numerical value
    """

    lookup = {}

    for _, row in dataframe.iterrows():

        region = row["Region"]
        value = row[value_column]

        if np.isfinite(value):

            lookup[
                normalize_key(region)
            ] = float(value)

    return lookup


# ============================================================
# MAP REGION VALUES TO VERTICES
# ============================================================

def values_to_vertices(
    region_names,
    vertex_region_index,
    value_lookup,
):
    """
    Convert regional values into one value per surface vertex.

    Also returns the corresponding region name for every vertex.
    """

    vertex_values = np.full(
        len(vertex_region_index),
        np.nan,
        dtype=np.float32,
    )

    vertex_names = np.full(
        len(vertex_region_index),
        "",
        dtype=object,
    )

    for region_idx, region_name in enumerate(region_names):

        value = value_lookup.get(
            normalize_key(region_name),
            np.nan,
        )

        mask = (
            vertex_region_index
            == region_idx
        )

        vertex_values[mask] = value
        vertex_names[mask] = region_name

    return (
        vertex_values,
        vertex_names,
    )


# ============================================================
# CREATE BASE HEMISPHERE
# ============================================================

def create_hemisphere_mesh(
    vertices,
    faces,
    vertex_values,
    vertex_names,
    name,
    cmin=-1.0,
    cmax=1.0,
    showscale=False,
):
    """
    Create the main cortical Mesh3d trace.
    """

    # customdata is important:
    # Dash clickData / hoverData can retrieve the region name.
    customdata = np.asarray(
        vertex_names,
        dtype=object,
    )

    mesh = go.Mesh3d(

        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],

        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],

        intensity=vertex_values,

        intensitymode="vertex",

        colorscale="RdBu_r",

        cmin=cmin,
        cmax=cmax,
        cmid=0,

        showscale=showscale,

        colorbar=dict(
            title="Gifted − Controls",
            thickness=15,
            len=0.7,
        ),

        customdata=customdata,

        hovertemplate=(
            "<b>%{customdata}</b>"
            "<br>"
            "Gifted − Controls: %{intensity:.3f}"
            "<extra></extra>"
        ),

        name=name,

        flatshading=False,

        lighting=dict(
            ambient=0.5,
            diffuse=0.8,
            roughness=0.6,
            specular=0.2,
        ),

        lightposition=dict(
            x=100,
            y=100,
            z=200,
        ),
    )

    return mesh


# ============================================================
# MAIN BRAIN FIGURE
# ============================================================

def make_brain_3d_figure(
    dataframe,
    value_column="Diff_gifted_minus_controls",
    title=None,
    cmin=-1.0,
    cmax=1.0,
):
    """
    Build interactive 3D cortical visualization.

    Trace organization is intentionally fixed:

        trace 0 = left hemisphere
        trace 1 = right hemisphere
        trace 2 = hover highlight #deleted for now -- took to much time to update
        trace 3 = hover contour #deleted for now -- took to much time to update 

    Dash callbacks rely on these trace indexes.
    """

    value_lookup = build_region_value_lookup(
        dataframe=dataframe,
        value_column=value_column,
    )

    # --------------------------------------------------------
    # Left hemisphere
    # --------------------------------------------------------

    (
        lh_values,
        lh_names,
    ) = values_to_vertices(
        region_names=LH_REGIONS,
        vertex_region_index=LH_VERTEX_REGION,
        value_lookup=value_lookup,
    )

    # --------------------------------------------------------
    # Right hemisphere
    # --------------------------------------------------------

    (
        rh_values,
        rh_names,
    ) = values_to_vertices(
        region_names=RH_REGIONS,
        vertex_region_index=RH_VERTEX_REGION,
        value_lookup=value_lookup,
    )

    # --------------------------------------------------------
    # Figure
    # --------------------------------------------------------

    figure = go.Figure()

    # Trace 0
    figure.add_trace(

        create_hemisphere_mesh(
            vertices=LH_VERTICES,
            faces=LH_FACES,
            vertex_values=lh_values,
            vertex_names=lh_names,
            name="Left hemisphere",
            cmin=cmin,
            cmax=cmax,
            showscale=True,
        )
    )

    # Trace 1
    figure.add_trace(

        create_hemisphere_mesh(
            vertices=RH_VERTICES,
            faces=RH_FACES,
            vertex_values=rh_values,
            vertex_names=rh_names,
            name="Right hemisphere",
            cmin=cmin,
            cmax=cmax,
            showscale=False,
        )
    )

    
    # --------------------------------------------------------
    # Layout
    # --------------------------------------------------------

    figure.update_layout(

        title=title,

        template="plotly_white",

        height=750,

        margin=dict(
            l=0,
            r=0,
            t=60,
            b=0,
        ),

        scene=dict(

            xaxis=dict(
                visible=False,
            ),

            yaxis=dict(
                visible=False,
            ),

            zaxis=dict(
                visible=False,
            ),

            aspectmode="data",

            bgcolor="white",

            camera=dict(
                eye=dict(
                    x=1.5,
                    y=0,
                    z=0.3,
                )
            ),
        ),

        showlegend=False,

        # Preserve camera when data changes
        uirevision="brain-camera",
    )

    return figure
