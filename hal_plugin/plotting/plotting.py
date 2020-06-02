from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from pandas import DataFrame

from hal_plugin.plotting.hal_data_processing import load_hal_b1_df, hal_load_import_kwh, load_hal_storage_df, \
    load_hal_p2h_df, load_all_hal_results
from hal_plugin.plotting.oemof_data_processing import load_oemof_net_power_flow, load_oemof_costs
from oemof_runs.plot import get_storage_data_from_saved_model


def plot_storage_diff(hal_dir, sim_name, oemof_results):
    oemof_storage_df, oemof_h_storage_df = get_storage_data_from_saved_model(oemof_results)
    hal_storage_df, hal_heat_storage_df = load_hal_storage_df(hal_dir, sim_name)

    storage_max_capacity = 4000
    diff = hal_storage_df['soc begin[%]'] - (
            oemof_storage_df[(('storage', 'None'), 'capacity')] / storage_max_capacity) * 100
    h_diff = hal_heat_storage_df['soc begin[%]'] - (
            oemof_h_storage_df[(('heat_storage', 'None'), 'capacity')] / storage_max_capacity) * 100
    diff_df = pd.DataFrame({'power soc diff': diff,
                            'heat soc diff': h_diff})
    diff_df.set_index(hal_storage_df.index)
    diff_df.plot(title='SOC Storage Difference -=hal, +=oemof', subplots=True)


def plot_general_hal_results(result_dir: Path):
    df = load_all_hal_results(result_dir)
    df2 = df.reindex(sorted(df.columns), axis=1)
    df2.plot(title='HAL Results', subplots=True, sort_columns=True)


def plot_net_power_flow_analysis(hal_result_dir, sim_name, oemof_results):
    oemof_net_power_flow = load_oemof_net_power_flow(oemof_results)
    hal_net_power_flow = load_hal_b1_df(hal_result_dir, sim_name)

    fig, axes = plt.subplots(nrows=3)

    net_flow_df = pd.DataFrame(
        {'hal': hal_net_power_flow['res_power[W]'], 'oemof': oemof_net_power_flow['net_power_flow']},
        index=oemof_net_power_flow.index)

    net_flow_df.plot(title='Net Power Flows [w] (positive = import)', ax=axes[0])
    net_flow_df.plot.hist(bins=100, ax=axes[1])
    net_flow_df.plot.box(ax=axes[2], showfliers=False, grid=True)


def plot_kwh_analysis(hal_result_dir, sim_name, oemof_results):
    hal_import = hal_load_import_kwh(hal_result_dir, sim_name)
    oemof_import = load_oemof_costs(oemof_results)

    fig, axes = plt.subplots(nrows=3)
    total_hal = hal_import['wh_total'] / 1000
    total_oemof = oemof_import['wh_total'] / 1000
    mixed_costs = pd.DataFrame({
        # 'hal_power_import': hal_import['wh'] / 1000,
        # 'oemof_power_import': oemof_import['wh'] / 1000,
        # 'hal_heat_import': hal_import['wh (heat)'] / 1000,
        # 'oemof_heat_import': oemof_import['wh (heat)'] / 1000,
        'hal_total_import': total_hal,
        'oemof_total_import': total_oemof,
        'import_diff': total_oemof - total_hal
    },
        index=oemof_import.index)
    mixed_costs.plot(title=f"KWh imported ", ax=axes[0])
    mixed_costs.cumsum().plot(title='Cummulated Imported KWh', ax=axes[1])
    mixed_costs.sum().plot.bar(title='Total KWh comparison', ax=axes[2], grid=True)


def plot_heat_storage_details(oemof_results, result_dir, sim_name):
    b, h_df = load_hal_storage_df(result_dir, sim_name)

    oemof_results['heat_storage'].plot(kind='line', drawstyle='steps-post', title='Oemof Heat Storage Details',
                                       subplots=True)
    h_df.plot(subplots=True, title='HAL Heat Storage Details')


def plot_p2h_details(oemof_results, result_dir, sim_name):
    p2h: DataFrame = load_hal_p2h_df(result_dir, sim_name)

    oemof_results['b_h_data'].plot(kind='line', drawstyle='steps-post', title='Oemof Heat Flow', subplots=True)
    p2h.plot(subplots=True, title='P2H Details')


def plot_prices(result_dir, sim_name):
    b1: DataFrame = load_hal_b1_df(result_dir, sim_name)
    p2h: DataFrame = load_hal_p2h_df(result_dir, sim_name)

    fig, axes = plt.subplots(2, 1)
    b1[['local_price']].plot(title='B1 Market Price', ax=axes[0])
    p2h[['local_price']].plot(title='P2H Market Price', ax=axes[1])
