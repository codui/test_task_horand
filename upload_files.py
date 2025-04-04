import os
import time

# Importing Selenium WebDriver to interact with the browser
from selenium import webdriver

# Service class introduced in Selenium 4 for managing driver installation, opening, and closing
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Used for setting wait times
from selenium.webdriver.support.ui import WebDriverWait

# ChromeDriverManager is used to install the driver without manually downloading the binary file
from webdriver_manager.chrome import ChromeDriverManager


def initialize_web_driver():
    """
    Initializes the Selenium WebDriver for Chrome and opens the target website.

    Returns:
        webdriver.Chrome: An instance of the Chrome WebDriver.
    """
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get("http://localhost:3000/")
    driver.implicitly_wait(3)  # Implicit wait for all elements
    return driver


def get_absolute_path_to_folder(folder_name: str = "img") -> str:
    """
    Constructs the absolute path to a specified folder relative to the current script.

    Args:
        folder_name (str): The name of the folder. Defaults to "img".

    Returns:
        str: The absolute path to the specified folder.
    """
    current_script_path: str = f"{os.path.dirname(os.path.abspath(__file__))}\\{folder_name}"
    return current_script_path


def organize_files_by_folder_prefix(
    folder_names: list[str], root_folder_path: str
) -> dict[str, list[str]]:
    """
    Groups image files by the first letter of their folder names.

    Args:
        folder_names (list[str]): List of folder names containing images.
        root_folder_path (str): Absolute path to the root folder containing the image folders.

    Returns:
        dict[str, list[str]]: A dictionary where keys are folder name prefixes (letters),
                                and values are lists of absolute paths to image files.
    """
    grouped_files: dict = {}

    for folder_name in folder_names:
        folder_path = f"{root_folder_path}\\{folder_name}"
        folder_prefix = folder_name[0].upper()

        if len(os.listdir(folder_path)) > 0:
            for file_name in os.listdir(folder_path):
                file_path = f"{folder_path}\\{file_name}"
                if os.path.isfile(file_path):
                    if grouped_files.get(folder_prefix) is None:
                        grouped_files[folder_prefix] = []
                    grouped_files[folder_prefix].append(file_path)

    return grouped_files


def upload_files_to_server(grouped_files: dict[str, list[str]]):
    """
    Iterates through grouped files and uploads them to the server using a web form.

    Args:
        grouped_files (dict[str, list[str]]): A dictionary where keys are folder prefixes (letters),
                                                and values are lists of absolute paths to image files.
    """
    driver = initialize_web_driver()

    for folder_prefix, file_paths in grouped_files.items():
        file_input_element = driver.find_element(
            By.CSS_SELECTOR, f".uploadForm[data-form-type={folder_prefix}] input"
        )
        upload_button_element = driver.find_element(
            By.CSS_SELECTOR, f".uploadForm[data-form-type={folder_prefix}] button"
        )

        for file_path in file_paths:
            file_input_element.send_keys(file_path)
            time.sleep(0.05)
            upload_button_element.click()
            time.sleep(0.05)

    driver.close()
