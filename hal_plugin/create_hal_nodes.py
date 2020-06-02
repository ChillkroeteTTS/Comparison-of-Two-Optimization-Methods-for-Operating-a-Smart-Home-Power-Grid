def create_top_node_cfg(no_of_datapoints, month_start=1, day_start=1, interval=60, delay_start=10):
    return {
        "node_class": "src.basic_structure.nodes.sim_control_top_node.SimControlTopNode",
        "behavior_parameter": {
            "i_max": no_of_datapoints,
            "month_start": month_start,
            "day_start": day_start,
            "interval": interval,
            "delay_start": delay_start,
        },
        "behavior_class": "src.behaviors.sim_control.SimControlBehavior"
    }


def create_inelastic_node(data_folder: str, data_name, direction_factor=1):
    return {
        "node_class": "src.basic_structure.nodes.node_leaf_zmq.NodeLeafZmq",
        "behavior_parameter": {
            "folder_data": str(data_folder),
            "data_file_name": data_name,
            "direction_factor": direction_factor,
        },
        "behavior_class": "src.behaviors.inelastic.InelasticBehavior"
    }


def create_parent_node(label='parent_node_0_target'):
    return {
        'node_class': 'src.basic_structure.nodes.node_parent_zmq.NodeParentZmq',
        'label': label,
        'behavior_parameter': {'target_q': 0},
        "behavior_class": "src.behaviors.parent_power_target.PowerTargetBehavior"
    }


def create_transformer_node(label='transformer', cop=4.2, max_out=6000):
    # https://www.ochsner.com/de-de/ochsner-produkte/produktdetail/ochsner-air-18-c11a/ one example
    return {
        'node_class': 'src.basic_structure.nodes.node_parent_zmq.NodeParentZmq',
        'label': label,
        'behavior_parameter': {
            'cop': cop,
            'max_out': max_out
        },
        "behavior_class": "src.behaviors.parent_transformer.TransformerBehavior"
    }


def create_storage_node(capacity, eta, init_soc, p_max):
    return {
        "node_class": "src.basic_structure.nodes.node_leaf_zmq.NodeLeafZmq",
        "behavior_class": "src.behaviors.battery.BatteryBehaviorSim",
        "behavior_parameter": {},
        "system_parameter": {
            "capacity": capacity / 1000,
            "p_max": p_max,
            "eta": eta,
            "soc_init": init_soc,
            "soc_min": 0,
            "soc_max": 100
        },
        "system_class": "src.system_models.battery.BatteryModel"
    }
