from hal_plugin.helper import write_node_cfg
from hal_plugin.create_hal_nodes import create_parent_node


def bus_to_hal(node_cfg_folder, bus):
    cfg_name = f"{bus.label}_cfg"
    write_node_cfg(node_cfg_folder, create_parent_node(bus.label), f"{cfg_name}.json")
    return bus.label, cfg_name

