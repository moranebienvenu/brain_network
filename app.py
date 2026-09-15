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
    PARCELLATIONS,
    GLOBAL_METRICS,
    NODAL_METRICS,
)

from services.data_loader import (
    load_global_data,
    load_nodal_data,
    load_high_nodes_data,
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
    compute_global_sed_by_density,
    compute_global_sed_all_methods,
    get_top_regions_across_densities,
    get_high_nodes_values,
)

from figures.global_figures import (
    make_spearman_figure,
    make_iq_scatter_figure,
    make_group_density_figure,
    
)

from figures.nodal_figures import (
    make_top_regions_figure,
    make_method_comparison_figure,
    make_regional_heatmap_figure,
)

from figures.brain_3d import (
    make_brain_3d_figure,
    make_high_nodes_brain_figure,
    normalize_key,
    
)


# ============================================================
# 1. LOAD DATA
# ============================================================

GLOBAL_DATA = load_global_data()
NODAL_DATA = load_nodal_data()
HIGH_NODES_DATA=load_high_nodes_data()


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

from api import register_api

register_api(server)




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

                                # Parcellation

                                html.Div(
                                    [
                                        html.Label("Parcellation"),

                                        dcc.Dropdown(
                                            id="global-parcellation",

                                            options=[
                                                {
                                                    "label": parcellation,
                                                    "value": parcellation,
                                                }
                                                for parcellation in PARCELLATIONS
                                            ],

                                            value="500.aparc",
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

                                # Parcellation

                                html.Div(
                                    [
                                        html.Label("Parcellation"),

                                        dcc.Dropdown(
                                            id="nodal-parcellation",

                                            options=[
                                                {
                                                    "label": parcellation,
                                                    "value": parcellation,
                                                }
                                                for parcellation in PARCELLATIONS
                                            ],

                                            value="500.aparc",
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
                                        "Explore regional Gifted-Control differences "
                                        "or compare high-versatility nodes between groups."
                                    ),
                                    className="figure-description",
                                ),

                                # ------------------------------------------
                                # 3D visualization mode
                                # ------------------------------------------

                                html.Div(

                                    className="controls",

                                    children=[

                                        html.Div(
                                            [
                                                html.Label(
                                                    "3D visualization"
                                                ),

                                                dcc.Dropdown(
                                                    id="brain-visualization-mode",

                                                    options=[
                                                        {
                                                            "label": "Gifted − Controls differences",
                                                            "value": "difference",
                                                        },
                                                        {
                                                            "label": "High-versatility nodes",
                                                            "value": "high-nodes",
                                                        },
                                                    ],

                                                    value="difference",
                                                    clearable=False,
                                                ),
                                            ]
                                        ),

                                        html.Div(
                                            [

                                                html.Div(
                                                    [
                                                        dcc.Checklist(
                                                            id="compare-parcellations",

                                                            options=[
                                                                {
                                                                    "label": "",
                                                                    "value": "compare",
                                                                },
                                                            ],

                                                            value=[],

                                                            inputStyle={
                                                                "marginRight": "0px",
                                                            },

                                                            style={
                                                                "margin": "0px",
                                                            },
                                                        ),

                                                        html.Span(
                                                            "Compare both parcellations",

                                                            style={
                                                                "marginLeft": "10px",
                                                                "fontSize": "18px",
                                                                "fontWeight": "500",
                                                            },
                                                        ),
                                                    ],

                                                    style={
                                                        "padding": "10px 14px",
                                                        "border": "1px solid #c7c7c7",
                                                        "borderRadius": "8px",
                                                        "backgroundColor": "white",
                                                        "display": "flex",
                                                        "alignItems": "center",
                                                        "marginTop": "20px",
                                                    },
                                                ),
                                            ]
                                        ),
                                    ],
                                ),

                                # ------------------------------------------
                                # Gifted - Controls brain
                                # ------------------------------------------

                                html.Div(

                                    id="difference-brain-container",

                                    children=[

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

                                html.Div(

                                    id="parcellation-comparison-container",

                                    className="two-columns",

                                    style={
                                        "display": "none",
                                    },

                                    children=[

                                        html.Div(
                                            children=[

                                                dcc.Graph(
                                                    id="aparc-brain-3d",

                                                    config={
                                                        "displaylogo": False,
                                                        "scrollZoom": True,
                                                    },
                                                ),
                                            ],
                                        ),

                                        html.Div(
                                            children=[

                                                dcc.Graph(
                                                    id="500-aparc-brain-3d",

                                                    config={
                                                        "displaylogo": False,
                                                        "scrollZoom": True,
                                                    },
                                                ),
                                            ],
                                        ),
                                    ],
                                ),

                                # ------------------------------------------
                                # High-versatility brains
                                # ------------------------------------------

                                html.Div(

                                    id="high-nodes-brain-container",

                                    className="two-columns",

                                    style={
                                        "display": "none",
                                    },

                                    children=[

                                        html.Div(

                                            children=[

                                                dcc.Graph(
                                                    id="control-high-nodes-brain",

                                                    config={
                                                        "displaylogo": False,
                                                        "scrollZoom": True,
                                                    },
                                                ),
                                            ],
                                        ),

                                        html.Div(

                                            children=[

                                                dcc.Graph(
                                                    id="gifted-high-nodes-brain",

                                                    config={
                                                        "displaylogo": False,
                                                        "scrollZoom": True,
                                                    },
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                
                                # ------------------------------------------
                                # High-versatility nodes
                                # Parcellation comparison
                                # ------------------------------------------

                                html.Div(

                                    id="high-nodes-parcellation-comparison-container",

                                    style={
                                        "display": "none",
                                    },

                                    children=[

                                        html.Div(

                                            className="two-columns",

                                            children=[

                                                html.Div(

                                                    children=[

                                                        dcc.Graph(
                                                            id="control-aparc-high-nodes-brain",

                                                            config={
                                                                "displaylogo": False,
                                                                "scrollZoom": True,
                                                            },
                                                        ),
                                                    ],
                                                ),

                                                html.Div(

                                                    children=[

                                                        dcc.Graph(
                                                            id="control-500-aparc-high-nodes-brain",

                                                            config={
                                                                "displaylogo": False,
                                                                "scrollZoom": True,
                                                            },
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),

                                        html.Div(

                                            className="two-columns",

                                            children=[

                                                html.Div(

                                                    children=[

                                                        dcc.Graph(
                                                            id="gifted-aparc-high-nodes-brain",

                                                            config={
                                                                "displaylogo": False,
                                                                "scrollZoom": True,
                                                            },
                                                        ),
                                                    ],
                                                ),

                                                html.Div(

                                                    children=[

                                                        dcc.Graph(
                                                            id="gifted-500-aparc-high-nodes-brain",

                                                            config={
                                                                "displaylogo": False,
                                                                "scrollZoom": True,
                                                            },
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                                    
                
                        # ==================================================
                        # NODAL PLOTLY FIGURES
                        # ==================================================

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

                                html.Div(
                                    [
                                        html.Label(
                                            "Heatmap values"
                                        ),

                                        html.Div(
                                            [
                                                dcc.Checklist(
                                                    id="heatmap-values",

                                                    options=[
                                                        {
                                                            "label": "Show values",
                                                            "value": "show",
                                                        },
                                                    ],

                                                    value=["show"],

                                                    inputStyle={
                                                        "marginRight": "20px",
                                                    },

                                                    labelStyle={
                                                        "cursor": "pointer",
                                                    },
                                                ),
                                            ],

                                            style={
                                                "marginLeft": "25px",
                                                "padding": "8px 12px",
                                                "border": "1px solid #c7c7c7",
                                                "borderRadius": "8px",
                                                "backgroundColor": "white",
                                                "display": "inline-block",
                                            },
                                        ),
                                    ],

                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "15px",
                                    },
                                ),

                                dcc.Graph(
                                    id="regional-heatmap-graph",
                                ),
                            ],
                        ),

                        html.Div(

                            className="graph-card",

                            children=[

                                html.H3(
                                    "Comparison across network construction methods"
                                ),

                                dcc.Graph(
                                    id="method-comparison-graph",
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
        "global-parcellation",
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
    parcellation,
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
            parcellation=parcellation,
        )

        main_fig = make_spearman_figure(

            spearman_df,

            title=(
                "Spearman rho of global topological features"
                "<br>"
                f"at various connection densities for {method} - {parcellation} parcellation"
            ),
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
    parcellation=parcellation,
    )

    iq_statistics = compute_iq_metric_statistics(
        dataframe=iq_df,
    )

    iq_fig = make_iq_scatter_figure(
        dataframe=iq_df,
        metric=metric,
        density=density,
        parcellation=parcellation,
        statistics=iq_statistics,
    )
   

    # ========================================================
    # GROUP DENSITY PROFILE
    # ========================================================

    profile_df = get_group_metric_profile(
        dataframe=GLOBAL_DATA,
        method=method,
        metric=metric,
        parcellation=parcellation,
    )

    profile_fig = make_group_density_figure(
        summary_df=profile_df,
        metric=metric,
        parcellation=parcellation,
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
        "nodal-parcellation",
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
    parcellation,
    feature,
    density,
):

    selected = get_nodal_values(
        dataframe=NODAL_DATA,
        method=method,
        parcellation=parcellation,
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
# 7. INTERACTIVE 3D BRAIN CALLBACK
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
        "nodal-parcellation",
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
    parcellation,
    feature,
    density,
):

    selected = get_nodal_values(
        dataframe=NODAL_DATA,
        method=method,
        feature=feature,
        density=density,
        parcellation=parcellation,
    )

    return make_brain_3d_figure(

        dataframe=selected,
        parcellation=parcellation,

        title=(
            f"{feature} — {method} — {parcellation} "
            "<br>"
            f"|Gifted − Controls | Density = {density:.2f}"
        ),
    )

# ============================================================
# 7B. 3D VISUALIZATION MODE CALLBACK
# ============================================================

@callback(

    Output(
        "difference-brain-container",
        "style",
    ),

    Output(
        "parcellation-comparison-container",
        "style",
    ),

    Output(
        "high-nodes-brain-container",
        "style",
    ),

    Output(
        "high-nodes-parcellation-comparison-container",
        "style",
    ),

    Input(
        "brain-visualization-mode",
        "value",
    ),

    Input(
        "compare-parcellations",
        "value",
    ),
)
def update_brain_visualization_mode(
    visualization_mode,
    compare_parcellations,
):

    compare = (
        "compare"
        in compare_parcellations
    )

    # --------------------------------------------------------
    # Gifted - Controls differences
    # --------------------------------------------------------

    if visualization_mode == "difference":

        if compare:

            return (
                {"display": "none"},
                {"display": "grid"},
                {"display": "none"},
                {"display": "none"},
            )

        return (
            {"display": "block"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
        )

    # --------------------------------------------------------
    # High-versatility nodes
    # --------------------------------------------------------

    if compare:

        return (
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "block"},
        )

    return (
        {"display": "none"},
        {"display": "none"},
        {"display": "grid"},
        {"display": "none"},
    )


# ============================================================
# 7C. PARCELLATION COMPARISON CALLBACK
# ============================================================

@callback(

    Output(
        "aparc-brain-3d",
        "figure",
    ),

    Output(
        "500-aparc-brain-3d",
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
def update_parcellation_comparison(
    method,
    feature,
    density,
):

    # --------------------------------------------------------
    # aparc
    # --------------------------------------------------------

    aparc_data = get_nodal_values(
        dataframe=NODAL_DATA,
        method=method,
        parcellation="aparc",
        feature=feature,
        density=density,
    )

    aparc_fig = make_brain_3d_figure(
        dataframe=aparc_data,
        parcellation="aparc",

        title=(
            f"{feature} — {method}"
            "<br>"
            f"aparc | Gifted − Controls | "
            f"Density = {density:.2f}"
        ),
    )

    # --------------------------------------------------------
    # 500.aparc
    # --------------------------------------------------------

    aparc500_data = get_nodal_values(
        dataframe=NODAL_DATA,
        method=method,
        parcellation="500.aparc",
        feature=feature,
        density=density,
    )

    aparc500_fig = make_brain_3d_figure(
        dataframe=aparc500_data,
        parcellation="500.aparc",

        title=(
            f"{feature} — {method}"
            "<br>"
            f"500.aparc | Gifted − Controls | "
            f"Density = {density:.2f}"
        ),
    )

    return (
        aparc_fig,
        aparc500_fig,
    )

# ============================================================
# 7D. HIGH-VERSATILITY NODES BRAINS CALLBACK
# ============================================================

@callback(

    Output(
        "control-high-nodes-brain",
        "figure",
    ),

    Output(
        "gifted-high-nodes-brain",
        "figure",
    ),

    Input(
        "nodal-method",
        "value",
    ),

    Input(
        "nodal-parcellation",
        "value",
    ),

    Input(
        "nodal-density",
        "value",
    ),
)
def update_high_nodes_brains(
    method,
    parcellation,
    density,
):

    # --------------------------------------------------------
    # Control
    # --------------------------------------------------------

    control_data = get_high_nodes_values(
        dataframe=HIGH_NODES_DATA,
        method=method,
        parcellation=parcellation,
        density=density,
        group="Control",
    )

    control_fig = make_high_nodes_brain_figure(
        dataframe=control_data,
        parcellation=parcellation,
        group="Control",

        title=(
            "Control — High-versatility nodes"
            "<br>"
            f"{method} — {parcellation} — "
            f"Density = {density:.2f}"
        ),
    )

    # --------------------------------------------------------
    # Gifted
    # --------------------------------------------------------

    gifted_data = get_high_nodes_values(
        dataframe=HIGH_NODES_DATA,
        method=method,
        parcellation=parcellation,
        density=density,
        group="Gifted",
    )

    gifted_fig = make_high_nodes_brain_figure(
        dataframe=gifted_data,
        parcellation=parcellation,
        group="Gifted",

        title=(
            "Gifted — High-versatility nodes"
            "<br>"
            f"{method} — {parcellation} — "
            f"Density = {density:.2f}"
        ),
    )

    return (
        control_fig,
        gifted_fig,
    )

# ============================================================
# 7E. HIGH-VERSATILITY PARCELLATION COMPARISON CALLBACK
# ============================================================

@callback(

    Output(
        "control-aparc-high-nodes-brain",
        "figure",
    ),

    Output(
        "control-500-aparc-high-nodes-brain",
        "figure",
    ),

    Output(
        "gifted-aparc-high-nodes-brain",
        "figure",
    ),

    Output(
        "gifted-500-aparc-high-nodes-brain",
        "figure",
    ),

    Input(
        "nodal-method",
        "value",
    ),

    Input(
        "nodal-density",
        "value",
    ),
)
def update_high_nodes_parcellation_comparison(
    method,
    density,
):

    # --------------------------------------------------------
    # Control - aparc
    # --------------------------------------------------------

    control_aparc_data = get_high_nodes_values(
        dataframe=HIGH_NODES_DATA,
        method=method,
        parcellation="aparc",
        density=density,
        group="Control",
    )

    control_aparc_fig = make_high_nodes_brain_figure(
        dataframe=control_aparc_data,
        parcellation="aparc",
        group="Control",

        title=(
            "Control — aparc"
            "<br>"
            f"{method} — Density = {density:.2f}"
        ),
    )

    # --------------------------------------------------------
    # Control - 500.aparc
    # --------------------------------------------------------

    control_500_data = get_high_nodes_values(
        dataframe=HIGH_NODES_DATA,
        method=method,
        parcellation="500.aparc",
        density=density,
        group="Control",
    )

    control_500_fig = make_high_nodes_brain_figure(
        dataframe=control_500_data,
        parcellation="500.aparc",
        group="Control",

        title=(
            "Control — 500.aparc"
            "<br>"
            f"{method} — Density = {density:.2f}"
        ),
    )

    # --------------------------------------------------------
    # Gifted - aparc
    # --------------------------------------------------------

    gifted_aparc_data = get_high_nodes_values(
        dataframe=HIGH_NODES_DATA,
        method=method,
        parcellation="aparc",
        density=density,
        group="Gifted",
    )

    gifted_aparc_fig = make_high_nodes_brain_figure(
        dataframe=gifted_aparc_data,
        parcellation="aparc",
        group="Gifted",

        title=(
            "Gifted — aparc"
            "<br>"
            f"{method} — Density = {density:.2f}"
        ),
    )

    # --------------------------------------------------------
    # Gifted - 500.aparc
    # --------------------------------------------------------

    gifted_500_data = get_high_nodes_values(
        dataframe=HIGH_NODES_DATA,
        method=method,
        parcellation="500.aparc",
        density=density,
        group="Gifted",
    )

    gifted_500_fig = make_high_nodes_brain_figure(
        dataframe=gifted_500_data,
        parcellation="500.aparc",
        group="Gifted",

        title=(
            "Gifted — 500.aparc"
            "<br>"
            f"{method} — Density = {density:.2f}"
        ),
    )

    return (
        control_aparc_fig,
        control_500_fig,
        gifted_aparc_fig,
        gifted_500_fig,
    )


# ============================================================
# 8. CLICK ON BRAIN -> SELECT REGION
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
        "nodal-parcellation",
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
    parcellation,
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
        parcellation=parcellation,
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
# 9. NODAL PLOTLY CALLBACK
# ============================================================

@callback(

    Output(
        "top-regions-graph",
        "figure",
    ),

    Output(
    "regional-heatmap-graph",
    "figure",
    ),

    Input(
        "nodal-method",
        "value",
    ),

    Input(
        "nodal-parcellation",
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
        "heatmap-values",
        "value",
    ),

)

def update_nodal_figures(
    method,
    parcellation,
    feature,
    density,  
    heatmap_values,
):

    selected = get_nodal_values(
        dataframe=NODAL_DATA,
        method=method,
        feature=feature,
        density=density,
        parcellation=parcellation
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
        parcellation=parcellation,
        n_regions=15,
    )

    top_fig = make_top_regions_figure(
        dataframe=top_df,
        feature=feature,
        density=density,
        parcellation=parcellation
    )

    # --------------------------------------------------------
    # Regional heatmap across densities
    # --------------------------------------------------------

    heatmap_df, regions_to_plot = (
        get_top_regions_across_densities(
            dataframe=NODAL_DATA,
            method=method,
            feature=feature,
            parcellation=parcellation,
            top_n=15,
        )
    )

    heatmap_fig = make_regional_heatmap_figure(
        dataframe=heatmap_df,
        regions_to_plot=regions_to_plot,
        feature=feature,
        method=method,
        parcellation=parcellation,
        show_values=(
            "show" in heatmap_values
        ),
    )

    return (
        top_fig,
        heatmap_fig,
    )


# ============================================================
# 10. GLOBAL SED FOR ALL METHODS CALLBACK
# ============================================================
@callback(

    Output(
        "method-comparison-graph",
        "figure",
    ),

    Input(
        "nodal-parcellation",
        "value",
    ),

    Input(
        "nodal-feature",
        "value",
    ),
)
def update_method_comparison(
    parcellation,
    feature,
):

    comparison_df = compute_global_sed_all_methods(
        dataframe=NODAL_DATA,
        methods=METHODS,
        parcellation=parcellation,
    )

    return make_method_comparison_figure(
        dataframe=comparison_df,
        feature=feature,
        parcellation=parcellation,
    )

# ============================================================
# 11. RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=8050,
    )