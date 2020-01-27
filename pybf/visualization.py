"""
   Copyright (C) 2020 ETH Zurich. All rights reserved.

   Author: Sergei Vostrikov, ETH Zurich

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import matplotlib
matplotlib.use('TKAgg')
from matplotlib import colors, cm, pyplot as plt

import plotly as py
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"

import numpy as np

# Constants
PLOTLY_SCALE_FACTOR = 2

# Log compression
def log_compress(image, db_range):

    db_range = abs(db_range)

    # Calc max value
    max_value = image.max()

    # Log scale transform
    image_log = 20 * np.log10(image/max_value)

    # Truncate
    image_log[image_log < (-db_range)] = -db_range

    print("BF Final dB range ({:2.1f},{:2.1f})".format(image_log.min(),
                                                        image_log.max()))
    return image_log

# Plot one trace
def plot_trace(rf_data, 
               channel=None, 
               framework='matplotlib', 
               save_fig=False, 
               show=True,
               path_to_save=None):

    # Check path for the image image
    if path_to_save is None:
        path_to_save = ''
    else:
        path_to_save = path_to_save + '/'

    # Select data
    if channel is not None:
        data = rf_data[:, channel]
        title = "Data from channel " + str(channel)
    else:
        data = rf_data
        title = " "

    # Choose framework
    if framework is 'matplotlib':

        fig, ax = plt.subplots(1, 1,figsize=(10,10))

        ax.plot(data, marker="o")
        ax.grid(True)

        ax.set_xlabel("Samples")
        ax.set_ylabel("Signal")
        ax.set_title(title)

        if show is True:
            plt.show()

        if save_fig is True:
            fig.savefig(path_to_save + title + '.png', 
                        dpi=300, 
                        bbox_inches='tight')

    elif framework is 'plotly':

        # Create plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=data,
                                 mode='lines+markers',
                                 name='lines'))

        # Edit the layout
        fig.update_layout(title=title,
                          xaxis_title='Samples',
                          yaxis_title='Signal')
        if show is True:
            fig.show()

        if save_fig is True:
            fig.write_image(path_to_save + title + '.png')
    return

# Plot image
def plot_image(img_data, 
               scatters_coords_xz=None,
               elements_coords_xz=None,
               framework='matplotlib',
               title=None,
               image_x_range=None,
               image_z_range=None,
               db_range=None,
               colorscale='Greys',
               save_fig=False, 
               show=True,
               path_to_save=None):

    # Check path for to save images
    if path_to_save is None:
        path_to_save = ''
    else:
        path_to_save = path_to_save + '/'

    # Set title
    if title is None:
        title='Image'

    # Make log compression
    if db_range is not None:
        data=log_compress(img_data, db_range)
        # Update title
        title = title + ' (dB scale)'
    else:
        data=img_data

    # Choose framework
    if framework is 'matplotlib':

        fig, ax = plt.subplots(1, 1,figsize=(10,10))

        # Plot scatters
        if scatters_coords_xz is not None:
            ax.scatter(scatters_coords_xz[0,:], 
                       scatters_coords_xz[1,:], 
                       color = 'red', 
                       s=5, 
                       label='scatters')

        # Plot transducer elements
        if elements_coords_xz is not None:
            ax.scatter(elements_coords_xz[0,:], 
                       elements_coords_xz[1,:], 
                       color = 'green', 
                       marker="v", 
                       s=80,
                       label='elements')

        # Plot image
        if (image_x_range is not None) and (image_z_range is not None):

            ax.imshow(data, 
                      cmap=cm.gray, 
                      origin="lower", 
                      extent=image_x_range+image_z_range)
        else:
            ax.imshow(data, 
                      cmap=cm.gray, 
                      origin="lower")

        ax.set_xlabel("X, m")
        ax.set_ylabel("Z, m")
        ax.set_title(title)

        ax.invert_yaxis()
        ax.legend()

        if show is True:
            plt.show()

        if save_fig is True:
            fig.savefig(path_to_save + title + '.png', 
                        dpi=300, 
                        bbox_inches='tight')

    elif framework is 'plotly':

        # Create plot
        if (image_x_range is not None) and (image_z_range is not None):

            # Calculate points coordinates
            x_coords = np.linspace(image_x_range[0], image_x_range[1], data.shape[1])
            z_coords = np.linspace(image_z_range[0], image_z_range[1], data.shape[0])

            fig = go.Figure(data=go.Heatmap(
                            z=data,
                            x=np.unique(x_coords),
                            y=np.unique(z_coords),
                            hoverongaps = False,
                            colorscale=colorscale,
                            reversescale=True))
        else:

            fig = go.Figure(data=go.Heatmap(
                            z=data,
                            hoverongaps = False,
                            colorscale=colorscale))        

        # Plot scatters
        if scatters_coords_xz is not None:
            fig.add_trace(go.Scatter(x=scatters_coords_xz[0,:], 
                                     y=scatters_coords_xz[1,:], 
                                     mode='markers',
                                     marker=dict(
                                         color='red',
                                         size=3),
                                     name="scatters"
                                     ))

        # Plot transducer elements
        if elements_coords_xz is not None:
            fig.add_trace(go.Scatter(x=elements_coords_xz[0,:], 
                                     y=elements_coords_xz[1,:], 
                                     mode='markers',
                                     marker=dict(
                                         color='green',
                                         size=3),
                                     name="elements"
                                     ))


        # Edit the layout
        fig.update_layout(
            scene=dict(aspectmode="data"),
            title=title,
            xaxis_title='X, m',
            yaxis_title='Z, m',
            yaxis=dict(scaleanchor="x", 
                       scaleratio=1,
                       range=[image_z_range[0], image_z_range[1]]),
            xaxis=dict(range=[image_x_range[0], image_x_range[1]]),
            showlegend=True,
            legend=dict(x=1, y=1.1)
        )

        fig.update_yaxes(autorange="reversed")

        if show is True:
            fig.show()

        if save_fig is True:
            fig.write_image(path_to_save + title + '.png', scale = PLOTLY_SCALE_FACTOR)
    return