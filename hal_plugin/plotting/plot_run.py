import functools
import os
import numpy as np
import pprint as pp
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from oemof import outputlib, solph
from pandas import DataFrame

from hal_plugin.plotting.plotting import plot_kwh_analysis, plot_storage_diff, plot_general_hal_results
from oemof_runs.plot import plot_oemof_results
from hal_plugin.plotting.hal_data_processing import hal_load_import_kwh
from hal_plugin.plotting.oemof_data_processing import load_oemof_costs


def get_oemof_results(path: Path, file_name: str, exclude_storage=False):
    es = solph.EnergySystem()
    es.restore(path, file_name)
    results = es.results['main']
    meta = es.results['meta']
    b1_data = outputlib.views.node(results, 'b1')
    b_h_data = outputlib.views.node(results, 'b_h')
    storage_data = outputlib.views.node(results, 'storage')
    source1_data = outputlib.views.node(results, 'source1')
    heat_storage = outputlib.views.node(results, 'heat_storage')
    excess_data = outputlib.views.node(results, 'sink2_excess')
    pp.pprint(es.results['meta'])

    # Plot directly using pandas
    return {'storage_data': storage_data['sequences'] if not exclude_storage else None,
            'heat_storage': heat_storage['sequences'] if not exclude_storage else None,
            'b1_data': b1_data['sequences'],
            'b_h_data': b_h_data['sequences']}


def get_oemof_split_results(path: Path, i_max):
    results = [get_oemof_results(path, f"dump_{i}.oemof") for i in range(0, i_max)]
    return dict(
        functools.reduce(lambda agg, dict: {'storage_data': pd.concat([agg['storage_data'], dict['storage_data']]),
                                            'heat_storage': pd.concat([agg['heat_storage'], dict['heat_storage']]),
                                            'b1_data': pd.concat([agg['b1_data'], dict['b1_data']]),
                                            'b_h_data': pd.concat([agg['b_h_data'], dict['b_h_data']])}, results))


def plot_results(hal_sim_name='oemof_sim', oemof_dir=Path.cwd() / 'oemof_runs' / 'results', oemof_file='my_dump.oemof',
                 split_max=None, show=True, skip_storage=False):
    hal_dir = Path.cwd() / 'hal' / 'sim_results' / hal_sim_name
    if split_max is not None:
        oemof_results = get_oemof_split_results(oemof_dir, split_max)
    else:
        oemof_results = get_oemof_results(oemof_dir, oemof_file, exclude_storage=skip_storage)

    plot_oemof_results(oemof_results)
    plot_general_hal_results(hal_dir)

    # plot_heat_storage_details(oemof_results, hal_dir, hal_sim_name)
    # plot_p2h_details(oemof_results, hal_dir, hal_sim_name)
    # plot_prices(hal_dir, hal_sim_name)
    # if not skip_storage:
    #     plot_storage_diff(hal_dir, hal_sim_name, oemof_results)
    # plot_net_power_flow_analysis(hal_dir, hal_sim_name, oemof_results)
    plot_kwh_analysis(hal_dir, hal_sim_name, oemof_results)

    if show:
        plt.show()

def output_result_table(out_path: Path,
                        hal1_name,
                        hal2_name,
                        oemof1_name,
                        oemof2_name,
                        oemof_file,
                        hal_sim_name,
                        oemof_file2,
                        hal_sim_name2,
                        oemof_dir=Path.cwd() / 'oemof_runs' / 'results',
                        ):
    hal_dir = Path.cwd() / 'hal' / 'sim_results' / hal_sim_name
    oemof_results = get_oemof_results(oemof_dir, oemof_file, exclude_storage=True)
    hal_import = hal_load_import_kwh(hal_dir, hal_sim_name)
    oemof_import = load_oemof_costs(oemof_results)
    hal_import2 = hal_load_import_kwh(hal_dir, hal_sim_name)
    oemof_import2 = load_oemof_costs(oemof_results)

    DataFrame({
        f"{hal1_name}_total": hal_import['wh_total'].sum(),
        f"{hal2_name}_total": hal_import2['wh_total'].sum(),
        f"{oemof1_name}_total": oemof_import['wh_total'].sum(),
        f"{oemof2_name}_total": oemof_import2['wh_total'].sum(),
        f"{hal1_name}_mean": hal_import['wh_total'].mean(),
        f"{hal2_name}_mean": hal_import2['wh_total'].mean(),
        f"{oemof1_name}_mean": oemof_import['wh_total'].mean(),
        f"{oemof2_name}_mean": oemof_import2['wh_total'].mean(),
        f"{hal1_name}_std": hal_import['wh_total'].std(),
        f"{hal2_name}_std": hal_import2['wh_total'].std(),
        f"{oemof1_name}_std": oemof_import['wh_total'].std(),
        f"{oemof2_name}_std": oemof_import2['wh_total'].std(),
    })



