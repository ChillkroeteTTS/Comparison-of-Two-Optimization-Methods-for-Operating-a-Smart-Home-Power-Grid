from pathlib import Path

from plotting.hal_data_processing import hal_load_import_kwh
from plotting.oemof_data_processing import load_oemof_costs
from plotting.plot_run import get_oemof_split_results, get_oemof_results
import matplotlib.pyplot as plt
import pandas as pd

from result_data.plotting.final_plots import dataframe_to_stat_table


def incremental_net_import_analysis():
    base_path = Path().cwd() / 'result_data'
    incr_path = base_path / 'incremental setup - sept'

    oemof_baseline = load_oemof_costs(get_oemof_results(base_path, 'oemof_baseline_result_pvol.oemof'))
    hal_sim_name = 'hal_baseline_result_pvol'
    hal_baseline = hal_load_import_kwh(base_path / hal_sim_name, hal_sim_name)
    split_24h = load_oemof_costs(get_oemof_split_results(incr_path / 'sliced_24h', 30))
    split_12h = load_oemof_costs(get_oemof_split_results(incr_path / 'sliced_12h', 60))
    split_6h = load_oemof_costs(get_oemof_split_results(incr_path / 'sliced_6h', 120))


    fig, axes = plt.subplots(nrows=2)
    total_hal_baseline = hal_baseline['wh_total'] / 1000
    total_oemof_baseline = oemof_baseline['wh_total'] / 1000
    total_oemof_24h = split_24h['wh_total'] / 1000
    total_oemof_12h = split_12h['wh_total'] / 1000
    total_oemof_6h = split_6h['wh_total'] / 1000

    mixed_costs = pd.DataFrame({
        'BL HAL': total_hal_baseline,
        'BL OEMOF': total_oemof_baseline,
        '24h split': total_oemof_24h,
        '12h split': total_oemof_12h,
        '6h split': total_oemof_6h,
    },
        index=total_oemof_baseline.index)
    mixed_costs.cumsum().plot(ax=axes[0]).set_ylabel('KWh')
    total_plot = mixed_costs.sum().plot.bar(ax=axes[1], grid=True)
    total_plot.set_ylabel('KWh')
    total_plot.set_xlabel('t')
    fig.subplots_adjust(left=0.12, right=0.97, top=0.92, bottom=0.19, hspace=0.53)
    plt.savefig("praktikumsbericht/images/splits_total.pdf")

    fig, axes = plt.subplots(nrows=1)
    mixed_costs.boxplot(grid=True, showfliers=False, ax=axes)
    dataframe_to_stat_table(incr_path / 'stats.csv', mixed_costs)


    fig.subplots_adjust(left=0.12, right=0.96, top=0.93, bottom=0.07, hspace=0.20)
    # plt.show()
    plt.savefig("praktikumsbericht/images/splits_peaks.pdf")

if __name__ == "__main__":
    incremental_net_import_analysis()
