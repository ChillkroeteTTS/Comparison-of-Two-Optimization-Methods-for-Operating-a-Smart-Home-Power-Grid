import oemof.solph as solph
from oemof.outputlib import processing
from oemof.tools import logger
import pandas as pd
import numpy as np
import logging

from oemof.plot import basic_plot_from_saved_model

logger.define_logging(logfile='simple_network.log',
                      screen_level=logging.INFO,
                      file_level=logging.DEBUG)

date_time_index = pd.date_range('1/1/2012', periods=24 * 7 * 2,
                                freq='H')

logging.info('Create oemof objects')

es = solph.EnergySystem(timeindex=date_time_index)

b1 = solph.Bus(label="b1")
es.add(b1)

# sources
sin_values = (np.sin([i * ((np.pi * 2 * 2) / (24 * 7 * 2)) + 1 for i, x in enumerate(date_time_index)]) + 1) / 2
es.add(solph.Source(label='source_pv',
                    outputs={b1: solph.Flow(actual_value=sin_values,
                                            nominal_value=10e5,
                                            fixed=True,
                                            # min=0.3,
                                            variable_costs=25)}))


# sinks
es.add(solph.Sink(label='sink1', inputs={b1: solph.Flow(actual_value=1, nominal_value=10e5*0.4, fixed=True)}))
es.add(solph.Sink(label='sink2_excess', inputs={b1: solph.Flow()}))

# storage
storage = solph.components.GenericStorage(
    nominal_storage_capacity=10e10,
    initial_storage_level=0,
    label='storage',
    inputs={b1: solph.Flow(nominal_value=10e6)},
    outputs={b1: solph.Flow(nominal_value=10e6, variable_costs=0.001)}
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

basic_plot_from_saved_model()
