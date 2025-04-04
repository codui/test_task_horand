import os
import subprocess


def run() -> None:
    """
    Функция запускает локальный сервер из cmd.exe
    """
    # Получить путь к текущей папке скрипта в формте Windows
    current_dir: str = os.path.dirname(os.path.abspath(__file__))
    # Вариант 1: Раздельные аргументы (рекомендуется)
    subprocess.Popen(
        ["cmd.exe", "/k", "cd", "/d", current_dir, "&&", "node", "server.js"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
