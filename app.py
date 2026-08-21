from dash import (
    Dash,
    dcc,
    html,
    Input,
    Output,
    State,
    callback,
    no_update,
)

from config import (
    METHODS,
    GLOBAL_METRICS,
    NODAL_METRICS,
)

from services.data_loader import (
    load_global_data,
    load_nodal_data,
)

from services.global_metrics import (
    compute_spearman_by_density,
    get_iq_metric_data,
    get_group_metric_profile,
    compute_iq_metric_statistics,
)

from services.nodal_metrics import (
    get_nodal_values,
    get_top_regions,
    get_region_density_profile,
    compute_global_sed_by_density,
)

from services.mne_images import (
    get_mne_image_path,
    MNE_STATIC_METRICS,
)

from figures.global_figures import (
    make_spearman_figure,
    make_iq_scatter_figure,
    make_group_density_figure,
    make_global_sed_figure,
)

from figures.nodal_figures import (
    make_top_regions_figure,
    make_region_density_figure,
)

from figures.brain_3d import (
    make_brain_3d_figure,
    normalize_key,
)


# ============================================================
# 1. LOAD DATA
# ============================================================

GLOBAL_DATA = load_global_data()
NODAL_DATA = load_nodal_data()


# ============================================================
# 2. AVAILABLE DENSITIES
# ============================================================

GLOBAL_DENSITIES = sorted(
    GLOBAL_DATA["Density"]
    .dropna()
    .unique()
)

NODAL_DENSITIES = sorted(
    NODAL_DATA["Density"]
    .dropna()
    .unique()
)


# ============================================================
# 3. DASH APPLICATION
# ============================================================

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
)

app.title = "Gifted Brain Network Explorer"

server = app.server


# ============================================================
# 4. APPLICATION LAYOUT
# ============================================================

