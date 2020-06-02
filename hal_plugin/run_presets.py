from pathlib import Path

import pandas as pd
from data.create_test_data import create_test_data
from hal_plugin.src.handle_es import build_es_from_oemof_sim_results, build_es_from_hal_sim_results, build_es
from hal_plugin.src.system import run_hal, run_oemof


def run_simulation(time_range, pv_path, heat_load_path, hal_result_sim_name, oemof_result_file_name):
    # generate data
    paths = create_test_data(time_range, False, pv_data_path=pv_path, heat_load_path=heat_load_path)

    # load data
    load_data = pd.read_csv(paths['load_data'])['power[W]']
    pv_data = pd.read_csv(paths['pv_data'])['power[W]']
    heat_load_data = pd.read_csv(paths['load_heat_data'])['power[W]']

    date_time_index = pd.date_range(time_range[0], periods=len(pv_data), freq='min')
    es = build_es(date_time_index, pv_data, load_data, heat_load_data)

    run_hal(es, hal_result_sim_name)
    run_oemof(es, oemof_result_file_name)


def run_with_existing_schedule(oemoef_schedule_file_name, time_range, pv_path, hal_result_sim_name,
                               oemof_result_file_name):
    # generate data
    paths = create_test_data(time_range, False, pv_data_path=pv_path)

    # load data
    load_data = pd.read_csv(paths['load_data'])['power[W]']
    pv_data = pd.read_csv(paths['pv_data'])['power[W]']
    heat_load_data = pd.read_csv(paths['load_heat_data'])['power[W]']

    date_time_index = pd.date_range(time_range[0], periods=len(pv_data), freq='min')
    es = build_es(date_time_index, pv_data, load_data, heat_load_data)

    # run oemof with existing schedule
    scheduled_es = build_es_from_oemof_sim_results(date_time_index, pv_data, load_data, heat_load_data,
                                             Path.cwd() / 'oemof_runs' / 'results', oemoef_schedule_file_name)

    run_hal(es, hal_result_sim_name)
    run_oemof(scheduled_es, oemof_result_file_name)


def run_both_with_existing_schedule(oemoef_schedule_file_name, hal_schedule_sim_name, time_range, pv_path,
                                    hal_result_file_name, oemof_result_file_name):
    # generate data
    paths = create_test_data(time_range, False, pv_data_path=pv_path)

    # load data
    load_data = pd.read_csv(paths['load_data'])['power[W]']
    pv_data = pd.read_csv(paths['pv_data'])['power[W]']
    heat_load_data = pd.read_csv(paths['load_heat_data'])['power[W]']

    date_time_index = pd.date_range(time_range[0], periods=len(pv_data), freq='min')
    hal_scheduled_es = build_es_from_hal_sim_results(date_time_index, pv_data, load_data, heat_load_data,
                                                     Path.cwd() / 'hal' / 'sim_results' / hal_schedule_sim_name, hal_schedule_sim_name)

    # run oemof with existing schedule
    oemof_scheduled_es = build_es_from_oemof_sim_results(date_time_index, pv_data, load_data, heat_load_data,
                                                   Path.cwd() / 'oemof_runs' / 'results', oemoef_schedule_file_name)

    run_oemof(oemof_scheduled_es, oemof_result_file_name)
    run_oemof(hal_scheduled_es, hal_result_file_name)
