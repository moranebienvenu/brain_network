from pathlib import Path
import re

import pandas as pd
from nibabel.freesurfer.io import read_annot


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ANNOT_DIR = BASE_DIR / "brain_data" / "annotations"

CSV_PATH = (
    BASE_DIR
    / "data"
    / "nodal_feature_values_all_densities_MSN_500.aparc.csv"
)

LH_ANNOT = ANNOT_DIR / "lh.500.aparc.annot"
RH_ANNOT = ANNOT_DIR / "rh.500.aparc.annot"


# ============================================================
# REGION NAME NORMALIZATION
# ============================================================

def normalize_csv_region(name):
    """
    Normalize region names from Gabrielle's CSV.

    Returns:
        (hemisphere, core_name)
    """

    s = str(name).strip().lower()
    hemi = None

    # Remove hemisphere markers at the end
    changed = True

    while changed:

        changed = False

        for suffix in (
            "-lh",
            "_lh",
            "-rh",
            "_rh",
        ):
            if s.endswith(suffix):

                if hemi is None:
                    hemi = (
                        "lh"
                        if "l" in suffix
                        else "rh"
                    )

                s = s[:-len(suffix)]
                changed = True
                break

    # Remove hemisphere markers at the beginning
    changed = True

    while changed:

        changed = False

        for prefix, hemisphere in (
            ("lh_", "lh"),
            ("lh-", "lh"),
            ("rh_", "rh"),
            ("rh-", "rh"),
            ("l_", "lh"),
            ("r_", "rh"),
        ):
            if s.startswith(prefix):

                if hemi is None:
                    hemi = hemisphere

                s = s[len(prefix):]
                changed = True
                break

    s = s.replace("_roi", "")

    core = re.sub(
        r"[^a-z0-9]",
        "",
        s,
    )

    return hemi, core


def normalize_annot_region(name, hemisphere):
    """
    Normalize a region name coming from a FreeSurfer
    annotation file.
    """

    if isinstance(name, bytes):
        name = name.decode("utf-8")

    s = str(name).strip().lower()

    # Remove possible hemisphere prefix
    for prefix in (
        "lh_",
        "lh-",
        "rh_",
        "rh-",
    ):
        if s.startswith(prefix):
            s = s[len(prefix):]

    s = s.replace("_roi", "")

    core = re.sub(
        r"[^a-z0-9]",
        "",
        s,
    )

    return hemisphere, core


# ============================================================
# LOAD CSV REGIONS
# ============================================================

print("\n========================================")
print("CSV REGIONS")
print("========================================")

df = pd.read_csv(CSV_PATH)

if "Region" not in df.columns:
    raise ValueError(
        "The CSV does not contain a 'Region' column."
    )

csv_region_names = sorted(
    df["Region"]
    .dropna()
    .astype(str)
    .unique()
)

csv_regions = {
    normalize_csv_region(region)
    for region in csv_region_names
}

print(
    f"Unique region names in CSV: "
    f"{len(csv_region_names)}"
)

print(
    f"Unique normalized CSV regions: "
    f"{len(csv_regions)}"
)


# ============================================================
# LOAD ANNOTATION REGIONS
# ============================================================

print("\n========================================")
print("ANNOTATION REGIONS")
print("========================================")


def load_annot_regions(path, hemisphere):

    labels, color_table, names = read_annot(
        str(path)
    )

    regions = set()

    original_names = []

    for name in names:

        decoded = (
            name.decode("utf-8")
            if isinstance(name, bytes)
            else str(name)
        )

        original_names.append(decoded)

        # Ignore standard FreeSurfer unknown regions
        if decoded.lower() in (
            "unknown",
            "???",
            "medial_wall",
        ):
            continue

        regions.add(
            normalize_annot_region(
                decoded,
                hemisphere,
            )
        )

    return regions, original_names


lh_regions, lh_names = load_annot_regions(
    LH_ANNOT,
    "lh",
)

rh_regions, rh_names = load_annot_regions(
    RH_ANNOT,
    "rh",
)

annot_regions = lh_regions | rh_regions


print(
    f"Left hemisphere regions: "
    f"{len(lh_regions)}"
)

print(
    f"Right hemisphere regions: "
    f"{len(rh_regions)}"
)

print(
    f"Total annotation regions: "
    f"{len(annot_regions)}"
)


# ============================================================
# COMPARE
# ============================================================

matched = csv_regions & annot_regions

missing_from_annot = (
    csv_regions - annot_regions
)

missing_from_csv = (
    annot_regions - csv_regions
)


print("\n========================================")
print("COMPARISON")
print("========================================")

print(
    f"Matched regions: "
    f"{len(matched)}"
)

print(
    f"CSV regions not found in annotations: "
    f"{len(missing_from_annot)}"
)

print(
    f"Annotation regions not found in CSV: "
    f"{len(missing_from_csv)}"
)


# ============================================================
# SHOW MISMATCHES
# ============================================================

if missing_from_annot:

    print("\nCSV regions missing from annotation:")

    for region in sorted(missing_from_annot):
        print("  ", region)


if missing_from_csv:

    print("\nAnnotation regions missing from CSV:")

    for region in sorted(missing_from_csv):
        print("  ", region)


# ============================================================
# RESULT
# ============================================================

print("\n========================================")

if len(missing_from_annot) == 0:

    print(
        "SUCCESS: every CSV region was found "
        "in the FreeSurfer annotations."
    )

else:

    percentage = (
        100
        * len(matched)
        / len(csv_regions)
    )

    print(
        f"Match rate: {percentage:.1f}%"
    )

print("========================================\n")