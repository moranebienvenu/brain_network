from pathlib import Path


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# ============================================================
# Available methods / parcellations
# ============================================================

METHODS = ["maxSW", "MIND", "MSN"]

PARCELLATIONS = ["500.aparc"]


# ============================================================
# IQ values
#
# These values come directly from Gabrielle's analysis script.
# Their order corresponds to:
# Subject Control_1 ... Subject Control_14
# Subject Gifted_1 ... Subject Gifted_15
# ============================================================

IQ_CONTROL = [
    118,
    130,
    124,
    124,
    118,
    130,
    119,
    120,
    120,
    125,
    124,
    123,
    127,
    116,
]

IQ_GIFTED = [
    149,
    147,
    152,
    149,
    149,
    152,
    146,
    142,
    152,
    152,
    152,
    146,
    147,
    148,
    149,
]


# ============================================================
# Global metrics
# ============================================================

GLOBAL_METRICS = [
    "Assortativity",
    "Transitivity",
    "Global Efficiency",
    "Characteristic Path Length",
    "Mean Participation Coefficient",
    "Mean Clustering Coefficient",
    "Mean Versatility",
]


HEMISPHERIC_METRICS = [
    "SLL",
    "SRR",
    "SLR",
    "Rlr",
    "Rii",
]


# ============================================================
# Nodal metrics
# ============================================================

NODAL_METRICS = [
    "Participation Coefficient",
    "Node Versatility",
    "Node Strength",
    "Local Efficiency",
    "Clustering Coefficient",
    "Betweenness Centrality",
    "Eigenvector Centrality",
    "Node Degree",
]