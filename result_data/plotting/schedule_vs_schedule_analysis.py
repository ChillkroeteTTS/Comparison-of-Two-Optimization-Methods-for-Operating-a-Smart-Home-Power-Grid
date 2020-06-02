from pathlib import Path

from pandas import DataFrame

from plotting.hal_data_processing import hal_load_import_kwh, load_hal_storage_df
from plotting.oemof_data_processing import load_oemof_costs
from plotting.plot_run import get_oemof_split_results, get_oemof_results
import matplotlib.pyplot as plt
import pandas as pd

from result_data.plotting.final_plots import dataframe_to_stat_table


def real_data_net_import_analysis():
    base_path = Path().cwd() / 'result_data'
    sept_setup_path = base_path / 'schedule vs schedule - sept'

    oemof_baseline = load_oemof_costs(get_oemof_results(sept_setup_path, 'baseline_pred.oemof', True))
    hal_baseline = hal_load_import_kwh(sept_setup_path / 'baseline_pred', 'baseline_pred')

    oemof_sept = load_oemof_costs(get_oemof_results(sept_setup_path, 'oemof_offline.oemof', True))
    hal_sept = load_oemof_costs(get_oemof_results(sept_setup_path, 'hal_offline.oemof', True))

    total_hal_baseline = hal_baseline['wh_total'] / 1000
    total_oemof_baseline = oemof_baseline['wh_total'] / 1000
    total_hal_sept = hal_sept['wh_total'] / 1000
    total_oemof_sept = oemof_sept['wh_total'] / 1000

    mixed_costs = pd.DataFrame({
        'Pred HAL': total_hal_baseline,
        'Pred OEMOF': total_oemof_baseline,
        'Real HAL': total_hal_sept,
        'Real OEMOF': total_oemof_sept,
    }, index=total_oemof_baseline.index)

    fig, axes = plt.subplots(nrows=1)

    summed_mixed_costs = mixed_costs.sum()
    summed_mixed_costs.plot.bar(ax=axes, grid=True).set_ylabel('KWh')
    fig.subplots_adjust(left=0.12, right=0.97, top=0.92, bottom=0.19, hspace=0.53)
    plt.savefig("praktikumsbericht/images/sept_svss_total.pdf")
    dataframe_to_stat_table(sept_setup_path / 'stats.csv', mixed_costs)
    summed_mixed_costs.to_latex(open("praktikumsbericht/images/schedule_vs_schedule.tex", 'w'),
                                label='t/res/schedule',
                                header=['sum'],
                                caption='Sum of all simulation runs net imports.',
                                float_format="%.2f")

    hal_results = get_oemof_results(sept_setup_path, 'hal_offline.oemof', exclude_storage=True)
    hal_stor_load = hal_results['b1_data'][(('b1', 'sink_storage'), 'flow')] - hal_results['b1_data'][
        (('source_storage', 'b1'), 'flow')]
    pred_oemof_results = get_oemof_results(sept_setup_path, 'baseline_pred.oemof', exclude_storage=True)
    real_oemof_results = get_oemof_results(sept_setup_path, 'oemof_offline.oemof', exclude_storage=True)
    oemof_stor_load = real_oemof_results['b1_data'][(('b1', 'sink_storage'), 'flow')] - real_oemof_results['b1_data'][
        (('source_storage', 'b1'), 'flow')]
    pv_pred = pred_oemof_results['b1_data'][(('source_pv', 'b1'), 'flow')]
    pv_real = real_oemof_results['b1_data'][(('source_pv', 'b1'), 'flow')]

    pl = DataFrame({
        'HAL controlled Storage Balance': hal_stor_load,
        'Oemof controlled Storage Balance': oemof_stor_load,
        'Pred PV Output': pv_pred,
        'Actual PV Output': pv_real,
    }, index=real_oemof_results['b1_data'].index)
    corr = pl.corr()
    print(corr.to_latex(
        label='t/res/real',
        header=['HAL', 'Schedule', 'Pred PV', 'Actual PV'],
        caption='Correlation between PV input and storage consumption',
        float_format="%.2f"))
    fig, axes = plt.subplots(nrows=1)
    pl["2016-09-01"].plot(ax=axes)
    # plt.savefig("praktikumsbericht/images/sept_svss_example.pdf")

    # Percentiles
    fig, axes = plt.subplots(nrows=1)
    boxplot = mixed_costs.boxplot(grid=True, showfliers=False, ax=axes)
    boxplot.set_ylabel('KWh')
    fig.subplots_adjust(left=0.12, right=0.96, top=0.93, bottom=0.07, hspace=0.20)
    plt.savefig("praktikumsbericht/images/sept_svss_peaks.pdf")

    dataframe_to_stat_table(sept_setup_path / 'stats.csv', mixed_costs)
    # plt.show()


if __name__ == "__main__":
    real_data_net_import_analysis()
