import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from plotting.oemof_data_processing import load_oemof_costs
from plotting.plot_run import plot_results, get_oemof_results
from run_presets import run_simulation, run_both_with_existing_schedule


def run_schedule_by_schedule_comparison(time_range, predicted_pv_data_path, real_pv_data_path):
    control_sim_name = f"baseline_pred"
    control_oemof_file_name = 'baseline_pred.oemof'
    run_simulation(time_range, predicted_pv_data_path, 'hal_plugin/data/sh_intensity=15_area=46.5.csv',
                   control_sim_name, control_oemof_file_name)

    hal_schedule_file_name = 'hal_offline'
    oemoef_schedule_file_name = 'oemof_offline'
    run_both_with_existing_schedule(control_oemof_file_name, control_sim_name, time_range, real_pv_data_path,
                                    hal_schedule_file_name,
                                    oemoef_schedule_file_name)

    # plot control
    plot_results(control_sim_name, oemof_file=control_oemof_file_name, show=False)

    # plot schedule sim
    oemof_dir = Path.cwd() / 'oemof_runs' / 'results'
    hal_scheduled_results = get_oemof_results(oemof_dir, hal_schedule_file_name, exclude_storage=True)
    oemof_scheduled_results = get_oemof_results(oemof_dir, oemoef_schedule_file_name, exclude_storage=True)

    oemof_schedule_costs = load_oemof_costs(oemof_scheduled_results)
    hal_schedule_costs = load_oemof_costs(hal_scheduled_results)

    fig, axes = plt.subplots(nrows=3)
    mixed_costs = pd.DataFrame({'hal_KWh': hal_schedule_costs['wh'] / 1000, 'oemof_KWh': oemof_schedule_costs['wh'] / 1000,
                                'KWh_diff': oemof_schedule_costs['wh'] / 1000 - hal_schedule_costs['wh'] / 1000},
                               index=oemof_schedule_costs.index)
    mixed_costs.plot(title=f"Imported KWh", ax=axes[0])
    mixed_costs.cumsum().plot(title='Cummulated Imported KWh', ax=axes[1])
    mixed_costs.sum().plot.bar(title='Total KWh Comparison', ax=axes[2], grid=True)

    plt.show()



if __name__ == "__main__":
    run_schedule_by_schedule_comparison(['2016-09-01', '2016-10-01'],
                                        'hal_plugin/data/2016_pred_res60s_7days_train_full.csv',
                                        'hal_plugin/data/2016_real_res60s_7days_train_full.csv')
