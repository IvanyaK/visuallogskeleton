from typing import Any, Dict

from chardet import detect
from pandas import DataFrame, read_csv

from pm4py import (
    discover_log_skeleton,
    format_dataframe,
    read_xes,
)

from pm4py.analysis import insert_artificial_start_end

from visualize import visualize_model


def getting_log(file_path: str) -> DataFrame:

    if file_path.lower().endswith(".xes"):
        log_df = read_xes(file_path)

    elif file_path.lower().endswith(".csv"):
        with open(file_path, "rb") as f:
            result = detect(f.read())

        log_df = read_csv(file_path, encoding=result["encoding"])

        case_id = input("Your case_id column: ")
        activity_key = input("Your activity_key column: ")
        timestamp_key = input("Your timestamp column: ")

        log_df = format_dataframe(
            log_df,
            case_id=case_id,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            timest_format="%Y-%m-%d %H:%M:%S",
        )
    else:
        raise ValueError("Supported extensions: .xes or .csv")

    log_df = insert_artificial_start_end(log_df)

    return log_df


def build_log_skeleton(log: DataFrame, noise: float = 0.9) -> Dict[str, Any]:
    return discover_log_skeleton(log, noise_threshold=noise)


def main() -> None:
    path = input('Enter path to .xes / .csv file: ').strip('"')
    log = getting_log(path)

    log_skeleton = build_log_skeleton(log)
    #print(log_skeleton)    # Отладка       

    visualize_model(log_skeleton)

if __name__ == "__main__":
    main()
