import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def make_spearman_figure(
    spearman_df,
    title=None,
):
    """
    Plot Spearman rho across densities.
    """

    fig = px.line(
        spearman_df,
        x="Density",
        y="Spearman_rho",
        color="Metric",
        markers=True,
        hover_data={
            "Density": ":.2f",
            "Spearman_rho": ":.3f",
            "Spearman_p_value": ":.4f",
            "N": True,
        },
    )

    # Same reference lines as original figure
    fig.add_hline(
        y=0,
        line_width=1,
    )

    fig.add_hline(
        y=0.2,
        line_dash="dash",
        line_width=1,
    )

    fig.add_hline(
        y=-0.2,
        line_dash="dash",
        line_width=1,
    )

    fig.update_layout(
        title=title,
        xaxis_title="Density",
        yaxis_title="Spearman ρ",
        legend_title="Metric",
        hovermode="closest",
        template="plotly_white",
        height=650,
    )

    return fig

def make_iq_scatter_figure(
    dataframe,
    metric,
    density,
    statistics=None,
):
    """
    Interactive IQ vs metric scatter plot.

    Reproduces Gabrielle's analysis by showing:

    - Control and Gifted subjects
    - pooled linear regression
    - Spearman rho
    - Spearman p-value
    - Mann-Whitney p-value
    """

    # ========================================================
    # Scatter
    # ========================================================

    fig = px.scatter(
        dataframe,
        x="IQ",
        y="Value",
        color="Group",

        labels={
            "IQ": "IQ",
            "Value": metric,
            "Group": "Group",
        },

        hover_data={
            "IQ": ":.2f",
            "Value": ":.3f",
            "Group": True,
        },
    )

    # ========================================================
    # Pooled OLS regression line
    # ========================================================

    valid = dataframe[
        dataframe["IQ"].notna()
        & dataframe["Value"].notna()
    ].copy()

    if len(valid) > 1:

        x = valid[
            "IQ"
        ].astype(float).to_numpy()

        y = valid[
            "Value"
        ].astype(float).to_numpy()

        if np.unique(x).size > 1:

            slope, intercept = np.polyfit(
                x,
                y,
                1,
            )

            x_line = np.linspace(
                x.min(),
                x.max(),
                100,
            )

            y_line = (
                slope * x_line
                + intercept
            )

            fig.add_trace(
                go.Scatter(
                    x=x_line,
                    y=y_line,

                    mode="lines",

                    name="OLS regression",

                    line=dict(
                        width=2,
                    ),
                )
            )

    # ========================================================
    # Statistical annotations
    # ========================================================

    if statistics is not None:

        rho = statistics.get(
            "rho",
            np.nan,
        )

        spearman_p = statistics.get(
            "spearman_p",
            np.nan,
        )

        mannwhitney_p = statistics.get(
            "mannwhitney_p",
            np.nan,
        )

        n = statistics.get(
            "n",
            None,
        )

        stat_lines = []

        if np.isfinite(rho):

            stat_lines.append(
                f"ρ = {rho:.2f}"
            )

        if np.isfinite(spearman_p):

            stat_lines.append(
                f"P<sub>Spearman</sub> = "
                f"{spearman_p:.3g}"
            )

        if np.isfinite(mannwhitney_p):

            stat_lines.append(
                f"P<sub>MW</sub> = "
                f"{mannwhitney_p:.3g}"
            )

        if n is not None:

            stat_lines.append(
                f"N = {n}"
            )

        fig.add_annotation(

            x=0.03,
            y=0.97,

            xref="paper",
            yref="paper",

            text="<br>".join(
                stat_lines
            ),

            showarrow=False,

            align="left",

            xanchor="left",
            yanchor="top",

            bgcolor="rgba(255,255,255,0.85)",

            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1,
            borderpad=6,
        )

    # ========================================================
    # Layout
    # ========================================================

    fig.update_layout(

        title=(
            f"IQ vs {metric}"
            "<br>"
            f"Density = {density:.2f}"
        ),

        xaxis_title="IQ",

        yaxis_title=metric,

        template="plotly_white",

        height=500,

        legend_title="Group",
    )

    return fig

def make_group_density_figure(
    summary_df,
    metric,
):
    """
    Mean global metric across densities for each group.
    """

    fig = px.line(
        summary_df,
        x="Density",
        y="Mean",
        color="Group",
        markers=True,
        error_y="SEM",
    )

    fig.update_layout(
        title=f"{metric} across densities",
        xaxis_title="Density",
        yaxis_title=metric,
        template="plotly_white",
        height=500,
    )

    return fig

def make_global_sed_figure(
    dataframe,
    method,
):
    """
    Plot Global SED of all nodal features
    across connection densities.
    """

    fig = px.line(
        dataframe,
        x="Density",
        y="Global_SED",
        color="Feature",
        markers=True,

        hover_data={
            "Density": ":.2f",
            "Global_SED": ":.3f",
            "Feature": True,
        },
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_width=1,
    )

    fig.update_layout(

        title=(
            "Global SED of nodal features "
            "at various connection densities "
            f"for {method}"
        ),

        xaxis_title="Density",

        yaxis_title="Global SED",

        legend_title="Nodal feature",

        template="plotly_white",

        hovermode="closest",

        height=650,
    )

    return fig