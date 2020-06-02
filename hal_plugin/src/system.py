import os
import sys
from pathlib import Path
import oemof.solph as solph


from oemof.outputlib import processing

from hal.src.congf_file_handling.in_memory_sim_config_navigation import InMemorySimConfigNavigation
from hal_plugin.src.es_to_hal_tree import es_to_hal_sim_cfg
from hal.src.simulation.sim_zmq import LocalZmqSim


def run_oemof(es, output_filename='my_dump.oemof'):
    print('run oemof simulation')
    om = solph.Model(es)
    om.solve(solver='cbc')
    print('optimization done, processing results')
    es.results['main'] = processing.results(om)
    es.results['meta'] = processing.meta_results(om)
    es.dump(str(Path.cwd() / 'oemof_runs' / 'results'), output_filename)
    print('oemof done')


def run_hal(es, sim_name='oemof_sim'):
    sim_dict = es_to_hal_sim_cfg(es, sim_name=sim_name)
    old_cwd = Path.cwd()
    os.chdir(str(old_cwd / 'hal' / 'src'))
    sim_obj = LocalZmqSim(InMemorySimConfigNavigation(sim_dict), show_live_graph=False)
    sim_obj.run_simulation()
    os.chdir(str(old_cwd))
    print('HAL simulation done, you have nothing to worry about')

def setup_sys_path():
    print(Path.cwd())
    print(os.getcwd())
    # super important to be able to run hal outside of its own context, otherwise "module not found"-errors will occur
    sys.path.append(str(Path.cwd() / 'hal'))
    sys.path.append(str(Path.cwd() / 'hal' / 'src'))
