from pathlib import Path
import oemof.solph as solph

from plotting.hal_data_processing import load_hal_storage_df
from plotting.plot_run import get_oemof_results


def build_es_from_results(date_time_index, pv_data, load_data, heat_load_data, get_storage_mocks_fn):

    es2 = solph.EnergySystem(timeindex=date_time_index)
    b1 = solph.Bus(label="b1")
    es2.add(b1)
    # sources
    es2.add(solph.Source(label='source_pv',
                         outputs={
                             b1: solph.Flow(actual_value=pv_data,
                                            nominal_value=1,
                                            fixed=True,
                                            variable_costs=0)}))
    es2.add(solph.Source(label='source_import',
                         outputs={b1: solph.Flow(variable_costs=1)}))

    heat_storage_input, heat_storage_output, storage_input, storage_output = get_storage_mocks_fn()
    # storage
    es2.add(solph.Source(label='source_storage',
                         outputs={
                             b1: solph.Flow(actual_value=storage_output,
                                            nominal_value=1,
                                            fixed=True,
                                            variable_costs=0)}))
    es2.add(solph.Sink(label='sink_storage',
                       inputs={b1: solph.Flow(actual_value=storage_input,
                                              nominal_value=1,
                                              fixed=True)}))


    # sinks
    es2.add(solph.Sink(label='sink1_household',
                       inputs={b1: solph.Flow(actual_value=load_data,
                                              nominal_value=1,
                                              fixed=True)}))
    es2.add(solph.Sink(label='sink2_excess', inputs={b1: solph.Flow(variable_costs=1)}))

    # Heat network
    b_h = solph.Bus(label='b_h')
    es2.add(b_h)
    es2.add(solph.Source(label='source_heat_import',
                        outputs={b_h: solph.Flow(variable_costs=1)}))
    es2.add(solph.Sink(label='sink3_household_heat',
                       inputs={b_h: solph.Flow(actual_value=heat_load_data,
                                               nominal_value=1,
                                               fixed=True)}))
    es2.add(solph.Sink(label='sink4_excess_heat', inputs={b_h: solph.Flow(variable_costs=1)}))
    es2.add(solph.Source(label='source_heat_storage',
                         outputs={
                             b_h: solph.Flow(actual_value=heat_storage_output,
                                             nominal_value=1,
                                             fixed=True,
                                             variable_costs=0)}))
    es2.add(solph.Sink(label='sink_heat_storage',
                       inputs={b_h: solph.Flow(actual_value=heat_storage_input,
                                               nominal_value=1,
                                               fixed=True)}))

    # Transformer
    cop = 4.45
    es2.add(solph.Transformer(label='p2h', inputs={b1: solph.Flow()},
                              conversion_factors={b1: 1 / cop},
                              outputs={b_h: solph.Flow(max=1, nominal_value=13200)}))

    return es2


def get_storage_mocks_from_oemof(result_path: Path, file_name: str):
    oemof_results = get_oemof_results(result_path, file_name)
    storage_input = oemof_results['storage_data'][(('b1', 'storage'), 'flow')]
    storage_output = oemof_results['storage_data'][(('storage', 'b1'), 'flow')]
    heat_storage_input = oemof_results['heat_storage'][(('b_h', 'heat_storage'), 'flow')]
    heat_storage_output = oemof_results['heat_storage'][(('heat_storage', 'b_h'), 'flow')]
    return heat_storage_input, heat_storage_output, storage_input, storage_output

def build_es_from_oemof_sim_results(date_time_index, pv_data, load_data, heat_load_data, oemof_result_path: Path, file_name: str):
    return build_es_from_results(date_time_index, pv_data, load_data, heat_load_data, lambda : get_storage_mocks_from_oemof(oemof_result_path, file_name))


def get_storage_mocks_from_hal(hal_sim_res_path: Path, sim_name: str):
    storage_df, heat_storage_df = load_hal_storage_df(hal_sim_res_path, sim_name)
    storage_input = storage_df['power[W]'].clip_lower(0)
    storage_output = storage_df['power[W]'].clip_upper(0)
    heat_storage_input = heat_storage_df['power[W]'].clip_lower(0)
    heat_storage_output = heat_storage_df['power[W]'].clip_upper(0)
    return heat_storage_input, heat_storage_output, storage_input, storage_output

def build_es_from_hal_sim_results(date_time_index, pv_data, load_data, heat_load_data, hal_sim_res_path: Path, sim_name: str):
    return build_es_from_results(date_time_index, pv_data, load_data, heat_load_data, lambda : get_storage_mocks_from_hal(hal_sim_res_path, sim_name))

def build_es(date_time_index, pv_data, load_data, heat_load_data, defaults=None):
    es = solph.EnergySystem(timeindex=date_time_index)
    b1 = solph.Bus(label="b1")
    es.add(b1)
    # sources
    es.add(solph.Source(label='source_pv',
                        outputs={
                            b1: solph.Flow(actual_value=pv_data,
                                           nominal_value=1,
                                           fixed=True,
                                           variable_costs=0)}))
    es.add(solph.Source(label='source_import',
                        outputs={b1: solph.Flow(variable_costs=1)}))
    # storage
    p_max = 3000
    eta = 0.95
    storage = solph.components.GenericStorage(
        nominal_storage_capacity=4000,
        initial_storage_level=defaults['init_storage'] if defaults is not None else 0.0,
        inflow_conversion_factor=eta,
        outflow_conversion_factor=eta,
        label='storage',
        inputs={b1: solph.Flow(max=1, nominal_value=p_max)},
        outputs={b1: solph.Flow(max=1, nominal_value=p_max)}
    )
    es.add(storage)
    # sinks
    es.add(solph.Sink(label='sink1_household',
                      inputs={b1: solph.Flow(actual_value=load_data,
                                             nominal_value=1,
                                             fixed=True)}))
    es.add(solph.Sink(label='sink2_excess', inputs={b1: solph.Flow(variable_costs=1)}))

    # Heat network
    b_h = solph.Bus(label='b_h')
    es.add(b_h)
    es.add(solph.Source(label='source_heat_import',
                        outputs={b_h: solph.Flow(variable_costs=1)}))
    es.add(solph.Sink(label='sink3_household_heat',
                      inputs={b_h: solph.Flow(actual_value=heat_load_data,
                                              nominal_value=1,
                                              fixed=True)}))
    es.add(solph.Sink(label='sink4_excess_heat', inputs={b_h: solph.Flow(variable_costs=1)}))
    h_storage = solph.components.GenericStorage(
        nominal_storage_capacity=35000,
        initial_storage_level=defaults['init_heat_storage'] if defaults is not None else 0.0,
        inflow_conversion_factor=1,
        outflow_conversion_factor=1,
        label='heat_storage',
        inputs={b_h: solph.Flow(max=1, nominal_value=p_max)},
        outputs={b_h: solph.Flow(max=1, nominal_value=p_max)}
    )
    es.add(h_storage)

    # Transformer
    cop = 4.45
    es.add(solph.Transformer(label='p2h', inputs={b1: solph.Flow()},
                             conversion_factors={b1: 1 / cop},
                             outputs={b_h: solph.Flow(max=1, nominal_value=13200)}))
    return es
