from pathlib import Path
import json
import re

import numpy as np
import plotly.graph_objects as go


# ============================================================
# PATHS
# ============================================================

def load_brain_data(parcellation):
    brain_data_dico={}

    BASE_DIR = Path(__file__).resolve().parent.parent

    PREPARED_DIR = (
        BASE_DIR
        / "brain_data"
        / "prepared"
    )

    safe_parcellation = parcellation.replace(".", "_")

    MESH_PATH = (
        PREPARED_DIR
        / f"brain_mesh_{safe_parcellation}.npz"
    )

    REGION_PATH = (
        PREPARED_DIR
        / f"brain_regions_{safe_parcellation}.json"
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


    brain_data_dico= {
    "lh_vertices": LH_VERTICES,
    "lh_faces": LH_FACES,
    "lh_vertex_region": LH_VERTEX_REGION,
    "rh_vertices": RH_VERTICES,
    "rh_faces": RH_FACES,
    "rh_vertex_region": RH_VERTEX_REGION,
    "lh_regions": LH_REGIONS,
    "rh_regions": RH_REGIONS,
    }

    return brain_data_dico


# ============================================================
# REGION LOOKUP
# ============================================================

def build_region_lookup(brain_data_dico):


    REGION_LOOKUP = {}

    for region_idx, region_name in enumerate(brain_data_dico["lh_regions"]):
        REGION_LOOKUP[region_name] = (
            "lh",
            region_idx,
        )

    for region_idx, region_name in enumerate(brain_data_dico["rh_regions"]):
        REGION_LOOKUP[region_name] = (
            "rh",
            region_idx,
        )
    
    return REGION_LOOKUP


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
    parcellation,
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
    
    brain_data_dico=load_brain_data(parcellation)
    
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
        region_names=brain_data_dico["lh_regions"],
        vertex_region_index=brain_data_dico["lh_vertex_region"],
        value_lookup=value_lookup,
    )

    # --------------------------------------------------------
    # Right hemisphere
    # --------------------------------------------------------

    (
        rh_values,
        rh_names,
    ) = values_to_vertices(
        region_names=brain_data_dico["rh_regions"],
        vertex_region_index=brain_data_dico["rh_vertex_region"],
        value_lookup=value_lookup,
    )

    # --------------------------------------------------------
    # Figure
    # --------------------------------------------------------

    figure = go.Figure()

    # Trace 0
    figure.add_trace(

        create_hemisphere_mesh(
            vertices=brain_data_dico["lh_vertices"],
            faces=brain_data_dico["lh_faces"],
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
            vertices=brain_data_dico["rh_vertices"],
            faces=brain_data_dico["rh_faces"],
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

# ============================================================
# HIGH-VERSATILITY NODES BRAIN FIGURE
# ============================================================

def make_high_nodes_brain_figure(
    dataframe,
    parcellation,
    group,
    title=None,
):
    """
    Create a 3D cortical map highlighting
    high-versatility nodes for one group.
    """

    brain_data_dico = load_brain_data(
        parcellation
    )

    # --------------------------------------------------------
    # Build region -> high-node lookup
    # --------------------------------------------------------

    high_node_lookup = {}

    metric_lookup = {}

    threshold_lookup = {}

    for _, row in dataframe.iterrows():

        region_key = normalize_key(
            row["Region"]
        )

        high_node_lookup[
            region_key
        ] = 1.0

        metric_lookup[
            region_key
        ] = float(
            row["Metric_Value"]
        )

        threshold_lookup[
            region_key
        ] = float(
            row["High_Threshold"]
        )

    # --------------------------------------------------------
    # Function to prepare one hemisphere
    # --------------------------------------------------------

    def prepare_hemisphere(
        region_names,
        vertex_region_index,
    ):

        vertex_values = np.zeros(
            len(vertex_region_index),
            dtype=np.float32,
        )

        vertex_names = np.full(
            len(vertex_region_index),
            "",
            dtype=object,
        )

        vertex_metric_values = np.full(
            len(vertex_region_index),
            np.nan,
            dtype=np.float32,
        )

        vertex_thresholds = np.full(
            len(vertex_region_index),
            np.nan,
            dtype=np.float32,
        )

        for region_idx, region_name in enumerate(
            region_names
        ):

            region_key = normalize_key(
                region_name
            )

            is_high = high_node_lookup.get(
                region_key,
                0.0,
            )

            mask = (
                vertex_region_index
                == region_idx
            )

            vertex_values[
                mask
            ] = is_high

            vertex_names[
                mask
            ] = region_name

            if is_high == 1.0:

                vertex_metric_values[
                    mask
                ] = metric_lookup[
                    region_key
                ]

                vertex_thresholds[
                    mask
                ] = threshold_lookup[
                    region_key
                ]

        return (
            vertex_values,
            vertex_names,
            vertex_metric_values,
            vertex_thresholds,
        )

    # --------------------------------------------------------
    # Left hemisphere
    # --------------------------------------------------------

    (
        lh_values,
        lh_names,
        lh_metric_values,
        lh_thresholds,
    ) = prepare_hemisphere(
        region_names=brain_data_dico[
            "lh_regions"
        ],
        vertex_region_index=brain_data_dico[
            "lh_vertex_region"
        ],
    )

    # --------------------------------------------------------
    # Right hemisphere
    # --------------------------------------------------------

    (
        rh_values,
        rh_names,
        rh_metric_values,
        rh_thresholds,
    ) = prepare_hemisphere(
        region_names=brain_data_dico[
            "rh_regions"
        ],
        vertex_region_index=brain_data_dico[
            "rh_vertex_region"
        ],
    )

    # --------------------------------------------------------
    # Figure
    # --------------------------------------------------------

    figure = go.Figure()

    hemispheres = [
        (
            "Left hemisphere",
            brain_data_dico["lh_vertices"],
            brain_data_dico["lh_faces"],
            lh_values,
            lh_names,
            lh_metric_values,
            lh_thresholds,
        ),
        (
            "Right hemisphere",
            brain_data_dico["rh_vertices"],
            brain_data_dico["rh_faces"],
            rh_values,
            rh_names,
            rh_metric_values,
            rh_thresholds,
        ),
    ]

    for (
        hemisphere_name,
        vertices,
        faces,
        vertex_values,
        vertex_names,
        metric_values,
        thresholds,
    ) in hemispheres:

        customdata = np.column_stack(
            [
                vertex_names,
                metric_values,
                thresholds,
            ]
        )

        figure.add_trace(

            go.Mesh3d(

                x=vertices[:, 0],
                y=vertices[:, 1],
                z=vertices[:, 2],

                i=faces[:, 0],
                j=faces[:, 1],
                k=faces[:, 2],

                intensity=vertex_values,

                intensitymode="vertex",

                colorscale=[
                    [0.0, "lightgray"],
                    [0.49, "lightgray"],
                    [0.50, "crimson"],
                    [1.0, "crimson"],
                ],

                cmin=0,
                cmax=1,

                showscale=False,

                customdata=customdata,

                hovertemplate=(
                    "<b>%{customdata[0]}</b>"
                    "<br>"
                    "Node versatility: %{customdata[1]:.3f}"
                    "<br>"
                    "High-node threshold: %{customdata[2]:.3f}"
                    "<extra></extra>"
                ),

                name=hemisphere_name,

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
        )

    # --------------------------------------------------------
    # Layout
    # --------------------------------------------------------

    if title is None:

        title = (
            f"{group} high-versatility nodes"
            "<br>"
            f"{parcellation} parcellation"
        )

    figure.update_layout(

        title=title,

        template="plotly_white",

        height=700,

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

        uirevision=f"high-nodes-{group}",
    )

    return figure