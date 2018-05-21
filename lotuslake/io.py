"""
IO
===

    Functions to read and write the data from the lotus lake and other
disorganised collections of lotus simulations.

* get_simulation_directories
* create_lake_df

"""

import os
import pandas as pd
import numpy as np

def get_simulation_directories(lake_path, data_file='fort.9'):
    """
        Loop through all available directories and return those where
    the datafile is found.
    """
    cwd = os.getcwd()
    all_dirs = os.listdir(lake_path)
    all_dirs = [d for d in all_dirs if d[0] != '.'] #remove hidden files or directories
    simulation_dirs = []
    for d in all_dirs:
        simulation_files = os.listdir(lake_path + '/' + d)
        if data_file in simulation_files:
            #print('fort.9 in {0}'.format(d))
            simulation_dirs.append(d)
            pass
        else:
            pass
    return simulation_dirs

def create_lake_df(lake_dict, parameters_key, variables_key):
    """
        LotusLakes can be used to study variations in parameters in order to
    understand their effect in some variables of interest.
        Turns a lake_metadata dict into an empty dataframe based on the sub-keys
    under the supplied paramaters and variables keys.
    """
    col_names = {**lake_dict[parameters_key], **lake_dict[variables_key]}
    sim_no = lake_dict['simulation_number']
    df = pd.DataFrame(np.ones([sim_no, len(col_names)]), columns=col_names)
    return df
