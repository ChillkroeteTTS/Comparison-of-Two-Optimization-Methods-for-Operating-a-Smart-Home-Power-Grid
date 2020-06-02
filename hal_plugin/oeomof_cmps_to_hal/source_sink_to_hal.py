from pathlib import Path

from oemof.network import Bus
from oemof.solph import Source, Sink, Flow

from hal_plugin.errors.hal_configuration_error import HalConfigurationError
from hal_plugin.helper import array_from_flow, write_power_values, write_node_cfg, cfg_name, data_name, get_label, \
    get_last_part
from hal_plugin.create_hal_nodes import create_inelastic_node


def source_to_hal(time_index, node_cfg_folder, data_folder, source: Source):
    output_targets = list(source.outputs.data.values())
    direction_factor = -1
    if len(output_targets) == 1:
        return source_sink_to_hal(node_cfg_folder, data_folder, direction_factor, output_targets[0], source, time_index)
    else:
        raise HalConfigurationError(
            f"{len(output_targets)} targets/sources can't be configured in HAL, only 1 target/source is allowed")


def sink_to_hal(time_index, node_cfg_folder, data_folder, bus: Bus, sink: Sink):
    flow = bus.outputs.data[sink]
    direction_factor = 1
    return source_sink_to_hal(node_cfg_folder, data_folder, direction_factor, flow, sink, time_index)


def source_sink_to_hal(node_cfg_folder, data_folder: Path, direction_factor, flow: Flow, source_or_sink, time_index):
    power_values = array_from_flow(flow)
    if power_values is not None:
        write_power_values(time_index, power_values, data_folder, data_name(source_or_sink))
        node_cfg = create_inelastic_node(get_last_part(data_folder), data_name(source_or_sink), direction_factor)
        write_node_cfg(node_cfg_folder, node_cfg, cfg_name(source_or_sink))
        return get_label(source_or_sink), cfg_name(source_or_sink)
    else:
        return None
