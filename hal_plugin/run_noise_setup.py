import time
from pathlib import Path

import numpy as np
import pandas as pd
from pandas import DataFrame

from data.create_test_data import create_test_data
from plotting.plot_run import plot_ensemble_results
from run_presets import run_simulation, run_with_existing_schedule
from run_test_setup import setup_sys_path


def red_noise(pv_data: DataFrame, tau, std):
    dp = len(pv_data)
    ip_max = np.max(pv_data)
    print(ip_max)
    a = np.zeros(dp)
    for i in range(1, dp):
        prev_x = a[i - 1]
        delta_t = 1
        x = prev_x + delta_t * (-prev_x / tau) + np.sqrt(2 / tau) * np.sqrt(delta_t) * std * np.random.normal(0,
                                                                                                              delta_t)
        a[i] = x
    return a


def run_altered_pv(time_range, pv_data_path: str, oemof_control_file_name, tau=30, std=1000, i=0):
    paths = create_test_data(time_range, plot=False, pv_data_path=pv_data_path)
    pv_data = pd.read_csv(paths['pv_data'], parse_dates=True, index_col=0)

    noise = red_noise(pv_data, tau, std)
    # plt.plot(noise)
    # plt.show()

    pv_data['power[W]'] = pv_data['power[W]'] + noise
    modified_pv = pv_data.clip_lower(0)
    modified_pv_path = '/'.join(pv_data_path.split('/')[:-1]) + '/noised_pv_data.csv'
    modified_pv.to_csv(modified_pv_path)

    oemof_file_name = f"ensemble_{tau}_{std}_{i}.oemof"
    hal_sim_name = f"ensemble_{tau}_{std}_{i}"

    run_with_existing_schedule(oemof_control_file_name, time_range, modified_pv_path, hal_sim_name,
                               oemof_file_name)

    # plot_results(show=False)
    # plot_results(oemof_file=oemof_file_name, hal_sim_name=hal_sim_name)


def run_altered_pv_ensemble(time_range, pv_data_path, oemof_control_file_name, tau=30, std=1000, ensemble_number=10):
    for i in range(0, ensemble_number):
        run_altered_pv(time_range, pv_data_path, oemof_control_file_name, tau, std, i)


def altered_pv_ensemble_entry(time_range):
    # IMPRTANT! MANUALLY DELETE ALL PREVIOUS RESULT FILES
    start = time.time()
    setup_sys_path()

    oemo_file_name_control = 'ensemble_control.oemof'
    control_sim_name = f"ensemble_control"

    pv_data_path = 'hal_plugin/data/ol_data_pv_az180_inc36_mod23.csv'
    # basline simulation
    run_simulation(time_range,
                   pv_data_path,
                   'hal_plugin/data/sh_intensity=15_area=46.5.csv',
                   control_sim_name,
                   oemo_file_name_control)

    # std \in [100, 2000]
    for factor in np.linspace(0.1, 2, 5):
        run_altered_pv_ensemble(time_range, pv_data_path, oemo_file_name_control, tau=30, std=1000 * factor, ensemble_number=10)

    end = time.time()
    print(f"took me {(end - start) / (60 * 60)}h to finish simulation")
    hal_dir = Path.cwd() / 'hal' / 'sim_results'
    plot_ensemble_results(hal_dir, control_sim_name, 'ensemble_', Path.cwd() / 'oemof_runs' / 'results',
                          oemo_file_name_control, 'ensemble_')

if __name__ == "__main__":
    # std \in [100, 2000]
    # T = 01.09 - 09.09 for computational feasibility
    # ensemble = 10
    altered_pv_ensemble_entry(['2016-09-01', '2016-09-08'])
