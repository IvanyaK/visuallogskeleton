from typing import Any, Dict

from chardet import detect
from pandas import DataFrame, read_csv
from pm4py import discover_log_skeleton, format_dataframe, read_xes

from visualize import visualize_model
# Determines file format and retrieves event logs
def getting_log(file_path: str) -> DataFrame:
    if file_path.split(".")[-1] == "xes":
        return read_xes(file_path)

    if file_path.split(".")[-1] == "csv":
        with open(file_path, "rb") as f:
            result = detect(f.read())

        log = read_csv(file_path, encoding=result["encoding"])

        case_id = input("Your case_id: ")
        activity_key = input("Your activity_key: ")
        timestamp_key = input("Your timestamp: ")
        log = format_dataframe(
            log,
            case_id=case_id,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            timest_format="%Y-%m-%d %H:%M:%S",
        )

        return log


def build_log_skeleton(log: DataFrame) -> Dict[str, Any]:
    log_skeleton = discover_log_skeleton(log, noise_threshold=0.0)
    return log_skeleton


def main() -> None:
    log = getting_log(input("Enter path to xes/csv file: "))
    res = build_log_skeleton(log)
    visualize_model(res)

if __name__ == "__main__":
    main()
