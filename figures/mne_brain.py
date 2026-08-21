# import os
# import re
# import base64
# import tempfile
# from io import BytesIO

# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.cm as mcm

# from matplotlib.colors import Normalize

# import mne


# # ============================================================
# # Configuration
# # ============================================================

# ATLAS_PARC = {
#     "aparc": "aparc",
#     "500.aparc": "500.aparc",
# }

# _SUBJECTS_DIR = None
# _LABELS_CACHE = {}


# # ============================================================
# # FreeSurfer / MNE utilities
# # ============================================================

# def get_subjects_dir():
#     """
#     Download/load fsaverage and return subjects_dir.
#     """

#     global _SUBJECTS_DIR

#     if _SUBJECTS_DIR is None:

#         mne_data_dir = os.path.abspath("./mne_data")

#         os.makedirs(
#             mne_data_dir,
#             exist_ok=True,
#         )

#         fs_dir = mne.datasets.fetch_fsaverage(
#             subjects_dir=mne_data_dir,
#             verbose=False,
#         )

#         _SUBJECTS_DIR = os.path.dirname(fs_dir)

#     return _SUBJECTS_DIR


# def get_labels(atlas):
#     """
#     Load FreeSurfer cortical labels for the selected atlas.
#     """

#     if atlas in _LABELS_CACHE:
#         return _LABELS_CACHE[atlas]

#     subjects_dir = get_subjects_dir()

#     labels = mne.read_labels_from_annot(
#         "fsaverage",
#         parc=ATLAS_PARC[atlas],
#         subjects_dir=subjects_dir,
#         verbose=False,
#     )

#     labels = [
#         label
#         for label in labels
#         if label.name.lower().split("-")[0]
#         not in (
#             "unknown",
#             "???",
#             "medial_wall",
#         )
#     ]

#     _LABELS_CACHE[atlas] = labels

#     return labels


# # ============================================================
# # Region naming
# # ============================================================

# def normalize_region_name(name):
#     """
#     Normalize region names so CSV regions can be matched to
#     FreeSurfer/MNE labels.
#     """

#     s = str(name).strip().lower()

#     hemi = None

#     changed = True

#     while changed:

#         changed = False

#         for suffix in (
#             "-lh",
#             "_lh",
#             "-rh",
#             "_rh",
#         ):

#             if s.endswith(suffix):

#                 if hemi is None:
#                     hemi = (
#                         "lh"
#                         if "l" in suffix
#                         else "rh"
#                     )

#                 s = s[:-len(suffix)]

#                 changed = True

#                 break

#     changed = True

#     while changed:

#         changed = False

#         for prefix, hemisphere in (
#             ("lh_", "lh"),
#             ("lh-", "lh"),
#             ("rh_", "rh"),
#             ("rh-", "rh"),
#             ("l_", "lh"),
#             ("r_", "rh"),
#         ):

#             if s.startswith(prefix):

#                 if hemi is None:
#                     hemi = hemisphere

#                 s = s[len(prefix):]

#                 changed = True

#                 break

#     s = s.replace(
#         "_roi",
#         "",
#     )

#     core = re.sub(
#         r"[^a-z0-9]",
#         "",
#         s,
#     )

#     return hemi, core


# def build_label_lookup(labels):
#     """
#     Build:
#         (hemisphere, normalized region name) -> MNE Label
#     """

#     lookup = {}

#     for label in labels:

#         hemi, core = normalize_region_name(
#             label.name
#         )

#         if hemi is None:
#             hemi = label.hemi

#         lookup[(hemi, core)] = label

#     return lookup


# ============================================================
# Brain rendering
# ============================================================

# this function take too much time to update on real time 
#  def make_mne_brain_image(
#     dataframe,
#     atlas="500.aparc",
#     value_column="Diff_gifted_minus_controls",
#     cmap="coolwarm",
#     color_range=(-1.0, 1.0),
#     title="",
# ):
#     """
#     Create an MNE cortical visualization and return it as a
#     base64 image URI suitable for Dash html.Img.

#     Parameters
#     ----------
#     dataframe : pandas.DataFrame
#         Must contain Region and the selected value column.

#     Returns
#     -------
#     str
#         data:image/png;base64,...
#     """

#     labels = get_labels(atlas)

#     lookup = build_label_lookup(labels)

#     subjects_dir = get_subjects_dir()

#     cmap_object = plt.get_cmap(cmap)

#     norm = Normalize(
#         vmin=color_range[0],
#         vmax=color_range[1],
#     )

#     region_values = dict(
#         zip(
#             dataframe["Region"],
#             dataframe[value_column],
#         )
#     )

#     # Off-screen rendering
#     try:
#         import pyvista

#         pyvista.OFF_SCREEN = True

#     except Exception:
#         pass

#     temp_fd, temp_path = tempfile.mkstemp(
#         suffix=".png"
#     )

#     os.close(temp_fd)

#     try:

#         brain = mne.viz.Brain(
#             "fsaverage",
#             hemi="split",
#             surf="inflated",
#             subjects_dir=subjects_dir,
#             background="white",
#             cortex="low_contrast",
#             size=(1200, 900),
#             views=[
#                 "lateral",
#                 "medial",
#             ],
#             view_layout="horizontal",
#         )

#         matched_regions = 0

#         for region, value in region_values.items():

#             label = lookup.get(
#                 normalize_region_name(region)
#             )

#             if label is None:
#                 continue

#             if np.isnan(value):
#                 value = 0.0

#             brain.add_label(
#                 label,
#                 color=cmap_object(
#                     norm(value)
#                 )[:3],
#                 borders=False,
#             )

#             matched_regions += 1

#         brain.save_image(
#             temp_path
#         )

#         brain.close()

#         image = plt.imread(
#             temp_path
#         )

#         height, width = image.shape[:2]

#         figure_width = 11

#         fig, ax = plt.subplots(
#             figsize=(
#                 figure_width,
#                 figure_width
#                 * height
#                 / width,
#             )
#         )

#         ax.imshow(image)

#         ax.axis("off")

#         ax.set_title(
#             title,
#             fontsize=15,
#             fontweight="bold",
#         )

#         scalar_map = mcm.ScalarMappable(
#             cmap=cmap_object,
#             norm=norm,
#         )

#         scalar_map.set_array([])

#         fig.colorbar(
#             scalar_map,
#             ax=ax,
#             shrink=0.70,
#             pad=0.02,
#             label="Gifted - Controls",
#         )

#         buffer = BytesIO()

#         fig.savefig(
#             buffer,
#             format="png",
#             dpi=180,
#             bbox_inches="tight",
#         )

#         plt.close(fig)

#         buffer.seek(0)

#         encoded = base64.b64encode(
#             buffer.read()
#         ).decode("utf-8")

#         return (
#             "data:image/png;base64,"
#             + encoded
#         )

#     finally:

#         if os.path.exists(temp_path):
#             os.remove(temp_path)