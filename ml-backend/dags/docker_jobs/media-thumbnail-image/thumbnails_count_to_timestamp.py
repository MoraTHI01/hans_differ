"""
Convert thumbnail count to timestamps
"""

import argparse
import os


def seconds_to_hh_mm_ss(seconds):
    """
    Convert seconds to HH:MM:SS format
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}#{minutes:02d}#{seconds:02d}"


def rename_files(folder_path):
    """
    Rename ffmpeg thumbnail files to timestamp files
    """
    # Iterate through files in the directory
    for filename in os.listdir(folder_path):
        # Construct the full file path
        file_path = os.path.join(folder_path, filename)
        # Check if the current item is a file
        if os.path.isfile(file_path) and file_path.endswith(".png"):
            # Perform actions with the file
            print("File path:", file_path)
            file_arr = file_path.rsplit("-", 1)
            counter = file_arr[-1].replace(".png", "")
            duration_s = (int(counter) - 1) * 10
            print(f"duration_s: {duration_s}")
            if duration_s == 0:
                new_name = file_arr[0] + "-00#00#00.png"
            else:
                new_name = file_arr[0] + "-" + seconds_to_hh_mm_ss(duration_s) + ".png"
            print(f"new_name: {new_name}")
            os.rename(file_path, new_name)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-folder", type=str, help="Input folder")
    return parser.parse_args()


def main():
    """
    Convert counted thumbnails to timestamp
    """
    args = parse_args()
    rename_files(args.input_folder)


if __name__ == "__main__":
    main()
