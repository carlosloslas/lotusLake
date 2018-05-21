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
    import lotuslake

    cwd = os.getcwd()
    lake_path = cwd + '/gStarStudy_64ppd_re100'

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
        plt.close()
        plt.close()

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

    lake_simulations = lotuslake.get_simulation_directories(lake_path)

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


    lake_df = lotuslake.create_lake_df(
        lotus_lake_parameters, 'simulation_parameters', 'study_parameters'
        )

    lake_list = []

    for i, s in enumerate(lake_simulations[:]):
        print(s)
        s_dir = '{0}/{1}'.format(lake_path, s)
        s_metadata = parse_simulation_name(s)
        lift_stats, drag_stats = postproc_lotus_simulation(s_dir)

        s_data = [s_metadata['d'], s_metadata['g'], lift_stats['mad'], drag_stats['mean']]
        lake_df.iloc[i] = s_data

    fig, ax = lotuslake.plot_lake_df(lake_df, 'gap', 'lift_mad', group_param='dimensions')
    plt.savefig(lotus_lake_parameters['project_name'])
