import functools
import os

import pandas as pd


def hal_load_import_kwh(result_dir, sim_name):
    df = load_hal_b1_df(result_dir, sim_name)
    df_h = load_hal_p2h_df(result_dir, sim_name)
    df['res_power[W]'] = df['res_power[W]'].clip(0)
    df['wh'] = df['res_power[W]'] * 60 / 3600
    df['wh (heat)'] = df_h['local_res_power'] * 60 / 3600
    df['wh_total'] = df_h['local_res_power'] * 60 / 3600 + df['res_power[W]'] * 60 / 3600
    return df


def load_hal_b1_df(result_dir, sim_name):
    # positive values indicate that power flows INTO the system, negative that power flows OUT of the system
    return pd.read_csv(result_dir / f"{sim_name}__noSpec__connection__b1.csv", index_col='t_begin', parse_dates=True)

def load_hal_p2h_df(result_dir, sim_name):
    # positive values indicate that power flows INTO the system, negative that power flows OUT of the system
    return pd.read_csv(result_dir / f"{sim_name}__noSpec__transformer__p2h.csv.csv", index_col='t_begin', parse_dates=True)


def plot_hal_b1_load_his(result_dir, sim_name):
    data = load_hal_b1_df(result_dir, sim_name)[['res_power[W]']]
    data.plot.hist(bins=100)


def load_hal_storage_df(result_dir, sim_name):
    return pd.read_csv(result_dir / f"{sim_name}__noSpec__battery__storage.csv", index_col='t_begin', parse_dates=True), \
           pd.read_csv(result_dir / f"{sim_name}__noSpec__battery__heat_storage.csv", index_col='t_begin',
                       parse_dates=True)



def load_all_hal_results(result_dir):
    def get_name(str):
        return str.split('__noSpec__')[1].split('.')[0]

    def item_2_main_metric_df(item):
        cmp_to_main_metric = {
            'battery': 'soc begin[%]',
            'connection': 'res_power[W]',
            'sink': 'power_schedule[W]',
            'source': 'power_schedule[W]',
            'transformer': 'consumed_power[W]',
        }
        id, df = item

        cmp_key = [k for k in cmp_to_main_metric.keys() if k in id]
        print(id)
        if len(cmp_key) > 0:
            main_metric = cmp_to_main_metric[cmp_key[0]]
            df_main_metric = df[[main_metric]]
            df_main_metric.rename({'soc begin[%]': f"{id} SOC%",
                                   'res_power[W]': f"{id}[W]",
                                   'consumed_power[W]': f"{id}[W]",
                                   'power_schedule[W]': f"{id}[W]",
                                   }, inplace=True, axis='columns')
            return df_main_metric
        else:
            return None

    df_dict = {get_name(path): pd.read_csv(result_dir / path, index_col='t_begin', parse_dates=True) for path in
               os.listdir(result_dir)}

    dfs = list([item_2_main_metric_df(item) for item in df_dict.items() if item_2_main_metric_df(item) is not None])
    return functools.reduce(lambda agg, df: agg.merge(df, on='t_begin'), dfs)


def load_hal_p2h_df(result_dir, sim_name):
    return pd.read_csv(result_dir / f"{sim_name}__noSpec__transformer__p2h.csv", index_col='t_begin', parse_dates=True)
