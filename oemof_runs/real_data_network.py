from pathlib import Path

import oemof.solph as solph
from oemof.outputlib import processing
from oemof.tools import logger
import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt

from oemof_runs.plot import plot_oemof_results

logger.define_logging(logfile='simple_network.log',
                      screen_level=logging.INFO,
                      file_level=logging.DEBUG)

date_time_index = pd.date_range('1/1/2012', periods=60*24,
                                freq='min')

logging.info('Create oemof objects')

es = solph.EnergySystem(timeindex=date_time_index)

b1 = solph.Bus(label="b1")
es.add(b1)

# sources
es.add(solph.Source(label='source_pv',
                    outputs={b1: solph.Flow(actual_value=pd.read_csv('data/hal_pv_data_1day.csv')['power[W]'],
                                            nominal_value=1,
                                            fixed=True,
                                            # min=0.3,
                                            variable_costs=0)}))

es.add(solph.Source(label='source_import',
                    outputs={b1: solph.Flow(variable_costs=1)}))


# sinks
es.add(solph.Sink(label='sink1_household', inputs={b1: solph.Flow(actual_value=pd.read_csv(
    'data/hal_load_data_1day.csv')['power[W]'],
                                                                  nominal_value=1,
                                                                  fixed=True)}))
es.add(solph.Sink(label='sink2_excess', inputs={b1: solph.Flow()}))

# storage
p_max = 3000
eta = 0.95
storage = solph.components.GenericStorage(
    nominal_storage_capacity=4000,
    initial_storage_level=0.5,
    inflow_conversion_factor=eta,
    outflow_conversion_factor=eta,
    label='storage',
    inputs={b1: solph.Flow(nominal_value=p_max)},
    outputs={b1: solph.Flow(nominal_value=p_max)}
)

es.add(storage)

# solving

om = solph.Model(es)
logging.info('Build model')
om.solve(solver='cbc')
logging.info('Solved model')

# debug equations should be used with 3 timesteps to have a readable file
# om.write('./equations.lp', io_options={'symbolic_solver_labels': True})

es.results['main'] = processing.results(om)
es.results['meta'] = processing.meta_results(om)

es.dump('results', 'my_dump.oemof')

plot_oemof_results(Path.cwd() / 'results', 'my_dump.oemof')
plt.show()
