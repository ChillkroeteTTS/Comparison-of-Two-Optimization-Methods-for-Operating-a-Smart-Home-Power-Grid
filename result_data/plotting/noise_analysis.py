import os
import re
from pathlib import Path
import matplotlib.pyplot as plt
from pandas import DataFrame

from plotting.hal_data_processing import hal_load_import_kwh, load_hal_storage_df
from plotting.oemof_data_processing import load_oemof_costs
from plotting.plot_run import get_oemof_results, to_percentiles, params_from_hal_path, params_from_oemof_path

base_path = Path.cwd() / 'result_data' / 'noise setup - sept 1w'
hal_dir = base_path / 'hal variance'
oemof_dir = base_path / 'oemof variance'

hal_dirs = [dir for dir in os.listdir(hal_dir) if re.search('_([0-9\.]+)_([0-9\.]+)_([0-9])+$', dir) is not None]
oemof_file_names = [file_name for file_name in os.listdir(oemof_dir) if re.search('_([0-9\.]+)_([0-9\.]+)_([0-9])+.oemof', file_name) is not None]

oemof_control_results = get_oemof_results(base_path, 'ensemble_control.oemof', exclude_storage=True)

hal_costs = [(dir, hal_load_import_kwh(hal_dir / dir, dir)['wh'].sum() / 1000) for dir in hal_dirs]
hal_costs_by_param, hal_mean, hal_percentiles = to_percentiles(hal_costs, params_from_hal_path)

oemof_costs = [(file_name, load_oemof_costs(get_oemof_results(oemof_dir, file_name, exclude_storage=True))['wh'].sum() / 1000)
               for file_name in oemof_file_names]
oemof_costs_by_param, oemof_mean, oemof_percentiles = to_percentiles(oemof_costs, params_from_oemof_path)

stds = [t[1] for t in hal_costs_by_param.keys()]

fig, axes = plt.subplots(1, 1)
axes.fill_between(stds, hal_percentiles[0], hal_percentiles[1], alpha=0.4)
axes.plot(stds, hal_mean, 'x-')
axes.fill_between(stds, oemof_percentiles[0], oemof_percentiles[1], alpha=0.4)
axes.plot(stds, oemof_mean, 'x-')
axes.set_xlabel('$\sigma$')
axes.set_ylabel('KWh')
axes.legend(['HAL controlled', 'schedule controlled'])

fig.subplots_adjust(left=0.12, right=0.97, top=0.92, bottom=0.11, hspace=0.38)
plt.savefig("praktikumsbericht/images/noiseTotalNet.pdf")

hal_stor_load = load_hal_storage_df(hal_dir / 'ensemble_30_2000.0_0', 'ensemble_30_2000.0_0')[0]['power[W]']
oemof_results = get_oemof_results(oemof_dir, 'ensemble_30_2000.0_0.oemof', exclude_storage=True)
oemof_stor_load = oemof_results['b1_data'][(('b1', 'sink_storage'), 'flow')] - oemof_results['b1_data'][(('source_storage', 'b1'), 'flow')]
pv = oemof_results['b1_data'][(('source_pv', 'b1'), 'flow')]

pl = DataFrame({
    'Storage Consumption HAL': hal_stor_load,
    'Storage Consumption OEMOF': oemof_stor_load,
    'Noise Induced PV Output': pv,
}, index=oemof_results['b1_data'].index)["2016-09-01"]
cov = pl.cov()
print(cov)
fig, axes = plt.subplots(1, 1)
pl.plot(ax=axes).set_ylabel('W')
fig.subplots_adjust(left=0.12, right=0.98, top=0.93, bottom=0.11, hspace=0.38)
plt.savefig("praktikumsbericht/images/noiseExample.pdf")

# pl2 = DataFrame({
#     'Storage Consumption HAL': pv - hal_stor_load,
#     'Storage Consumption OEMOF': pv - oemof_stor_load,
# }, index=oemof_results['b1_data'].index)
# pl2.plot(title='$\tau =30$, $\sigma =2000$ Difference to PV Output').set_ylabel('W')

# plt.show()
