#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Developement file for lotusLake

Created on Sun May  6 11:23:56 2018

@author: closadalastra
"""
import lotusstat
import numpy as np
import pandas as pd
import os

import matplotlib.pyplot as plt

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

def get_simulation_directories(lake_path, data_file='fort.9'):
    """
        Loop through all available directories and return those where
    the datafile is found.
    """
    cwd = os.getcwd()
    all_dirs = os.listdir(cwd + lake_path)
    all_dirs = [d for d in all_dirs if d[0] != '.'] #remove hidden files or directories
    simulation_dirs = []
    for d in all_dirs:
        simulation_files = os.listdir(cwd + lake_path + '/' + d)
        if data_file in simulation_files:
            #print('fort.9 in {0}'.format(d))
            simulation_dirs.append(d)
            pass
        else:
            pass
    return simulation_dirs

def plot_lake_df(lake_df, x, y, group_param=None, subplots=False, fig_size=(8,6)):
    if group_param == None:
        assert subplots == False
        fig = plt.figure(figsize=fig_size)
        ax = plt.gca()
        lake_df.plot(x, y, ax=ax)
        ax.set(xlabel=x,
               ylabel=y
               )
    else:
        grouped_lake = lake_df.groupby(by=group_param)

        if subplots:
            fig, axs = plt.subplots(ncols=1, nrows=len(grouped_lake), figsize=fig_size)
            for ax, (g, df) in zip(axs, grouped_lake):
                df.plot(x, y, ax=ax)
                ax.set(xlabel=x,
                       ylabel=y,
                       title='{0} {1}'.format(group_param, g)
                       )
        else:
            fig, ax = plt.subplots(ncols=1, nrows=1, figsize=fig_size)
            for g, df in grouped_lake:
                df.plot(x, y, ax=ax, label=g)
            ax.set(xlabel=x,
                   ylabel=y,
                   title='{0} vs {1}, per {2}'.format(x, y, group_param)
                   )
    return fig, ax

if __name__ == '__main__':

    """
    Typically collections of Lotus simulations are used to gain insight into
    simulation or geometry permutations.
    This should help go through the results in a structured way. Proposed method bellow
    ---
    1. Build postproc function
    2. Create a lake dictionary with all of the metadata for the lotus simulations
    3. Crunch throught the simulation results with the postproc function
        1. Create a DataFrame from the simulation parameters in the 'lotus_lake_dict'
        2. Loop through the simulation files
            1. Obtain simulation metadata
            2. Post-process the simulation results
            3. Add results to the DataFrame organsied on the metadata
    4. Plot the results from the study
    """
    cwd = os.getcwd()
    lake_path = '/gStarStudy_64ppd_re100'

    def postproc_lotus_simulation(simulation_dir):
        """
        """
        data_file = 'fort.9'
        data_dir = '{0}/{1}'.format(simulation_dir, data_file)
        data_df = lotusstat.convert_data_path_to_dataFrame_3d(data_dir)
        data_df = data_df.iloc[100:,:]

        case_name = simulation_dir.split('/')[-1]

        data_df = lotusstat.calculate_total_forces(data_df)

        lift_stats = lotusstat.calculate_signal_stats(data_df, 'totalForceY', signal_range=(0.8, 1))
        drag_stats = lotusstat.calculate_signal_stats(data_df, 'totalForceX', signal_range=(0.8, 1))

        #no need to plot the specific simulation resultsss
        fig_l, ax_l = lotusstat.plot_lift_signal(data_df, show_visc=True, plot_stats=True, stats=lift_stats, show_stats=True, figsize=(10,5))
        fig_d, ax_d = lotusstat.plot_drag_signal(data_df, plot_stats=True, stats=drag_stats, show_stats=True, figsize=(10,5))

        lotusstat.save_figures_to_pdf([fig_l, fig_d], '{0}.pdf'.format(case_name))

        return lift_stats, drag_stats

    def parse_simulation_name(name):
        """
            Takes a simulation name and returns the simulation parameters as a
        dictionary of keys and values
        """
        import re
        parameters = name.split('_')
        keys = [re.sub("[0-9, .]", "", p) for p in parameters]
        values = [float(re.sub("[a-z]", "", p)) for p in parameters]

        return dict(zip(keys, values))

    lake_simulations = get_simulation_directories(lake_path)

    lotus_lake_parameters = {
            'project_name' : 'Circlar cylinder array gap study',
            'grid_props' : {
                    'ppd' : 64
                    },
            'simulation_number' : len(lake_simulations),
            'simulation_parameters' : {
                    'dimensions' : 'd',
                    'gap' : 'g'
                    },
            'study_parameters' : {
                    'lift_mad' : 'lMad',
                    'drag_mean' : 'dMean'
                    }
            }


    lake_df = create_lake_df(
        lotus_lake_parameters, 'simulation_parameters', 'study_parameters'
        )

    lake_list = []

    for i, s in enumerate(lake_simulations[:]):
        print(s)
        s_dir = '{0}{1}/{2}'.format(cwd, lake_path, s)
        s_metadata = parse_simulation_name(s)
        lift_stats, drag_stats = postproc_lotus_simulation(s_dir)

        s_data = [s_metadata['d'], s_metadata['g'], lift_stats['mad'], drag_stats['mean']]
        lake_df.iloc[i] = s_data

    fig, ax = plot_lake_df(lake_df, 'gap', 'lift_mad', group_param='dimensions')
    plt.savefig(lotus_lake_parameters['project_name'])
