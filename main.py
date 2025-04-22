from typing import Any, Dict

from pandas import DataFrame, read_csv
from pm4py import discover_log_skeleton, read_xes


# Determines file format and retrieves event logs
def getting_log(file_path: str) -> DataFrame:
    if file_path.split(".")[-1] == "xes":
        return read_xes(file_path)
    if file_path.split(".")[-1] == "csv":
        return read_csv(file_path)


# TODO: when import csv - exeption: the dataframe should (at least) contain a column of type date
def build_log_skeleton(log: DataFrame) -> Dict[str, Any]:
    log_skeleton = discover_log_skeleton(log, noise_threshold=0.0)
    return log_skeleton


def main() -> None:
    log = getting_log(input("Enter path to xes/csv file: "))
    res = build_log_skeleton(log)
    print(res)


if __name__ == "__main__":
    main()
