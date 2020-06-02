
def get_max_input_output_value(component, default_value=None):
    """
    Returns default value if value is not set
    :param component:
    :return:
    """
    max = list(component.outputs.data.values())[0].max.default
    nominal_value = list(component.outputs.data.values())[0].nominal_value
    oemof_default = 1
    max_res = max * (nominal_value if nominal_value is not None else 1)
    return max_res if (max_res != oemof_default) or default_value is None else default_value

