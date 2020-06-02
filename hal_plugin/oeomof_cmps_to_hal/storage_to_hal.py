from pathlib import Path

from oemof.solph.components import GenericStorage

from create_hal_nodes import create_storage_node
from hal_plugin.helper import write_node_cfg, get_label, cfg_name
from oeomof_cmps_to_hal.flow_to_hal import get_max_input_output_value


def get_conversion_factor(storage):
    oemoef_conversion_factor_default = 1
    return storage.inflow_conversion_factor.default \
        if storage.inflow_conversion_factor.default != oemoef_conversion_factor_default \
        else storage.outflow_conversion_factor.default

def generic_storage_to_hal(node_cfg_folder: Path, storage: GenericStorage):
    """
    There are still some flaws in conversion to hal:
        - HAL requires the max output/input value to be the same. Thus the max output value of oemof is taken as this value (since it's easier accessable)
        - HAL requires the conversion factor to be the same. Thus we use the factor which is different from the default

    :param node_cfg_folder:
    :param storage:
    :return:
    """
    capacity = storage.nominal_storage_capacity
    init_soc = storage.initial_storage_level * 100

    # HAL supports only one conversion factor so far, thus take the one which is different from system default
    eta = get_conversion_factor(storage)

    # HAL supports only a single value for max in/out. Thus take the easier accessible output max
    p_max = get_max_input_output_value(storage, capacity)

    node_cfg = create_storage_node(capacity, eta, init_soc, p_max)
    write_node_cfg(node_cfg_folder, node_cfg, cfg_name(storage))
    return get_label(storage), cfg_name(storage)
