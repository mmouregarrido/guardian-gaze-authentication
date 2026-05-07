# ==============================================================================
# Imports and configuration
# ==============================================================================

# Standard library
import os
import re
import warnings
import math
import ast

# Third-party
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import loadmat


# ------------------------------------------------------------------------------
# Global flags
# ------------------------------------------------------------------------------

# Ignore warnings globally (use with care in production)
warnings.filterwarnings("ignore")


# ------------------------------------------------------------------------------
# Matplotlib style
# ------------------------------------------------------------------------------
SMALL_SIZE = 16
MEDIUM_SIZE = 18
BIGGER_SIZE = 32

plt.style.use("seaborn-v0_8-whitegrid")
plt.rc("font", family="serif")
plt.rc("font", size=SMALL_SIZE)
plt.rc("axes", titlesize=MEDIUM_SIZE)
plt.rc("axes", labelsize=MEDIUM_SIZE)
plt.rc("xtick", labelsize=SMALL_SIZE)
plt.rc("ytick", labelsize=SMALL_SIZE)
plt.rc("legend", fontsize=MEDIUM_SIZE)
plt.rc("figure", titlesize=BIGGER_SIZE)
plt.rcParams["savefig.bbox"] = "tight"


# ------------------------------------------------------------------------------
# Paths and shared data
# ------------------------------------------------------------------------------
BASE_PATH = "./"
PATH_DATA = os.path.join(BASE_PATH, "data")
PATH_USERS = os.path.join(PATH_DATA, "users")
PATH_PLOT = os.path.join(PATH_DATA, "plot")

PASTEL_COLORS = [
    "#BAE1FF",  # pastel blue
    "#FFF5BA",  # pastel yellow
    "#E3BAFF",  # pastel purple
]

# Load segment metadata once and reuse it in helper functions
segment_description_csv_path = os.path.join(PATH_DATA, "30s_segment_description.csv")
segment_description_df = pd.read_csv(segment_description_csv_path, sep=",", encoding="latin-1")
segment_description_df.dropna(subset=["index"], inplace=True)
segment_description_df["index"] = (
    segment_description_df["index"].astype(float).astype(int).astype(str)
)


# ==============================================================================
# Data loading helpers
# ==============================================================================

def get_videos_info(user_folder_path: str) -> pd.DataFrame:
    """
    Read the user's 'videos' text file and merge it with segment metadata.
    """
    txt_files = [f for f in os.listdir(user_folder_path) if f.endswith(".txt")]
    videos_txt_files = [f for f in txt_files if "videos" in f.lower()]

    if not videos_txt_files:
        raise FileNotFoundError(f"No videos .txt file found in: {user_folder_path}")

    videos_txt_path = os.path.join(user_folder_path, videos_txt_files[0])
    with open(videos_txt_path, "r", encoding="latin-1") as file:
        video_names = [line.strip() for line in file.readlines() if line.strip()]

    df_video_numbers = pd.DataFrame({"video_number": video_names})
    df_video_numbers["video_number"] = (
        df_video_numbers["video_number"].astype(int).astype(str)
    )

    # Merge user video order with metadata table
    return pd.merge(
        df_video_numbers,
        segment_description_df,
        left_on="video_number",
        right_on="index",
        how="left",
    )


def load_dataset(folder_path: str, index: int = -1) -> dict[int, pd.DataFrame]:
    """
    Load all .mat files for one user and return a dictionary:
    {video_number_from_filename: dataframe}
    """
    mat_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".mat")])
    df_video_info = get_videos_info(folder_path)
    dict_files: dict[int, pd.DataFrame] = {}

    if not mat_files:
        return dict_files

    # If index == 0, process only the first file; otherwise process all files
    files_to_process = [mat_files[0]] if index == 0 else mat_files

    for i, filename in enumerate(files_to_process, start=1):
        print(f"\rSession {i}/{len(files_to_process)}", flush=True, end="\r")

        mat_file_path = os.path.join(folder_path, filename)
        mat_data = loadmat(mat_file_path)

        # MATLAB structure extraction
        gaze_data = mat_data["eyetrackRecord"][0][0]
        field_names = mat_data["eyetrackRecord"][0].dtype.names
        gaze_arrays = {name: gaze_data[name].flatten() for name in field_names}

        # Build a normalized DataFrame
        df = pd.DataFrame({
            "x": gaze_arrays["x"] if "x" in gaze_arrays else np.nan,
            "y": gaze_arrays["y"] if "y" in gaze_arrays else np.nan,
            "pupil_area": gaze_arrays["pa"] if "pa" in gaze_arrays else np.nan,
            "timestamp": gaze_arrays["t"] if "t" in gaze_arrays else np.nan,
            "missing": gaze_arrays["missing"] if "missing" in gaze_arrays else np.nan,
        })

        # Extract file number, e.g., "001.mat" -> 1
        match = re.search(r"(\d{3})\.mat$", filename)
        number = int(match.group(1)) if match else None
        if number is None:
            continue

        df["number"] = number

        # Link to metadata using the same logic as your original code
        row = df_video_info.iloc[number - 1]
        df["video_number"] = row["video_number"]
        df["genre_category"] = row["genre category"]

        dict_files[number] = df

    return dict_files


def load_all_users_data(users_data_path: str) -> dict[str, pd.DataFrame]:
    """
    Load all users from a root folder and return:
    {username: concatenated_user_dataframe}
    """
    all_users_data: dict[str, pd.DataFrame] = {}
    user_names = sorted(
        [n for n in os.listdir(users_data_path) if os.path.isdir(os.path.join(users_data_path, n))]
    )

    for i, user_name in enumerate(user_names, start=1):
        print(f"Processing user {user_name} ({i}/{len(user_names)})")
        user_folder = os.path.join(users_data_path, user_name)
        user_data = load_dataset(user_folder)

        if not user_data:
            continue

        user_df = pd.concat(user_data.values(), ignore_index=True)
        user_df["user"] = user_name
        all_users_data[user_name] = user_df

    return all_users_data


def get_all_users_df(all_users_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Concatenate all per-user DataFrames into one DataFrame.
    """
    return pd.concat(all_users_data.values(), ignore_index=True)
