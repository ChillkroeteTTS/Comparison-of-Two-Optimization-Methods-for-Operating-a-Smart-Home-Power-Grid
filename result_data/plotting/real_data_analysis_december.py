from pathlib import Path

from pandas import DataFrame

from plotting.hal_data_processing import hal_load_import_kwh, load_hal_storage_df
from plotting.oemof_data_processing import load_oemof_costs
from plotting.plot_run import get_oemof_results
import matplotlib.pyplot as plt
import pandas as pd

from result_data.plotting.final_plots import dataframe_to_stat_table


# def real_data_net_import_analysis():
#     base_path = Path().cwd() / 'result_data'
#     dec_setup_path = base_path / 'schedule vs real - dec'
#
#     oemof_baseline = load_oemof_costs(get_oemof_results(dec_setup_path, 'baseline_pred.oemof', True))
#     hal_baseline = hal_load_import_kwh(dec_setup_path / 'baseline_pred', 'baseline_pred')
#
#     oemof_dec = load_oemof_costs(get_oemof_results(dec_setup_path, 'real_data_offline.oemof', True))
#     hal_dec = hal_load_import_kwh(dec_setup_path / 'real_data_online', 'real_data_online')
#
#     total_hal_baseline = hal_baseline['wh_total'] / 1000
#     total_oemof_baseline = oemof_baseline['wh_total'] / 1000
#     total_hal_dec = hal_dec['wh_total'] / 1000
#     total_oemof_dec = oemof_dec['wh_total'] / 1000
#
#     mixed_costs = pd.DataFrame({
#         'HAL controlled': total_hal_dec,
#         'Schedule controlled': total_oemof_dec,
#     }, index=total_oemof_baseline.index)
#
#     fig, axes = plt.subplots(nrows=1)
#
#     mixed_costs.cumsum().plot(ax=axes).set_ylabel('KWh')
#     fig.subplots_adjust(left=0.12, right=0.97, top=0.92, bottom=0.19, hspace=0.53)
#     plt.savefig("praktikumsbericht/images/dec_real_total.pdf")
#     dataframe_to_stat_table(dec_setup_path / 'stats.csv', mixed_costs)
#     plt.show()

def real_data_net_import_analysis():
    base_path = Path().cwd() / 'result_data'
    sept_setup_path = base_path / 'schedule vs real - sept'
    dec_setup_path = base_path / 'schedule vs real - dec'

    sept_total_hal_baseline, sept_total_oemof_baseline, sept_total_hal, sept_total_oemof = get_baseline(sept_setup_path)
    dec_total_hal_baseline, dec_total_oemof_baseline, dec_total_hal, dec_total_oemof = get_baseline(dec_setup_path)

    mixed_costs = pd.DataFrame({
        'Sept Pred HAL': sept_total_hal_baseline,
        'Sept Pred OEMOF': sept_total_oemof_baseline,
        'Sept Real HAL': sept_total_hal,
        'Sept Real OEMOF': sept_total_oemof,
        'Dec Pred HAL': dec_total_hal_baseline,
        'Dec Pred OEMOF': dec_total_oemof_baseline,
        'Dec Real HAL': dec_total_hal,
        'Dec Real OEMOF': dec_total_oemof,
    }, index=pd.date_range('2016-09-01', '2017-01-01', freq='min'))

    fig, axes = plt.subplots(nrows=1)

    summed = mixed_costs.sum()
    summed.plot.bar(ax=axes, grid=True).set_ylabel('KWh')
    fig.subplots_adjust(left=0.12, right=0.97, top=0.92, bottom=0.19, hspace=0.53)
    plt.savefig("praktikumsbericht/images/dec_real_total.pdf")
    dataframe_to_stat_table(dec_setup_path / 'stats.csv', mixed_costs)

    ratios = DataFrame({
        'HAL Pred/Real': [summed['Sept Pred HAL'] / summed['Sept Real HAL'], summed['Dec Pred HAL'] / summed['Dec Real HAL']],
        'OEMOF Pred/Real': [summed['Sept Pred OEMOF'] / summed['Sept Real OEMOF'], summed['Dec Pred OEMOF'] / summed['Dec Real OEMOF']],
        'Pred OEMOF/HAL': [summed['Sept Pred OEMOF'] / summed['Sept Pred HAL'], summed['Dec Pred OEMOF'] / summed['Dec Pred HAL']],
        'Real OEMOF/HAL': [summed['Sept Real OEMOF'] / summed['Sept Real HAL'], summed['Dec Real OEMOF'] / summed['Dec Real HAL']],
    }, index=['September', 'December'])
    dataframe_to_stat_table(dec_setup_path / 'ratios.csv', ratios)

    diff = ratios[['Pred OEMOF/HAL', 'Real OEMOF/HAL']].diff(axis='columns')[['Real OEMOF/HAL']].rename({'Real OEMOF/HAL': 'Real OEMOF/HAL - PRED OEMOF/HAL'}, axis='columns')
    dataframe_to_stat_table(dec_setup_path / 'diff.csv', diff)
    diff.to_latex(open("praktikumsbericht/images/real_data_diff.tex", 'w'),
                         label='t/res/diff',
                         caption='Difference between the ratio of HALs and OEMOFs net import ..',
                         float_format="%.2f")




    # Percentiles
    fig, axes = plt.subplots(nrows=1)
    boxplot = mixed_costs.boxplot(grid=True, showfliers=False, ax=axes)
    boxplot.set_ylabel('kWh')
    fig.subplots_adjust(left=0.12, right=0.96, top=0.93, bottom=0.07, hspace=0.20)
    plt.savefig("praktikumsbericht/images/dec_real_peaks.pdf")

    # plt.show()


def get_baseline(dec_setup_path):
    oemof_baseline = load_oemof_costs(get_oemof_results(dec_setup_path, 'baseline_pred.oemof', True))
    hal_baseline = hal_load_import_kwh(dec_setup_path / 'baseline_pred', 'baseline_pred')
    oemof_dec = load_oemof_costs(get_oemof_results(dec_setup_path, 'real_data_offline.oemof', True))
    hal_dec = hal_load_import_kwh(dec_setup_path / 'real_data_online', 'real_data_online')
    total_hal_baseline = hal_baseline['wh_total'] / 1000
    total_oemof_baseline = oemof_baseline['wh_total'] / 1000
    total_hal_dec = hal_dec['wh_total'] / 1000
    total_oemof_dec = oemof_dec['wh_total'] / 1000

    return total_hal_baseline, total_oemof_baseline, total_hal_dec, total_oemof_dec


if __name__ == "__main__":
    real_data_net_import_analysis()
