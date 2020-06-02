import pandas as pd


# loads a DF which contains information about the netto power flow in and out of the system
# positive values indicate power which flows INTO the system
# negative values power which flows OUT of the system
def load_oemof_net_power_flow(oemof_results):
    b1 = oemof_results['b1_data']

    diff = b1[(('source_import', 'b1'), 'flow')] - b1[(('b1', 'sink2_excess'), 'flow')]
    return pd.DataFrame({'net_power_flow': diff}, index=b1.index)


def load_oemof_costs(oemof_results):
    b1 = oemof_results['b1_data']
    b_h = oemof_results['b_h_data']
    return pd.DataFrame({'import_power_flow': b1[(('source_import', 'b1'), 'flow')],
                         'wh': b1[(('source_import', 'b1'), 'flow')] * 60 / 3600,
                         'wh_total': b1[(('source_import', 'b1'), 'flow')] * 60 / 3600 + b_h[(('source_heat_import', 'b_h'), 'flow')] * 60 / 3600,
                         'wh (heat)': b_h[(('source_heat_import', 'b_h'), 'flow')] * 60 / 3600}, index=b1.index)
