#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Developement file for lotusLake

Created on Sun May  6 11:23:56 2018

@author: closadalastra
"""
import lotusstat
import pandas as pd
import os

def create_lake_df(lake_params, key):
    """
        LotusLakes can be used to study variations in different kinds 
    of parameters.
        Turns a lake_params dict into an empty dataframe based on the sub-keys
    under the supplied key.
    """
    return pd.DataFrame(names=lake_params[key].keys())

def get_simulation_directories(lake_path):
    cwd = os.getcwd()
    all_files = os.listdir(cwd + lake_path)
    

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
    
    lake_path = '/gStarStudy_64ppd_re100'
    
    def postproc_lotus_simulation(simulation_dir):
        """
        """
        data_file = 'fort.9'
        data_df = lotusstat.convert_data_path_to_dataFrame_3d(data_file)
        data_df = lotusstat.data_df.iloc[0:,:]
        
        data_df = lotusstat.calculate_total_forces(data_df)
        
        lift_stats = lotusstat.calculate_signal_stats(data_df, 'totalForceY', signal_range=(0.8, 1))
        drag_stats = lotusstat.calculate_signal_stats(data_df, 'totalForceX', signal_range=(0.8, 1))
        
        #no need to plot the specific simulation resultsss
        #lotusstat.plot_lift_signal(data_df, show_visc=True, plot_stats=True, stats=lift_stats, show_stats=True, figsize=(10,5))
        #lotusstat.plot_drag_signal(data_df, plot_stats=True, stats=drag_stats, show_stats=True, figsize=(10,5))
        
        return lift_stats, drag_stats
    
    def parse_simulation_name(name):
        """
            Takes a simulation name and returns the simulation parameters as a 
        dictionary of keys and values
        """
        import re
        parameters = name.split('_')
        keys = [re.sub("[0-9, .]", "", p) for p in parameters]
        values = [re.sub("[a-z]", "", p) for p in parameters]
        
        return dict(zip(keys, values))
    
    lotus_lake_parameters = {
            'project_name' : 'Circlar cylinder array gap study',
            'grid_props' : {
                    'ppd' : 64
                    },
            'simulation_parameters' : {
                    'dimensions' : 'd',
                    'gap' : 'g'
                    }
            }
    lake_df = create_lake_df(lotus_lake_parameters, 'simulation_parameters')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    