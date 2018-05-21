"""
Vis
===

    Functions to visualize the results from the lotus lake.

* plot_lake_df

"""

import matplotlib.pyplot as plt

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
