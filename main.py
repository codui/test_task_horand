"""
In the EasyOCR library, coordinates represent an array of four points
defining a rectangular area where text was detected.

    These points follow the standard coordinate system in computer graphics, where:
    X — horizontal coordinate (left to right).
    Y — vertical coordinate (top to bottom).

! To extract only text:
text = reader.readtext(path_to_image, detail=0)
! To extract full details:
text_coord = reader.readtext(path_to_image, detail=1)
"""

import os
import shutil
import subprocess
from pathlib import Path

import cv2
import easyocr

import start_server
import upload_files


def calculate_image_crop_coordinates(
    image_path: str,
    table_text_height: int = 1398,
    table_header_height: int = 453,
    x_left: int = 0,
    x_right: int = 580,
) -> list[int]:
    """
    Calculates the coordinates of the region in the image to process for text recognition.

    Args:
        image_path (str): Path to the image file.
        table_text_height (int): Height of the table text area. Defaults to 1398.
        table_header_height (int): Height of the table header area. Defaults to 453.
        x_left (int): Left X-coordinate. Defaults to 0.
        x_right (int): Right X-coordinate. Defaults to 580.

    Returns:
        list[int]: A list of coordinates [y_top, y_bottom, x_left, x_right].
    """
    image = cv2.imread(image_path)
    image_height: int = image.shape[0]
    y_top: int = image_height - table_text_height
    y_bottom: int = y_top + table_header_height
    return [y_top, y_bottom, x_left, x_right]


def extract_folder_name_from_image_text(
    recognized_text: list[str], image_path: str
) -> str:
    """
    Extracts the folder name from the recognized text in the image.

    Args:
        recognized_text (list[str]): List of strings obtained from text recognition.
        image_path (str): Path to the image file.

    Returns:
        str: The folder name extracted from the recognized text.
    """
    for word in recognized_text:
        word_parts_count = len(word.split())
        if word_parts_count == 2 or word_parts_count == 3:
            folder_name_candidate = word
            break
    folder_name: str = " ".join(folder_name_candidate.split()[:2])
    return folder_name


def move_image_to_folder(source_folder: str, target_folder_name: str, image_path: str):
    """
    Moves an image file from the source folder to a target folder based on the recognized text.

    Args:
        source_folder (str): Absolute path to the source folder containing the image.
        target_folder_name (str): Name of the target folder to move the image to.
        image_path (str): Absolute path to the image file.
    """
    target_folder_path = f"{source_folder}\\{target_folder_name}"
    if not os.path.exists(target_folder_path):
        os.mkdir(target_folder_path)
    shutil.move(image_path, target_folder_path)


def preprocess_image_for_text_recognition(image_path: str):
    """
    Prepares an image for text recognition by cropping, converting to grayscale, and binarizing.

    Args:
        image_path (str): Path to the image file.

    Returns:
        numpy.ndarray: The processed binary image.
    """
    image = cv2.imread(image_path)
    y_top, y_bottom, x_left, x_right = calculate_image_crop_coordinates(image_path)
    cropped_image = image[y_top:y_bottom, x_left:x_right]
    grayscale_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    binary_image = cv2.inRange(grayscale_image, 200, 255)
    return binary_image


def process_images_and_move_to_folders(source_folder: str = ""):
    """
    Processes images in the source folder, recognizes text, and moves them to corresponding folders.

    Args:
        source_folder (str): Path to the folder containing the images.
    """
    source_folder_path: Path = Path(source_folder)
    files_and_folders = (item for item in source_folder_path.iterdir())

    for item in files_and_folders:
        if os.path.isfile(item):
            image_path: str = str(item)
            processed_image = preprocess_image_for_text_recognition(image_path)
            recognized_text: list[str] = reader.readtext(
                processed_image,
                detail=0,
                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ",
                rotation_info=[0],
            )
            folder_name = extract_folder_name_from_image_text(
                recognized_text, image_path
            )
            move_image_to_folder(source_folder, folder_name, image_path)


if __name__ == "__main__":
    # Run local server for site
    start_server.run()

    # Initialize the EasyOCR reader
    reader = easyocr.Reader(["en"])

    # Process images and move them to folders
    root_folder_path = upload_files.get_absolute_path_to_folder(folder_name="img")
    process_images_and_move_to_folders(root_folder_path)

    # Debugging and verification
    absolute_root_folder_path = upload_files.get_absolute_path_to_folder()
    # print(f"{absolute_root_folder_path=}")

    folder_names: list = os.listdir(absolute_root_folder_path)
    # print(f"{folder_names=}")

    files_grouped_by_folder: dict = upload_files.organize_files_by_folder_prefix(
        folder_names, absolute_root_folder_path
    )
    # print(f"{files_grouped_by_folder=}")

    upload_files.upload_files_to_server(files_grouped_by_folder)
