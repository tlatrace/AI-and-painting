import csv
import time
from pathlib import Path
from loguru import logger


def save_list_to_csv(list_to_export: list, output_path: Path) -> None:
    assert (
        str(output_path)[-4:] == ".csv"
    ), f"Specified output path {output_path} is not in format .csv"
    with open(str(output_path), "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(list_to_export)


def save_dict_to_csv(dict_to_export: dict, output_path: Path) -> None:
    assert (
        str(output_path)[-4:] == ".csv"
    ), f"Specified output path {output_path} is not in format .csv"
    with open(str(output_path), "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for key, value in dict_to_export.items():
            writer.writerow([key, value])


def load_saved_list(input_path: Path) -> list:
    saved_list = list()
    with open(str(input_path), "r") as f:
        data = csv.reader(f)
        for row in data:
            saved_list += row
    return saved_list


def load_saved_dict(input_path: Path) -> dict:
    saved_dict = dict()
    with open(str(input_path), "r") as f:
        data = csv.reader(f)
        for row in data:
            saved_dict[row[0]] = row[1]
    return saved_dict


def timeit(method):
    """Decorator to time the execution of a function."""

    def timed(*args, **kw):
        start_time = time.time()
        logger.info(f"\nStarting execution of {method.__name__}.")
        result = method(*args, **kw)
        end_time = time.time()
        n_seconds = int(end_time - start_time)
        if n_seconds < 60:
            logger.info(f"\n{method.__name__} : {n_seconds}s to execute")
        elif 60 < n_seconds < 3600:
            logger.info(
                f"\n{method.__name__} : {n_seconds // 60}min {n_seconds % 60}s to execute"
            )
        else:
            logger.info(
                f"\n{method.__name__} : {n_seconds // 3600}h {n_seconds % 3600 // 60}min {n_seconds // 3600 % 60}s to execute"
            )
        return result

    return timed


def get_formatted_time():
    return time.strftime("%Y_%m_%d__%H_%M_%S", time.localtime())
