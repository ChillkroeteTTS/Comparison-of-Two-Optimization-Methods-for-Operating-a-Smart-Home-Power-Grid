import json
from collections import Set
from pathlib import Path

from oemof.solph import EnergySystem, Source, Sink, Bus, Transformer
from oemof.solph.blocks import Flow
from oemof.solph.components import GenericStorage
from pandas import DatetimeIndex

from hal.src.congf_file_handling.sim_config_factory import SimConfigFactory
from hal_plugin.create_hal_nodes import create_top_node_cfg
from hal_plugin.errors.hal_configuration_error import HalConfigurationError
from hal_plugin.helper import write_node_cfg
from hal_plugin.oeomof_cmps_to_hal.bus_to_hal import bus_to_hal
from hal_plugin.oeomof_cmps_to_hal.source_sink_to_hal import source_to_hal, sink_to_hal
from hal_plugin.oeomof_cmps_to_hal.storage_to_hal import generic_storage_to_hal
from oeomof_cmps_to_hal.transformer_to_hal import transformer_to_hal


def find_top_parent(es: EnergySystem):
    has_no_parent_inputs = lambda e: len([edge for edge in e._in_edges if isinstance(edge, Bus) or isinstance(edge, Transformer)]) == 0
    top_buses = [e.label for e in es.entities if isinstance(e, Bus) and has_no_parent_inputs(e)]
    if len(top_buses) == 1:
        return es.groups[top_buses[0]]
    else:
        raise HalConfigurationError('Only one bus is allowed to be root node (having no parent inputs)')


def es_to_hal_sim_cfg(es: EnergySystem, sim_name='oemof_sim'):
    time_index: DatetimeIndex = es.timeindex
    data_folder = Path.cwd() / 'hal' / 'data' / 'yearly_data' / 'oemof_sim'
    node_cfg_folder = Path.cwd() / 'hal' / 'node_cfg'
    conf_fac = SimConfigFactory(sim_name, node_cfg_dir=node_cfg_folder)

    create_top_node(conf_fac, node_cfg_folder, time_index)

    buses = [e.label for e in es.entities if isinstance(e, Bus)]
    print(buses)

    top_bus = find_top_parent(es)
    create_parent_node(conf_fac, data_folder, es, node_cfg_folder, time_index, 'top_node', top_bus)

    print(conf_fac.make_sim_dict())
    return conf_fac.make_sim_dict()


def create_parent_node(conf_fac, data_folder, es, node_cfg_folder, time_index, parent_id, bus_or_transformer):

    # Create parent node
    if isinstance(bus_or_transformer, Transformer):
        sub_parent_node_id, sub_parent_cfg_name = transformer_to_hal(node_cfg_folder, es.groups[parent_id], bus_or_transformer)
        sub_bus = [t[1] for t in es.groups[Flow] if t[0] == bus_or_transformer][0]
        outputs = [t[1] for t in es.groups[Flow] if t[0] == sub_bus]
        inputs = [t[0] for t in es.groups[Flow] if t[1] == sub_bus and t[0] != bus_or_transformer]
        bus_or_transformer = sub_bus
    elif isinstance(bus_or_transformer, Bus):
        sub_parent_node_id, sub_parent_cfg_name = bus_to_hal(node_cfg_folder, bus_or_transformer)
        outputs = [t[1] for t in es.groups[Flow] if t[0] == bus_or_transformer]
        inputs = [t[0] for t in es.groups[Flow] if t[1] == bus_or_transformer]
    else:
        raise HalConfigurationError('Only bus or transformers are allowed as parent nodes')

    conf_fac.insert_sub_node(parent_node_id=parent_id, node_id=sub_parent_node_id, node_config=sub_parent_cfg_name)

    create_sub_nodes(sub_parent_node_id, conf_fac, data_folder, es, node_cfg_folder, time_index, bus_or_transformer, inputs, outputs)


def create_sub_nodes(parent_node_id, conf_fac, data_folder, es, node_cfg_folder, time_index, top_bus, inputs, outputs):

    for entity in set(inputs + outputs):
        if isinstance(entity, Transformer) or isinstance(entity, Bus):
            create_parent_node(conf_fac, data_folder, es, node_cfg_folder, time_index, parent_node_id, entity)
            node_res = None
        elif isinstance(entity, Source):
            node_res = source_to_hal(time_index, node_cfg_folder, data_folder, entity)
        elif isinstance(entity, Sink):
            node_res = sink_to_hal(time_index, node_cfg_folder, data_folder, top_bus, entity)
        elif isinstance(entity, GenericStorage):
            node_res = generic_storage_to_hal(node_cfg_folder, entity)
        else:
            raise HalConfigurationError(f"unknown instance of type {type(entity)}")

        if node_res is not None:
            node_id, cfg_name = node_res
            conf_fac.insert_sub_node(parent_node_id=parent_node_id, node_id=node_id, node_config=cfg_name)


def create_top_node(conf_fac, node_cfg_folder: Path, time_index: DatetimeIndex):
    cfg_name = 'sim_control_oemof_sim'
    cfg_file_name = f"{cfg_name}.json"
    write_node_cfg(node_cfg_folder, create_top_node_cfg(len(time_index), month_start=time_index[0].month, day_start=time_index[0].day), cfg_file_name)
    conf_fac.insert_top_node(node_id='top_node', node_config=cfg_name)
