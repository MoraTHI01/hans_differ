"""
Convert images
"""

import argparse
import os
from PIL import Image


def scale_images(input_dir, file, img, target_width, target_height):
    """
    Scale image
    """
    # Get orig image size
    width, height = img.size
    # Resize the image using Lanczos
    resized_img = img.resize((target_width, target_height), Image.LANCZOS)
    # generate output file name
    output_file = file.replace("-w" + str(int(width)) + "-", "-w" + str(int(target_width)) + "-")
    output_file = output_file.replace("-h" + str(int(height)) + "-", "-h" + str(int(target_height)) + "-")

    # Save the resized image
    resized_img.save(os.path.join(input_dir, output_file))


def process_images(input_dir):
    """
    Process input folder images
    """
    # List all files in the input directory
    files = os.listdir(input_dir)
    files = [f for f in files if os.path.isfile(input_dir + "/" + f)]
    # resolutions [width, height] items
    resolutions = [[114, 64], [160, 90], [228, 128]]
    for file in files:
        # Open the image file
        if file.endswith(".png"):
            print(file)
            with Image.open(os.path.join(input_dir, file)) as img:
                for resolution in resolutions:
                    scale_images(
                        input_dir=input_dir, file=file, img=img, target_width=resolution[0], target_height=resolution[1]
                    )


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
    process_images(args.input_folder)


if __name__ == "__main__":
    main()
