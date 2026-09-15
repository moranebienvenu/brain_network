import plotly.express as px


def make_top_regions_figure(
    dataframe,
    feature,
    density,
    parcellation,
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
            f"Density = {density:.2f} - "
            f"{parcellation} parcellation"
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
    parcellation,
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
            f"{feature} - "
            f"{parcellation} parcellation"
        ),
        xaxis_title="Density",
        yaxis_title="Gifted − Controls",
        template="plotly_white",
        height=500,
    )

    return fig


def make_method_comparison_figure(
    dataframe,
    feature,
    parcellation,
):
    """
    Compare the Global SED of one nodal metric across densities
    for all network construction methods.
    """

    df = dataframe[
        dataframe["Feature"] == feature
    ].copy()

    fig = px.line(
        df,
        x="Density",
        y="Global_SED",
        color="Method",
        markers=True,

        hover_data={
            "Density": ":.2f",
            "Global_SED": ":.3f",
            "Method": True,
        },
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_width=1,
    )

    fig.update_layout(

        title=(
            f"{feature} — comparison across methods"
            "<br>"
            f"{parcellation} parcellation"
        ),

        xaxis_title="Density",

        yaxis_title="Global SED",

        legend_title="Method",

        template="plotly_white",

        hovermode="closest",

        height=600,
    )

    return fig

def make_regional_heatmap_figure(
    dataframe,
    regions_to_plot,
    feature,
    method,
    parcellation,
    show_values=True,
):
    """
    Heatmap showing the top Gifted and Control
    regions across connection densities.
    """

    heatmap_data = dataframe.pivot(
        index="Region",
        columns="Density",
        values="Diff_gifted_minus_controls",
    )

    heatmap_data = heatmap_data.loc[
        regions_to_plot
    ]

    fig = px.imshow(
        heatmap_data,

        color_continuous_scale="RdBu_r",

        color_continuous_midpoint=0,

        text_auto=(
            ".2f"
            if show_values
            else False
        ),

        labels={
            "x": "Density",
            "y": "Region",
            "color": "Gifted − Controls",
        },

        aspect="auto",
    )

    fig.add_hline(
        y=14.5,
        line_width=2,
    )

    fig.update_layout(

        title=(
            f"{feature}: top Gifted and Control regions "
            f"across densities"
            "<br>"
            f"{method} — {parcellation} parcellation"
        ),

        template="plotly_white",

        height=900,
    )

    return fig