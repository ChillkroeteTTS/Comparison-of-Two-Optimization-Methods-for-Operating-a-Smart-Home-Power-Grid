import pandas as pd
import json
import os
from pathlib import Path

from oemof.solph import Flow


def array_from_flow(flow: Flow):
    if len(flow.actual_value) > 0:
        return flow.actual_value.array * flow.nominal_value
    else:
        return None


def write_node_cfg(node_cfg_folder: Path, node_cfg, file_name: str):
    os.makedirs(str(node_cfg_folder), exist_ok=True)
    with open(str(node_cfg_folder / file_name), 'w') as fp:
        json.dump(node_cfg, fp)


def write_power_values(time_index, power_values, data_folder, file_name):
    out_path = data_folder
    os.makedirs(out_path, exist_ok=True)
    pd.DataFrame({'Time': time_index, 'power[W]': power_values}) \
        .to_csv(out_path / file_name, index=False)


def cfg_name(cmp) -> str:
    return f"{get_label(cmp)}_cfg.json"


def data_name(cmp) -> str:
    return f"{get_label(cmp)}_data.csv"


def get_label(cmp) -> str:
    return cmp.label


def get_last_part(path: Path):
    return path.parts[len(path.parts) - 1]
