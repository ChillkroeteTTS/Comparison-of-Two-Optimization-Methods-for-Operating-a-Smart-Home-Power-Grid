from pathlib import Path

from pandas import DataFrame

from plotting.hal_data_processing import hal_load_import_kwh
from plotting.oemof_data_processing import load_oemof_costs
from plotting.plot_run import get_oemof_split_results, get_oemof_results
import matplotlib.pyplot as plt
import pandas as pd


def get_imports(oemof_dir, oemof_file, hal_dir, hal_sim_name, split_max=None):

    if split_max is not None:
        oemof_results = get_oemof_split_results(oemof_dir, split_max)
    else:
        oemof_results = get_oemof_results(oemof_dir, oemof_file, exclude_storage=True)

    hal_import = hal_load_import_kwh(hal_dir, hal_sim_name)
    oemof_import = load_oemof_costs(oemof_results)

    return oemof_import, hal_import

def peak_max_and_frequency(oemof_dir, oemof_file, hal_dir, hal_sim_name):
    oemof, hal = get_imports(oemof_dir, oemof_file, hal_dir, hal_sim_name)


def net_import_analysis(oemof_dir, oemof_file, hal_dir, hal_sim_name,
                        hal_label='hal_total_import', oemof_label='oemof_total_import'):
    oemof, hal = get_imports(oemof_dir, oemof_file, hal_dir, hal_sim_name)
    fig, axes = plt.subplots(nrows=2)
    total_hal = hal['wh_total'] / 1000
    total_oemof = oemof['wh_total'] / 1000
    mixed_costs = pd.DataFrame({
        hal_label: total_hal,
        'oemof_total_import': total_oemof,
    },
        index=oemof.index)
    mixed_costs.cumsum().plot(title='Cummulated Imported KWh', ax=axes[0])
    mixed_costs.sum().plot.bar(title='Total KWh comparison', ax=axes[1], grid=True)


def dataframe_to_stat_table(file_path: Path, df: DataFrame):
    calc_stats = lambda ts: ['{:3f}'.format(v) for v in [ts.min(), ts.max(), ts.mean(), ts.median(), ts.std(), ts.var(), ts.sum()]]

    with open(str(file_path), 'w+') as f:
        f.write('time series,min,max,mean,median,std,var,sum\n')
        stats = [ [column] + calc_stats(df[column]) for column in df]
        f.writelines([','.join(column_stats) + '\n' for column_stats in stats])
