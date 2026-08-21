from pathlib import Path
import json
import re

import numpy as np

from nibabel.freesurfer.io import (
    read_annot,
    read_geometry,
)


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ANNOT_DIR = (
    BASE_DIR
    / "brain_data"
    / "annotations"
)

OUTPUT_DIR = (
    BASE_DIR
    / "brain_data"
    / "prepared"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# 2. FSAVERAGE
# ============================================================
#
# We use the fsaverage directory that MNE previously downloaded.
#
# Expected:
#
# mne_data/
# └── fsaverage/
#     └── surf/
#         ├── lh.inflated
#         └── rh.inflated
#
# ============================================================

FSAVERAGE_DIR = (
    BASE_DIR
    / "mne_data"
    / "fsaverage"
)

SURF_DIR = (
    FSAVERAGE_DIR
    / "surf"
)


# ============================================================
# 3. INPUT FILES
# ============================================================

LH_SURFACE = SURF_DIR / "lh.pial" #inflated"
RH_SURFACE = SURF_DIR / "rh.pial" #inflated"

LH_ANNOT = (
    ANNOT_DIR
    / "lh.500.aparc.annot"
)

RH_ANNOT = (
    ANNOT_DIR
    / "rh.500.aparc.annot"
)


# ============================================================
# 4. OUTPUT FILES
# ============================================================

OUTPUT_MESH = (
    OUTPUT_DIR
    / "brain_mesh_500_aparc.npz"
)

OUTPUT_REGIONS = (
    OUTPUT_DIR
    / "brain_regions_500_aparc.json"
)


# ============================================================
# 5. REGION NAME NORMALIZATION
# ============================================================

def normalize_region_name(
    name,
    hemisphere,
):
    """
    Convert a FreeSurfer annotation region name into the same
    normalized naming convention used by the dashboard.

    Returns
    -------
    str
        Example:
        lh_bankssts_part1
    """

    if isinstance(name, bytes):
        name = name.decode("utf-8")

    name = str(name).strip()

    # Remove hemisphere prefix if already present
    name = re.sub(
        r"^(lh|rh)[_-]",
        "",
        name,
        flags=re.IGNORECASE,
    )

    return f"{hemisphere}_{name}"


# ============================================================
# 6. LOAD ONE HEMISPHERE
# ============================================================

def prepare_hemisphere(
    surface_path,
    annot_path,
    hemisphere,
):
    """
    Load FreeSurfer geometry and annotation.

    Returns
    -------
    vertices : ndarray
        Shape (n_vertices, 3)

    faces : ndarray
        Shape (n_faces, 3)

    vertex_region_index : ndarray
        For each vertex, index of corresponding cortical region.

    region_names : list[str]
        Names of cortical regions.
    """

    print()
    print("=" * 70)
    print(
        f"Preparing hemisphere: {hemisphere}"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Surface geometry
    # --------------------------------------------------------

    vertices, faces = read_geometry(
        str(surface_path)
    )

    print(
        f"Vertices: {vertices.shape}"
    )

    print(
        f"Faces: {faces.shape}"
    )

    # --------------------------------------------------------
    # Annotation
    # --------------------------------------------------------

    labels, color_table, names = read_annot(
        str(annot_path)
    )

    print(
        f"Annotation vertices: {labels.shape}"
    )

    print(
        f"Annotation labels: {len(names)}"
    )

    # Surface and annotation must refer to same vertices
    if len(labels) != len(vertices):

        raise ValueError(
            f"Surface/annotation mismatch for {hemisphere}: "
            f"{len(vertices)} surface vertices vs "
            f"{len(labels)} annotation vertices."
        )

    # --------------------------------------------------------
    # Build region list
    # --------------------------------------------------------

    decoded_names = []

    for name in names:

        if isinstance(name, bytes):
            name = name.decode("utf-8")

        decoded_names.append(
            str(name)
        )

    # Labels from read_annot() correspond to indexes into names
    region_names = []

    old_index_to_new_index = {}

    excluded_names = {
        "unknown",
        "unknownpart1",
        "corpuscallosum",
        "corpuscallosumpart1",
        "???",
        "medial_wall",
    }

    for old_index, name in enumerate(
        decoded_names
    ):

        normalized_lower = (
            name
            .lower()
            .replace("_", "")
            .replace("-", "")
        )

        if normalized_lower in excluded_names:

            continue

        new_name = normalize_region_name(
            name=name,
            hemisphere=hemisphere,
        )

        new_index = len(region_names)

        region_names.append(
            new_name
        )

        old_index_to_new_index[
            old_index
        ] = new_index

    # --------------------------------------------------------
    # Vertex -> region index
    # --------------------------------------------------------

    vertex_region_index = np.full(
        len(vertices),
        -1,
        dtype=np.int32,
    )

    for vertex_idx, old_label_idx in enumerate(
        labels
    ):

        if old_label_idx in old_index_to_new_index:

            vertex_region_index[
                vertex_idx
            ] = old_index_to_new_index[
                old_label_idx
            ]

    # --------------------------------------------------------
    # Diagnostics
    # --------------------------------------------------------

    valid_vertices = (
        vertex_region_index >= 0
    )

    print(
        f"Included cortical regions: "
        f"{len(region_names)}"
    )

    print(
        f"Mapped vertices: "
        f"{valid_vertices.sum()}"
    )

    print(
        f"Excluded vertices: "
        f"{(~valid_vertices).sum()}"
    )

    return (
        vertices.astype(np.float32),
        faces.astype(np.int32),
        vertex_region_index,
        region_names,
    )


# ============================================================
# 7. MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Check files
    # --------------------------------------------------------

    required_files = [
        LH_SURFACE,
        RH_SURFACE,
        LH_ANNOT,
        RH_ANNOT,
    ]

    for path in required_files:

        if not path.exists():

            raise FileNotFoundError(
                f"Missing file:\n{path}"
            )

    # --------------------------------------------------------
    # Left hemisphere
    # --------------------------------------------------------

    (
        lh_vertices,
        lh_faces,
        lh_vertex_region,
        lh_region_names,

    ) = prepare_hemisphere(

        surface_path=LH_SURFACE,
        annot_path=LH_ANNOT,
        hemisphere="lh",
    )

    # --------------------------------------------------------
    # Right hemisphere
    # --------------------------------------------------------

    (
        rh_vertices,
        rh_faces,
        rh_vertex_region,
        rh_region_names,

    ) = prepare_hemisphere(

        surface_path=RH_SURFACE,
        annot_path=RH_ANNOT,
        hemisphere="rh",
    )

    # --------------------------------------------------------
    # Save NumPy mesh data
    # --------------------------------------------------------

    np.savez_compressed(

        OUTPUT_MESH,

        lh_vertices=lh_vertices,
        lh_faces=lh_faces,
        lh_vertex_region=lh_vertex_region,

        rh_vertices=rh_vertices,
        rh_faces=rh_faces,
        rh_vertex_region=rh_vertex_region,
    )

    # --------------------------------------------------------
    # Save region names
    # --------------------------------------------------------

    region_metadata = {

        "lh": lh_region_names,
        "rh": rh_region_names,

        "all": (
            lh_region_names
            + rh_region_names
        ),
    }

    with open(
        OUTPUT_REGIONS,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            region_metadata,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PREPARATION COMPLETE")
    print("=" * 70)

    print(
        f"Left regions: "
        f"{len(lh_region_names)}"
    )

    print(
        f"Right regions: "
        f"{len(rh_region_names)}"
    )

    print(
        f"Total regions: "
        f"{len(lh_region_names) + len(rh_region_names)}"
    )

    print()

    print(
        f"Mesh saved to:\n"
        f"{OUTPUT_MESH}"
    )

    print()

    print(
        f"Region metadata saved to:\n"
        f"{OUTPUT_REGIONS}"
    )

    print("=" * 70)


# ============================================================
# 8. RUN
# ============================================================

if __name__ == "__main__":
    main()