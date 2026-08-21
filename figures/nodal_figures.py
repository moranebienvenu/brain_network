import plotly.express as px


def make_top_regions_figure(
    dataframe,
    feature,
    density,
):
    """
    Horizontal bar chart showing the largest regional
    Gifted-Control differences.
    """

    df = dataframe.copy()

    df = df.sort_values(
        "Diff_gifted_minus_controls"
    )

    fig = px.bar(
        df,
        x="Diff_gifted_minus_controls",
        y="Region",
        orientation="h",
        color="Diff_gifted_minus_controls",
        color_continuous_scale="RdBu_r",
        range_color=[-1, 1],
        hover_data={
            "Control_normalized": ":.3f",
            "Gifted_normalized": ":.3f",
            "Diff_gifted_minus_controls": ":.3f",
        },
    )

    fig.update_layout(
        title=(
            f"Regional differences — {feature}<br>"
            f"Density = {density:.2f}"
        ),
        xaxis_title="Gifted − Controls",
        yaxis_title="Region",
        template="plotly_white",
        height=600,
        coloraxis_colorbar={
            "title": "Gifted − Controls"
        },
    )

    return fig


def make_region_density_figure(
    dataframe,
    region,
    feature,
):
    """
    Plot regional Gifted-Control difference across densities.
    """

    fig = px.line(
        dataframe,
        x="Density",
        y="Diff_gifted_minus_controls",
        markers=True,
        hover_data={
            "Control_normalized": ":.3f",
            "Gifted_normalized": ":.3f",
            "Diff_gifted_minus_controls": ":.3f",
        },
    )

    fig.add_hline(
        y=0,
        line_width=1,
    )

    fig.update_layout(
        title=(
            f"{region}<br>"
            f"{feature}"
        ),
        xaxis_title="Density",
        yaxis_title="Gifted − Controls",
        template="plotly_white",
        height=500,
    )

    return fig