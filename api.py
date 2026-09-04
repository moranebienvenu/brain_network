## still in process
# ============================================================
# API FOR WIRED PAPER <-> DASHBOARD
# ============================================================

from flask import request, jsonify

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
)


# ============================================================
# 1. LOAD DATA
# ============================================================

GLOBAL_DATA = load_global_data()
NODAL_DATA = load_nodal_data()


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def figure_to_json(figure):
    """
    Convert a Plotly figure into a JSON-compatible dictionary.
    """
    return figure.to_dict()


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

        return jsonify({

            "methods": [
                "MSN"
            ],

            "global_metrics": [
                "Global Efficiency"
            ],

            "nodal_metrics": [
                "Clustering Coefficient"
            ],

            "global_densities": global_densities,

            "nodal_densities": nodal_densities,

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

            spearman_df = compute_spearman_by_density(
                dataframe=GLOBAL_DATA,
                method=method,
                metrics=None,
            )

            figure = make_spearman_figure(
                spearman_df,
                title=(
                    "Spearman rho of global "
                    "topological features"
                    "<br>"
                    f"at various connection "
                    f"densities for {method}"
                ),
            )

            return jsonify({
                "figure": figure_to_json(figure),

                "parameters": {
                    "method": method
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

            # ----------------------------------------------
            # Retrieve data
            # ----------------------------------------------

            iq_df = get_iq_metric_data(
                dataframe=GLOBAL_DATA,
                method=method,
                metric=metric,
                density=density,
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

            iq_df = get_iq_metric_data(
                dataframe=GLOBAL_DATA,
                method=method,
                metric=metric,
                density=density,
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

            profile_df = get_group_metric_profile(
                dataframe=GLOBAL_DATA,
                method=method,
                metric=metric,
            )

            figure = make_group_density_figure(
                summary_df=profile_df,
                metric=metric,
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "parameters": {
                    "method": method,
                    "metric": metric,
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

            sed_df = compute_global_sed_by_density(
                dataframe=NODAL_DATA,
                method=method,
            )

            figure = make_global_sed_figure(
                dataframe=sed_df,
                method=method,
            )

            return jsonify({

                "figure": figure_to_json(
                    figure
                ),

                "parameters": {
                    "method": method,
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
                n_regions=n_regions,
            )

            figure = make_top_regions_figure(
                dataframe=top_df,
                feature=feature,
                density=density,
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
            )

            if region_df.empty:

                return jsonify({
                    "error": "No data found for this region."
                }), 404

            figure = make_region_density_figure(
                dataframe=region_df,
                region=region,
                feature=feature,
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

            selected = get_nodal_values(
                dataframe=NODAL_DATA,
                method=method,
                feature=feature,
                density=density,
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
                title=(
                    f"{feature} — {method}"
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
                }

            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500
