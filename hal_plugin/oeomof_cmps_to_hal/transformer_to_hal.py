from oemof.solph import Bus, Transformer

from hal_plugin.helper import write_node_cfg
from hal_plugin.create_hal_nodes import create_transformer_node
from oeomof_cmps_to_hal.flow_to_hal import get_max_input_output_value


def transformer_to_hal(node_cfg_folder, parent: Bus, transformer: Transformer):
    cfg_name = f"{transformer.label}_cfg"
    parent_conversion_obj = transformer.conversion_factors.get(parent, None)

    # in oemof, the factor is multiplied with the input to determine how much of input A is needed to generate 1 unit of the output
    cop = 1 / parent_conversion_obj.default if parent_conversion_obj is not None else 1

    p_max = get_max_input_output_value(transformer)

    cfg = create_transformer_node(transformer.label, cop=cop, max_out=p_max) if p_max != 1 else create_transformer_node(transformer.label, cop=cop)
    write_node_cfg(node_cfg_folder, cfg, f"{cfg_name}.json")
    return transformer.label, cfg_name