app.layout = html.Div(

    className="app-container",

    children=[

        # ====================================================
        # HEADER
        # ====================================================

        html.H1(
            "Gifted vs Controls",
            className="main-title",
        ),

        html.P(
            "Interactive brain network analysis",
            className="subtitle",
        ),

        # ====================================================
        # MAIN TABS
        # ====================================================

        dcc.Tabs(

            value="global-tab",

            children=[

                # ==================================================
                # GLOBAL METRICS TAB
                # ==================================================

                dcc.Tab(

                    label="Global metrics",
                    value="global-tab",

                    children=[

                        # ------------------------------------------
                        # Global controls
                        # ------------------------------------------

                        html.Div(

                            className="controls",

                            children=[

                                # Analysis
                                html.Div(
                                    [
                                        html.Label("Analysis"),

                                        dcc.Dropdown(
                                            id="global-analysis",

                                            options=[
                                                {
                                                    "label": "Spearman",
                                                    "value": "spearman",
                                                },
                                                {
                                                    "label": "Global SED",
                                                    "value": "sed",
                                                },
                                            ],

                                            value="spearman",
                                            clearable=False,
                                        ),
                                    ]
                                ),

                                # Method
                                html.Div(
                                    [
                                        html.Label("Method"),

                                        dcc.Dropdown(
                                            id="global-method",

                                            options=[
                                                {
                                                    "label": method,
                                                    "value": method,
                                                }
                                                for method in METHODS
                                            ],

                                            value="MSN",
                                            clearable=False,
                                        ),
                                    ]
                                ),

                                # Metric
                                html.Div(
                                    [
                                        html.Label("Metric"),

                                        dcc.Dropdown(
                                            id="global-metric",

                                            options=[
                                                {
                                                    "label": metric,
                                                    "value": metric,
                                                }
                                                for metric in GLOBAL_METRICS
                                            ],

                                            value="Global Efficiency",
                                            clearable=False,
                                        ),
                                    ]
                                ),

                                # Density
                                html.Div(
                                    [
                                        html.Label("Density"),

                                        dcc.Dropdown(
                                            id="global-density",

                                            options=[
                                                {
                                                    "label": f"{density:.2f}",
                                                    "value": density,
                                                }
                                                for density in GLOBAL_DENSITIES
                                            ],

                                            value=0.10,
                                            clearable=False,
                                        ),
                                    ]
                                ),
                            ],
                        ),

                        # ------------------------------------------
                        # Main global graph
                        # Spearman or Global SED
                        # ------------------------------------------

                        html.Div(

                            className="graph-card",

                            children=[

                                dcc.Graph(
                                    id="global-main-graph",
                                ),
                            ],
                        ),

                        # ------------------------------------------
                        # Other global figures
                        # ------------------------------------------

                        html.Div(

                            className="two-columns",

                            children=[

                                html.Div(

                                    className="graph-card",

                                    children=[

                                        dcc.Graph(
                                            id="iq-scatter",
                                        ),
                                    ],
                                ),

                                html.Div(

                                    className="graph-card",

                                    children=[

                                        dcc.Graph(
                                            id="global-density-profile",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),

                # ==================================================
                # NODAL METRICS TAB
                # ==================================================

                dcc.Tab(

                    label="Nodal metrics",
                    value="nodal-tab",

                    children=[

                        # ==================================================
                        # STATIC MNE CORTICAL MAP
                        # ==================================================

                        html.Div(

                            className="graph-card",

                            children=[

                                html.H3(
                                    "Cortical map — MNE",
                                ),

                                html.P(
                                    (
                                        "Static cortical visualization "
                                        "generated from the original "
                                        "MNE analysis."
                                    ),
                                    className="figure-description",
                                ),

                                # ------------------------------
                                # Static MNE controls
                                # ------------------------------

                                html.Div(

                                    className="controls",

                                    children=[

                                        html.Div(
                                            [
                                                html.Label("Method"),

                                                dcc.Dropdown(
                                                    id="mne-method",

                                                    options=[
                                                        {
                                                            "label": method,
                                                            "value": method,
                                                        }
                                                        for method in METHODS
                                                    ],

                                                    value="MSN",
                                                    clearable=False,
                                                ),
                                            ]
                                        ),

                                        html.Div(
                                            [
                                                html.Label("Metric"),

                                                dcc.Dropdown(
                                                    id="mne-feature",

                                                    options=[
                                                        {
                                                            "label": metric,
                                                            "value": metric,
                                                        }
                                                        for metric
                                                        in MNE_STATIC_METRICS
                                                    ],

                                                    value=(
                                                        "Clustering "
                                                        "Coefficient"
                                                    ),

                                                    clearable=False,
                                                ),
                                            ]
                                        ),

                                        html.Div(
                                            [
                                                html.Label("Density"),

                                                html.Div(
                                                    "0.15",
                                                    className="fixed-value",
                                                ),
                                            ]
                                        ),

                                        html.Div(
                                            [
                                                html.Label("Parcellation"),

                                                html.Div(
                                                    "500.aparc",
                                                    className="fixed-value",
                                                ),
                                            ]
                                        ),
                                    ],
                                ),

                                # ------------------------------
                                # Static MNE PNG
                                # ------------------------------

                                html.Img(
                                    id="mne-brain-image",

                                    style={
                                        "width": "100%",
                                        "maxWidth": "1200px",
                                        "height": "auto",
                                        "display": "block",
                                        "margin": "0 auto",
                                    },
                                ),
                            ],
                        ),

                        # ==================================================
                        # INTERACTIVE NODAL CONTROLS
                        # ==================================================

                        html.Div(

                            className="controls",

                            children=[

                                html.Div(
                                    [
                                        html.Label("Method"),

                                        dcc.Dropdown(
                                            id="nodal-method",

                                            options=[
                                                {
                                                    "label": method,
                                                    "value": method,
                                                }
                                                for method in METHODS
                                            ],

                                            value="MSN",
                                            clearable=False,
                                        ),
                                    ]
                                ),

                                html.Div(
                                    [
                                        html.Label("Metric"),

                                        dcc.Dropdown(
                                            id="nodal-feature",

                                            options=[
                                                {
                                                    "label": metric,
                                                    "value": metric,
                                                }
                                                for metric in NODAL_METRICS
                                            ],

                                            value="Clustering Coefficient",
                                            clearable=False,
                                        ),
                                    ]
                                ),

                                html.Div(
                                    [
                                        html.Label("Density"),

                                        dcc.Dropdown(
                                            id="nodal-density",

                                            options=[
                                                {
                                                    "label": f"{density:.2f}",
                                                    "value": density,
                                                }
                                                for density in NODAL_DENSITIES
                                            ],

                                            value=0.15,
                                            clearable=False,
                                        ),
                                    ]
                                ),

                                html.Div(
                                    [
                                        html.Label("Region"),

                                        dcc.Dropdown(
                                            id="region-dropdown",
                                            clearable=False,
                                        ),
                                    ]
                                ),
                            ],
                        ),

                        # ==================================================
                        # INTERACTIVE 3D BRAIN
                        # ==================================================

                        html.Div(

                            className="graph-card",

                            children=[

                                html.H3(
                                    "Interactive 3D cortical map"
                                ),

                                html.P(
                                    (
                                        "Hover over the cortical surface "
                                        "to inspect regional values. "
                                        "Click a region to select it."
                                    ),
                                    className="figure-description",
                                ),

                                dcc.Graph(
                                    id="brain-3d-graph",

                                    config={
                                        "displaylogo": False,
                                        "scrollZoom": True,
                                    },

                                    style={
                                        "height": "750px",
                                    },
                                ),
                            ],
                        ),

                        # ==================================================
                        # NODAL PLOTLY FIGURES
                        # ==================================================

                        html.Div(

                            className="two-columns",

                            children=[

                                html.Div(

                                    className="graph-card",

                                    children=[

                                        dcc.Graph(
                                            id="top-regions-graph",
                                        ),
                                    ],
                                ),

                                html.Div(

                                    className="graph-card",

                                    children=[

                                        dcc.Graph(
                                            id="region-density-graph",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


# ============================================================
# 5. GLOBAL METRICS CALLBACK
# ============================================================

@callback(

    Output(
        "global-main-graph",
        "figure",
    ),

    Output(
        "iq-scatter",
        "figure",
    ),

    Output(
        "global-density-profile",
        "figure",
    ),

    Input(
        "global-analysis",
        "value",
    ),

    Input(
        "global-method",
        "value",
    ),

    Input(
        "global-metric",
        "value",
    ),

    Input(
        "global-density",
        "value",
    ),
)
def update_global_figures(
    analysis,
    method,
    metric,
    density,
):

    # ========================================================
    # MAIN FIGURE
    # ========================================================

    if analysis == "spearman":

        spearman_df = compute_spearman_by_density(
            dataframe=GLOBAL_DATA,
            method=method,
            metrics=GLOBAL_METRICS,
        )

        main_fig = make_spearman_figure(

            spearman_df,

            title=(
                "Spearman rho of global topological features"
                "<br>"
                f"at various connection densities for {method}"
            ),
        )

    elif analysis == "sed":

        sed_df = compute_global_sed_by_density(
            dataframe=NODAL_DATA,
            method=method,
        )

        main_fig = make_global_sed_figure(
            dataframe=sed_df,
            method=method,
        )

    else:

        raise ValueError(
            f"Unknown analysis: {analysis}"
        )

    # ========================================================
    # IQ SCATTER
    # ========================================================
    iq_df = get_iq_metric_data(
    dataframe=GLOBAL_DATA,
    method=method,
    metric=metric,
    density=density,
    )

    iq_statistics = compute_iq_metric_statistics(
        dataframe=iq_df,
    )

    iq_fig = make_iq_scatter_figure(
        dataframe=iq_df,
        metric=metric,
        density=density,
        statistics=iq_statistics,
    )
   

    # ========================================================
    # GROUP DENSITY PROFILE
    # ========================================================

    profile_df = get_group_metric_profile(
        dataframe=GLOBAL_DATA,
        method=method,
        metric=metric,
    )

    profile_fig = make_group_density_figure(
        summary_df=profile_df,
        metric=metric,
    )

    return (
        main_fig,
        iq_fig,
        profile_fig,
    )


# ============================================================
# 6. REGION DROPDOWN CALLBACK
# ============================================================

@callback(

    Output(
        "region-dropdown",
        "options",
    ),

    Output(
        "region-dropdown",
        "value",
    ),

    Input(
        "nodal-method",
        "value",
    ),

    Input(
        "nodal-feature",
        "value",
    ),

    Input(
        "nodal-density",
        "value",
    ),
)
def update_region_dropdown(
    method,
    feature,
    density,
):

    selected = get_nodal_values(
        dataframe=NODAL_DATA,
        method=method,
        feature=feature,
        density=density,
    )

    regions = sorted(
        selected["Region"]
        .dropna()
        .unique()
    )

    options = [
        {
            "label": region,
            "value": region,
        }
        for region in regions
    ]

    default_region = (
        regions[0]
        if regions
        else None
    )

    return (
        options,
        default_region,
    )


# ============================================================
# 7. STATIC MNE IMAGE CALLBACK
# ============================================================

@callback(

    Output(
        "mne-brain-image",
        "src",
    ),

    Input(
        "mne-method",
        "value",
    ),

    Input(
        "mne-feature",
        "value",
    ),
)
def update_mne_image(
    method,
    feature,
):

    return get_mne_image_path(
        method=method,
        feature=feature,
        density=0.15,
        parcellation="500.aparc",
    )


# ============================================================
# 8. INTERACTIVE 3D BRAIN CALLBACK
# ============================================================

@callback(

    Output(
        "brain-3d-graph",
        "figure",
    ),

    Input(
        "nodal-method",
        "value",
    ),

    Input(
        "nodal-feature",
        "value",
    ),

    Input(
        "nodal-density",
        "value",
    ),
)
def update_brain_3d(
    method,
    feature,
    density,
):

    selected = get_nodal_values(
        dataframe=NODAL_DATA,
        method=method,
        feature=feature,
        density=density,
    )

    return make_brain_3d_figure(

        dataframe=selected,

        title=(
            f"{feature} — {method}"
            "<br>"
            f"Gifted − Controls | "
            f"Density = {density:.2f}"
        ),
    )


# ============================================================
# 9. CLICK ON BRAIN -> SELECT REGION
# ============================================================

@callback(

    Output(
        "region-dropdown",
        "value",
        allow_duplicate=True,
    ),

    Input(
        "brain-3d-graph",
        "clickData",
    ),

    State(
        "nodal-method",
        "value",
    ),

    State(
        "nodal-feature",
        "value",
    ),

    State(
        "nodal-density",
        "value",
    ),

    prevent_initial_call=True,
)
def select_region_from_brain(
    click_data,
    method,
    feature,
    density,
):

    if not click_data:
        return no_update

    point = click_data[
        "points"
    ][0]

    region_name = point.get(
        "customdata"
    )

    if not region_name:
        return no_update

    if isinstance(
        region_name,
        (list, tuple),
    ):
        region_name = region_name[0]

    selected = get_nodal_values(
        dataframe=NODAL_DATA,
        method=method,
        feature=feature,
        density=density,
    )

    target_key = normalize_key(
        region_name
    )

    matching_regions = [
        region
        for region in selected["Region"]
        .dropna()
        .unique()
        if normalize_key(region) == target_key
    ]

    if not matching_regions:
        return no_update

    return matching_regions[0]


# ============================================================
# 10. NODAL PLOTLY CALLBACK
# ============================================================

@callback(

    Output(
        "top-regions-graph",
        "figure",
    ),

    Output(
        "region-density-graph",
        "figure",
    ),

    Input(
        "nodal-method",
        "value",
    ),

    Input(
        "nodal-feature",
        "value",
    ),

    Input(
        "nodal-density",
        "value",
    ),

    Input(
        "region-dropdown",
        "value",
    ),
)
def update_nodal_figures(
    method,
    feature,
    density,
    region,
):

    selected = get_nodal_values(
        dataframe=NODAL_DATA,
        method=method,
        feature=feature,
        density=density,
    )

    if selected.empty:

        raise ValueError(
            "No nodal data found for "
            f"method={method}, "
            f"feature={feature}, "
            f"density={density}."
        )

    # --------------------------------------------------------
    # Top regional differences
    # --------------------------------------------------------

    top_df = get_top_regions(
        dataframe=NODAL_DATA,
        method=method,
        feature=feature,
        density=density,
        n_regions=15,
    )

    top_fig = make_top_regions_figure(
        dataframe=top_df,
        feature=feature,
        density=density,
    )

    # --------------------------------------------------------
    # Selected region across densities
    # --------------------------------------------------------

    if region is None:

        region = (
            selected["Region"]
            .dropna()
            .iloc[0]
        )

    region_df = get_region_density_profile(
        dataframe=NODAL_DATA,
        method=method,
        feature=feature,
        region=region,
    )

    region_fig = make_region_density_figure(
        dataframe=region_df,
        region=region,
        feature=feature,
    )

    return (
        top_fig,
        region_fig,
    )


# ============================================================
# 11. RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=8050,
    )