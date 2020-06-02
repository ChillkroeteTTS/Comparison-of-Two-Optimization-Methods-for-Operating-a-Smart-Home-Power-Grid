import math

from oemof.outputlib import processing
import numpy as np

from data.create_test_data import create_test_data
from plotting.plot_run import plot_results
from hal_plugin.src.handle_es import build_es
from hal_plugin.src.system import run_oemof, run_hal


def run_oemof_sliced(es, index):
    print('run oemof simulation')
    om = solph.Model(es)
    om.solve(solver='cbc')
    es.results['main'] = processing.results(om)
    es.results['meta'] = processing.meta_results(om)
    es.dump(str(Path.cwd() / 'oemof_runs' / 'results_sliced'), f"dump_{index}.oemof")
    print('oemof done')

if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path

    print(Path.cwd())
    print(os.getcwd())
    # super important to be able to run hal outside of its own context, otherwise "module not found"-errors will occur
    sys.path.append(str(Path.cwd() / 'hal'))
    sys.path.append(str(Path.cwd() / 'hal' / 'src'))

    import oemof.solph as solph
    import pandas as pd


    # generate data
    day = 60 * 24
    week = day * 7
    month = week * 4
    time_window = day
    time_range = ['2016-09-01', '2016-10-01']
    paths = create_test_data(time_range, False)

    # load data
    load_data = pd.read_csv(paths['load_data'])['power[W]']
    pv_data = pd.read_csv(paths['pv_data'])['power[W]']
    heat_load_data = pd.read_csv(paths['load_heat_data'])['power[W]']
    date_time_index = pd.date_range(time_range[0], periods=len(pv_data), freq='min')

    no_of_datapoints = len(load_data)
    no_of_chunks = math.ceil(no_of_datapoints / time_window)

    split_load_data = np.array_split(load_data, no_of_chunks)
    split_pv_data = np.array_split(pv_data, no_of_chunks)
    split_heat_load_data = np.array_split(heat_load_data, no_of_chunks)
    split_date_time_index = np.array_split(date_time_index, no_of_chunks)

    es = build_es(date_time_index, pv_data, load_data, heat_load_data)
    # run_oemof(es, 'incremental_baseline_result')
    # run_hal(es)

    for i in range(0, no_of_chunks):
        es = build_es(split_date_time_index[i], list(split_pv_data[i]), list(split_load_data[i]), list(split_heat_load_data[i]))
        run_oemof_sliced(es, i)

    plot_results('oemof_sim', oemof_file='incremental_baseline_result', show=False)
    plot_results(oemof_dir=Path.cwd() / 'oemof_runs' / 'results_sliced', split_max=no_of_chunks)
