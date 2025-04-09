import pm4py
from pandas import read_csv, DataFrame


def getting_log(file_path: str) -> DataFrame:
    if file_path.split(".")[-1] == "xes":
        return pm4py.read_xes(file_path)
    if file_path.split(".")[-1] == "csv":
        return read_csv(file_path)


def execute_script() -> None:
    # example where the log skeleton is manullay built, and not automatically discovered from the log.
    log = getting_log("running-example.xes")

    log_skeleton = {
        "always_after": set(),
        "always_before": set(),
        "equivalence": set(),
        "never_together": set(),
        "directly_follows": set(),
        "activ_freq": dict(),
    }

    for act in pm4py.get_event_attribute_values(log, "concept:name"):
        # initially sets that every activity of the log can occur from 0 to 10 times
        # (without this constraints, conformance checking will signal deviations for every event)
        log_skeleton["activ_freq"][act] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

    # sets that the 'reinitiate request' activity should not occur (so it occurs 0 times)
    log_skeleton["activ_freq"]["reinitiate request"] = {0}

    # sets that the 'pay compensation' activity should occur somewhen after the 'decide' activity.
    log_skeleton["always_after"].add(("decide", "pay compensation"))

    # gets the conformance checking results. The first describes for each case of the log the exact deviations
    detailed_conf_results = pm4py.conformance_log_skeleton(log, log_skeleton)
    print(detailed_conf_results)

    # the second provides a summary (as a dataframe) of the fitness per case
    summary_df = pm4py.conformance_log_skeleton(
        log, log_skeleton, return_diagnostics_dataframe=True
    )
    print(summary_df)


def main() -> None:
    execute_script()


if __name__ == "__main__":
    main()
