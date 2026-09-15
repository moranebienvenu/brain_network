## still in process
# ============================================================
# API FOR WIRED PAPER <-> DASHBOARD
# ============================================================

from flask import request, jsonify
import json

from config import (
    METHODS,
    PARCELLATIONS,
    GLOBAL_METRICS,
    NODAL_METRICS
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
    get_region_density_profile,
    compute_global_sed_by_density,
    compute_global_sed_all_methods,
    get_top_regions_across_densities,
    get_high_nodes_values,
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
    make_method_comparison_figure,
    make_regional_heatmap_figure,
)

from figures.brain_3d import (
    make_brain_3d_figure,
    make_high_nodes_brain_figure,
)


# ============================================================
# 1. LOAD DATA
# ============================================================

GLOBAL_DATA = load_global_data()
NODAL_DATA = load_nodal_data()
HIGH_NODES_DATA=load_high_nodes_data()


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def figure_to_json(figure):
    """
    Convert a Plotly figure into a JSON-compatible dictionary.
    """
    return json.loads(
        figure.to_json()
    )


def dataframe_to_json(dataframe):
    """
    Convert a pandas DataFrame into a JSON-compatible list.
    """
    return dataframe.to_dict(orient="records")


def get_json_params():
    """
    Get parameters from a POST request.
    """
    params = request.get_json(silent=True)

    if params is None:
        return None, jsonify({
            "error": "Request body must contain valid JSON."
        }), 400

    return params, None, None


# ============================================================
# 3. HEALTH CHECK
# ============================================================

