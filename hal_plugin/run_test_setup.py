from hal_plugin.plotting.plot_run import plot_results
from hal_plugin.src.system import setup_sys_path
from hal_plugin.run_presets import run_simulation

if __name__ == "__main__":
    setup_sys_path()

    # generate data
    day = 60 * 24
    week = day * 7
    month = week * 4
    no_of_datapoints = day

    # run_simulation(['2016-12-01', '2016-12-02'],
    #                'hal_plugin/data/ol_data_pv_az180_inc36_mod23.csv',
    #                'hal_plugin/data/sh_intensity=15_area=46.5.csv',
    #                f"test_run",
    #                'test_run.oemof')

    plot_results(hal_sim_name='test_run', oemof_file='test_run.oemof')
