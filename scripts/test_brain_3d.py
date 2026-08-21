from pathlib import Path
import sys

import pandas as pd
import plotly.io as pio

pio.renderers.default = "browser"


BASE_DIR = Path(
    __file__
).resolve().parent.parent

sys.path.insert(
    0,
    str(BASE_DIR),
)


from figures.brain_3d import (
    make_brain_3d_figure,
)


CSV_PATH = (
    BASE_DIR
    / "data"
    / "nodal_feature_values_all_densities_MSN_500.aparc.csv"
)


df = pd.read_csv(
    CSV_PATH
)


selected = df[
    (df["Feature"] == "Clustering Coefficient")
    & (df["Density"].round(2) == 0.15)
].copy()


print(
    "Selected regions:",
    len(selected),
)


fig = make_brain_3d_figure(

    dataframe=selected,

    title=(
        "Clustering Coefficient — MSN"
        "<br>"
        "Gifted − Controls | Density = 0.15"
    ),
)


fig.show()