def register_api(server):

    @server.route("/api/health", methods=["GET"])
    def api_health():
        """
        Check whether the API is running.
        """

        return jsonify({
            "status": "ok",
            "message": "Gifted Brain Network API is running."
        })


    # ========================================================
    # 4. AVAILABLE PARAMETERS
    # ========================================================

    @server.route("/api/parameters", methods=["GET"])
    def api_parameters():
        """
        Return parameters available to the Wired Paper.
        """

        global_densities = sorted(
            GLOBAL_DATA["Density"]
            .dropna()
            .unique()
            .tolist()
        )

        nodal_densities = sorted(
            NODAL_DATA["Density"]
            .dropna()
            .unique()
            .tolist()
        )

        high_node_densities = sorted(
            HIGH_NODES_DATA["Density"]
            .dropna()
            .unique()
            .tolist()
        )

        return jsonify({

            "methods":  METHODS,

            "parcellations": PARCELLATIONS,
                
            "global_metrics": GLOBAL_METRICS,

            "nodal_metrics": NODAL_METRICS,

            "global_densities": global_densities,

            "nodal_densities": nodal_densities,

            "high_node_densities": high_node_densities,

        

        })


    # ========================================================
    # 5. GLOBAL — SPEARMAN
    # ========================================================

    @server.route(
        "/api/global/spearman",
        methods=["GET"]
    )
    def api_global_spearman():

        try:

            method = request.args.get(
                "method",
                "MSN"
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )

            spearman_df = compute_spearman_by_density(
                dataframe=GLOBAL_DATA,
                method=method,
                metrics=GLOBAL_METRICS,
                parcellation=parcellation
            )

            figure = make_spearman_figure(
                spearman_df,
                title=(
                    "Spearman rho of global "
                    "topological features"
                    "<br>"
                    f"at various connection "
                    f"densities for {method} - "
                    f"{parcellation} parcellation"
                ),
            )

            return jsonify({
                "figure": figure_to_json(figure),

                "parameters": {
                    "method": method,
                    "parcellation": parcellation,
                }
            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # 6. GLOBAL — IQ SCATTER
    # ========================================================

    @server.route(
        "/api/global/iq-scatter",
        methods=["GET"]
    )
    def api_global_iq_scatter():

        try:

            method = request.args.get(
                "method",
                "MSN"
            )

            metric = request.args.get(
                "metric",
                "Global Efficiency"
            )

            density = request.args.get(
                "density",
                0.10,
                type=float
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )

            # ----------------------------------------------
            # Retrieve data
            # ----------------------------------------------

            iq_df = get_iq_metric_data(
                dataframe=GLOBAL_DATA,
                method=method,
                metric=metric,
                density=density,
                parcellation=parcellation
            )

            if iq_df.empty:

                return jsonify({
                    "error": (
                        "No data found for the "
                        "requested parameters."
                    )
                }), 404

            # ----------------------------------------------
            # Statistics
            # ----------------------------------------------

            statistics = compute_iq_metric_statistics(
                dataframe=iq_df,
            )

            # ----------------------------------------------
            # Figure
            # ----------------------------------------------

            figure = make_iq_scatter_figure(
                dataframe=iq_df,
                metric=metric,
                density=density,
                parcellation=parcellation,
                statistics=statistics,
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "parameters": {
                    "method": method,
                    "metric": metric,
                    "density": density,
                    "parcellation": parcellation,
                },

                "statistics": statistics,

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # 7. GLOBAL — IQ SCATTER DATA
    # ========================================================

    @server.route(
        "/api/data/global/iq-scatter",
        methods=["GET"]
    )
    def api_global_iq_scatter_data():

        try:

            method = request.args.get(
                "method",
                "MSN"
            )

            metric = request.args.get(
                "metric",
                "Global Efficiency"
            )

            density = request.args.get(
                "density",
                0.10,
                type=float
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )

            iq_df = get_iq_metric_data(
                dataframe=GLOBAL_DATA,
                method=method,
                metric=metric,
                density=density,
                parcellation=parcellation,
            )

            if iq_df.empty:

                return jsonify({
                    "error": "No data found."
                }), 404

            return jsonify({

                "data": dataframe_to_json(
                    iq_df
                ),

                "parameters": {
                    "method": method,
                    "metric": metric,
                    "density": density,
                    "parcellation": parcellation,
                }

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # 8. GLOBAL — DENSITY PROFILE
    # ========================================================

    @server.route(
        "/api/global/density-profile",
        methods=["GET"]
    )
    def api_global_density_profile():

        try:

            method = request.args.get(
                "method",
                "MSN"
            )

            metric = request.args.get(
                "metric",
                "Global Efficiency"
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )

            profile_df = get_group_metric_profile(
                dataframe=GLOBAL_DATA,
                method=method,
                metric=metric,
                parcellation=parcellation,
            )

        
            figure = make_group_density_figure(
                summary_df=profile_df,
                metric=metric,
                parcellation=parcellation,
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "parameters": {
                    "method": method,
                    "metric": metric,
                    "parcellation": parcellation,
                }

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # 9. GLOBAL — SED
    # ========================================================

    @server.route(
        "/api/global/sed",
        methods=["GET"]
    )
    def api_global_sed():

        try:

            method = request.args.get(
                "method",
                "MSN"
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )

            sed_df = compute_global_sed_by_density(
                dataframe=NODAL_DATA,
                method=method,
                parcellation=parcellation
            )

            figure = make_global_sed_figure(
                dataframe=sed_df,
                method=method,
                parcellation=parcellation
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "parameters": {
                    "method": method,
                    "parcellation": parcellation,
                }

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # 10. NODAL — TOP REGIONS
    # ========================================================

    @server.route(
        "/api/nodal/top-regions",
        methods=["GET"]
    )
    def api_nodal_top_regions():

        try:

            method = request.args.get(
                "method",
                "MSN"
            )

            feature = request.args.get(
                "feature",
                "Clustering Coefficient"
            )

            density = request.args.get(
                "density",
                0.15,
                type=float
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )

            n_regions = request.args.get(
                "n_regions",
                15,
                type=int
            )

            top_df = get_top_regions(
                dataframe=NODAL_DATA,
                method=method,
                feature=feature,
                density=density,
                parcellation=parcellation,
                n_regions=n_regions,
            )

            figure = make_top_regions_figure(
                dataframe=top_df,
                feature=feature,
                density=density,
                parcellation=parcellation,
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "data": dataframe_to_json(
                    top_df
                ),

                "parameters": {
                    "method": method,
                    "feature": feature,
                    "density": density,
                    "parcellation": parcellation,
                    "n_regions": n_regions,
                }

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # 11. NODAL — REGION DENSITY
    # ========================================================

    @server.route(
        "/api/nodal/region-density",
        methods=["GET"]
    )
    def api_nodal_region_density():

        try:

            method = request.args.get(
                "method",
                "MSN"
            )

            feature = request.args.get(
                "feature",
                "Clustering Coefficient"
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )

            region = request.args.get(
                "region"
            )

            if region is None:

                return jsonify({
                    "error": "Region parameter is required."
                }), 400

            region_df = get_region_density_profile(
                dataframe=NODAL_DATA,
                method=method,
                feature=feature,
                region=region,
                parcellation=parcellation,
            )

            if region_df.empty:

                return jsonify({
                    "error": "No data found for this region."
                }), 404

            figure = make_region_density_figure(
                dataframe=region_df,
                region=region,
                feature=feature,
                parcellation=parcellation,
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "data": dataframe_to_json(
                    region_df
                ),

                "parameters": {
                    "method": method,
                    "feature": feature,
                    "region": region,
                    "parcellation": parcellation,
                }

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # 12. NODAL — BRAIN 3D
    # ========================================================

    @server.route(
        "/api/nodal/brain",
        methods=["GET"]
    )
    def api_nodal_brain():

        try:

            method = request.args.get(
                "method",
                "MSN"
            )

            feature = request.args.get(
                "feature",
                "Clustering Coefficient"
            )

            density = request.args.get(
                "density",
                0.15,
                type=float
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )



            selected = get_nodal_values(
                dataframe=NODAL_DATA,
                method=method,
                feature=feature,
                density=density,
                parcellation=parcellation,
            )

            if selected.empty:

                return jsonify({
                    "error": (
                        "No nodal data found for "
                        "the requested parameters."
                    )
                }), 404

            figure = make_brain_3d_figure(
                dataframe=selected,
                parcellation=parcellation,
                title=(
                    f"{feature} — {method} - {parcellation} "
                    "<br>"
                    "Gifted − Controls | "
                    f"Density = {density:.2f}"
                ),
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "data": dataframe_to_json(
                    selected
                ),

                "parameters": {
                    "method": method,
                    "feature": feature,
                    "density": density,
                    "parcellation":parcellation,
                }

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500
        
    
    # ========================================================
    # 13. NODAL — REGIONAL HEATMAP
    # ========================================================

    @server.route(
        "/api/nodal/heatmap",
        methods=["GET"]
    )
    def api_nodal_heatmap():

        try:

            method = request.args.get(
                "method",
                "MSN"
            )

            feature = request.args.get(
                "feature",
                "Clustering Coefficient"
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )

            show_values = request.args.get(
                "show_values",
                "true"
            ).lower() == "true"

            heatmap_df, regions_to_plot = (
                get_top_regions_across_densities(
                    dataframe=NODAL_DATA,
                    method=method,
                    feature=feature,
                    parcellation=parcellation,
                    top_n=15,
                )
            )

            if heatmap_df.empty:

                return jsonify({
                    "error": "No heatmap data found."
                }), 404

            figure = make_regional_heatmap_figure(
                dataframe=heatmap_df,
                regions_to_plot=regions_to_plot,
                feature=feature,
                method=method,
                parcellation=parcellation,
                show_values=show_values,
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "data": dataframe_to_json(
                    heatmap_df
                ),

                "regions": regions_to_plot,

                "parameters": {
                    "method": method,
                    "feature": feature,
                    "parcellation": parcellation,
                    "show_values": show_values,
                }

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500

    # ========================================================
    # 14. NODAL — METHOD COMPARISON
    # ========================================================

    @server.route(
        "/api/nodal/method-comparison",
        methods=["GET"]
    )
    def api_nodal_method_comparison():

        try:

            feature = request.args.get(
                "feature",
                "Clustering Coefficient"
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )

            comparison_df = compute_global_sed_all_methods(
                dataframe=NODAL_DATA,
                methods=METHODS,
                parcellation=parcellation,
            )

            if comparison_df.empty:

                return jsonify({
                    "error": "No method comparison data found."
                }), 404

            figure = make_method_comparison_figure(
                dataframe=comparison_df,
                feature=feature,
                parcellation=parcellation,
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "data": dataframe_to_json(
                    comparison_df
                ),

                "parameters": {
                    "feature": feature,
                    "parcellation": parcellation,
                }

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500
        
    # ========================================================
    # 15. NODAL — HIGH-VERSATILITY NODES
    # ========================================================

    @server.route(
        "/api/nodal/high-nodes",
        methods=["GET"]
    )
    def api_nodal_high_nodes():

        try:

            method = request.args.get(
                "method",
                "MSN"
            )

            parcellation = request.args.get(
                "parcellation",
                "500.aparc"
            )

            density = request.args.get(
                "density",
                0.15,
                type=float
            )

            group = request.args.get(
                "group",
                "Gifted"
            )

            high_nodes_df = get_high_nodes_values(
                dataframe=HIGH_NODES_DATA,
                method=method,
                parcellation=parcellation,
                density=density,
                group=group,
            )

            if high_nodes_df.empty:

                return jsonify({
                    "error": (
                        "No high-versatility nodes found "
                        "for the requested parameters."
                    )
                }), 404

            figure = make_high_nodes_brain_figure(
                dataframe=high_nodes_df,
                parcellation=parcellation,
                group=group,

                title=(
                    f"{group} — High-versatility nodes"
                    "<br>"
                    f"{method} — {parcellation} — "
                    f"Density = {density:.2f}"
                ),
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "data": dataframe_to_json(
                    high_nodes_df
                ),

                "parameters": {
                    "method": method,
                    "parcellation": parcellation,
                    "density": density,
                    "group": group,
                }

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500