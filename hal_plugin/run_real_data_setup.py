from pathlib import Path

from plotting.plot_run import plot_results, output_result_table
from run_presets import run_simulation, run_with_existing_schedule
from run_test_setup import setup_sys_path


def run_generated_schedule(time_range, pv_path_first_run, pv_path_second_run):
    setup_sys_path()

    run_simulation(time_range, pv_path_first_run, 'hal_plugin/data/sh_intensity=15_area=46.5.csv', f"baseline_pred",
                   'baseline_pred.oemof')
    run_with_existing_schedule('baseline_pred.oemof', time_range, pv_path_second_run, 'real_data_online',
                               'real_data_offline.oemof')

    plot_results('baseline_pred', oemof_file='baseline_pred.oemof', show=False)
    plot_results('real_data_online', oemof_file='real_data_offline.oemof', show=True, skip_storage=True)


if __name__ == "__main__":
    run_generated_schedule(['2016-11-01', '2016-12-01'], # exclusive
                           'hal_plugin/data/2016_pred_res60s_7days_train_full.csv',
                           'hal_plugin/data/2016_real_res60s_7days_train_full.csv')
    # output_result_table(Path.cwd() / 'result_data',
    #                     'baseline_pred', 'real_data_online',
    #                     'baseline_pred', 'real_data_schedule',
    #                     'first_run.oemof', 'first_run',
    #                     'scheduled_run.oemof', 'scheduled_run')