def params_from_hal_path(str):
    groups = re.search('_([0-9\.]+)_([0-9\.]+)_([0-9])+$', str).groups(0)
    tau = groups[0]
    std = groups[1]
    return (tau, std)


def params_from_oemof_path(str):
    groups = re.search('_([0-9\.]+)_([0-9\.]+)_([0-9])+.oemof', str).groups(0)
    tau = groups[0]
    std = groups[1]
    i = groups[2]
    return (tau, std)


def group_by_f(list, fn, trnsfm_key=lambda x: x, trnfsm_el=lambda x: x):
    def group(agg, el):
        key = trnsfm_key(fn(el))
        l = agg.get(key, [])
        l.append(trnfsm_el(el))
        agg[key] = l
        return agg

    return functools.reduce(group, list, {})

def to_percentiles(costs, params_from_path_fn):
    hal_costs_by_param = group_by_f(costs, lambda x: params_from_path_fn(x[0]), trnsfm_key=lambda x: (float(x[0]), float(x[1])), trnfsm_el=lambda x: x[1])
    sorted_c_by_param = {k: hal_costs_by_param[k] for k in sorted(hal_costs_by_param, key=lambda x: x[1])}
    percentiles = np.percentile(list(sorted_c_by_param.values()), [25, 75], 1)
    mean = np.mean(list(sorted_c_by_param.values()), 1)
    return sorted_c_by_param, mean, percentiles

def plot_ensemble_results(hal_dir, hal_control_sim_name, hal_ensemble_prefix, oemof_dir, oemof_control,
                          oemof_prefix):
    hal_dirs = [dir for dir in os.listdir(hal_dir) if re.search('_([0-9\.]+)_([0-9\.]+)_([0-9])+$', dir) is not None]
    oemof_file_names = [file_name for file_name in os.listdir(oemof_dir) if re.search('_([0-9\.]+)_([0-9\.]+)_([0-9])+.oemof', file_name) is not None]

    oemof_control_results = get_oemof_results(oemof_dir, oemof_control, exclude_storage=True)
    plot_kwh_analysis(hal_dir / hal_control_sim_name, hal_control_sim_name, oemof_control_results)

    hal_costs = [(dir, hal_load_import_kwh(hal_dir / dir, dir)['wh'].sum() / 1000) for dir in hal_dirs]
    hal_costs_by_param, hal_mean, hal_percentiles = to_percentiles(hal_costs, params_from_hal_path)

    oemof_costs = [(file_name, load_oemof_costs(get_oemof_results(oemof_dir, file_name, exclude_storage=True))['wh'].sum() / 1000)
                     for file_name in oemof_file_names]
    oemof_costs_by_param, oemof_mean, oemof_percentiles = to_percentiles(oemof_costs, params_from_oemof_path)

    stds = [t[1] for t in hal_costs_by_param.keys()]

    fig, axes = plt.subplots(2, 1)
    axes[0].fill_between(stds, hal_percentiles[0], hal_percentiles[1], alpha=0.4)
    axes[0].plot(stds, hal_mean, 'x-')
    axes[0].fill_between(stds, oemof_percentiles[0], oemof_percentiles[1], alpha=0.4)
    axes[0].plot(stds, oemof_mean, 'x-')
    axes[0].set_title('Costs per noise intensity')
    axes[0].set_xlabel('std(noise)')
    axes[0].set_ylabel('KWh')
    axes[0].legend(['hal', 'oemof'])

    axes[1].plot(stds, hal_mean - oemof_mean, 'x')
    axes[1].set_title('Mean KWh Diff')
    axes[1].set_xlabel('std(noise)')
    axes[1].set_ylabel('diff')
    plt.show()


if __name__ == "__main__":
    plot_results('first_run', oemof_file='first_run.oemof', show=False)
    plot_results('scheduled_run', oemof_file='scheduled_run.oemof', show=True, skip_storage=True)
    output_result_table(Path.cwd() / 'result_data',
                        'pred', 'live-real',
                        'pred', 'scheduled-real',
                        'first_run.oemof', 'first_run',
                        'scheduled_run.oemof', 'scheduled_run')
