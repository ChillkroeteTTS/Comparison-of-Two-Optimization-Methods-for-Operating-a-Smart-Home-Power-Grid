
def get_storage_data_from_saved_model(oemof_results):
    storage_data = oemof_results['storage']
    h_storage_data = oemof_results['heat_storage']

    return storage_data['sequences'], h_storage_data['sequences']


def get_b1_data_from_saved_model(oemof_results):
    b1_data = oemof_results['b1_data']

    return b1_data['sequences']


def plot_oemof_results(oemof_results):
    df = oemof_results['b1_data']
    df_h = oemof_results['b_h_data']

    # res_dict['storage_data'].plot(kind='line', drawstyle='steps-post', title='Oemof Power Battery Flows')
    res_dict = df.reindex(sorted(df.columns), axis=1)
    res_dict_h = df_h.reindex(sorted(df_h.columns), axis=1)
    res_dict.plot(kind='line', drawstyle='steps-post', title='Oemof Power Flow', subplots=True, sort_columns=True)
    res_dict_h.plot(kind='line', drawstyle='steps-post', title='Oemof Heat Flow', subplots=True, sort_columns=True)
