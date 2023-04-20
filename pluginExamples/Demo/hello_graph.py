
#### Welcome ####

# Hello and welcome to Enlighten plugins.

# This demo plugin simply creates a copy of the default scope graph.

# Here we will cover a couple fundamental use-cases for plugins:
# (1) Getting the original graph's data
# (2) Displaying a custom chart

# Between these two steps is where the real magic happens.

# Once you have the data in the form of numpy arrays
# you may apply any transformation in Python and display
# the changes in a graph.

# To see how to create a Wavelength v. Time graph see OEM/Worek.py

# In this demo we will not be applying any transformations.
# We will leave it to your own imagination.

#### Imports ####

# Every plugin imports from EnlightenPlugin

# There are a number of ways to import in Python,
# this way places everything into the global scope.

from EnlightenPlugin import *

#### The Plugin ####

class hello_graph(EnlightenPluginBase):

    # get_configuration is called once early on.
    # Here we will define how the user interface changes
    # when the plugin is first connected
    def get_configuration(self):

        # This variable is used in two places.
        #
        #   (1) Here. It is important that we define all
        #   of the plots we are going to graph. Before
        #   the plugin executes, the plot name will be
        #   visible in the graph's legend.
        #
        #   (2) We will use it again in process_request.
        #   Take care to use exactly the same string
        #   when referencing your plot.
        self.my_series = {
            "Copy of Graph !": {}
        }

        # Disambiguation.
        # Graph refers to the window which displays plots.
        # Plots are the paths themselves which represent spectra or time-series, etc.
        # 
        # The main scope graph shows only one plot, the spectra.
        # Your plugin's graph can display many plots.
        #
        # This plugin only shows one plot, to copy exactly the main graph.

        # Here we will provide a friendly name for the plugin
        # and the all-important has_other_graph= attribute
        # which signals to Enlighten to draw a new graph window.
        # We will also provide the series names for the legend
        # and axis labels.
        return EnlightenPluginConfiguration(
            name = "Hello Graph",
            has_other_graph = True,
            series_names = self.my_series.keys(),
            x_axis_label = "x-axis",
            y_axis_label = "y-axis",
        )

    # process_request is called continuously when a plugin is enabled.
    # Otherwise it is called when the "Process" button is clicked.
    def process_request(self, request):
        
        # request.settings contains wavelengths and wavenumbers
        # if you would like the x-axis to represent pixels use
        # range(len(request.processed_reading.get_processed()))
        # 
        # Make sure your x-axis label is representative of the
        # quantity you use here
        x_values = request.settings.wavelengths

        # This is where we copy data from the spectroscope !
        y_values = request.processed_reading.get_processed()

        # Here using the same series name defined above,
        # we prepare the plot to be sent back in an
        # EnlightenPluginResponse
        self.my_series["Copy of Graph !"] = {
            "x": x_values,
            "y": y_values
        }

        # EnlightenPluginResponse also takes the unmodified original request
        # as a parameter
        return EnlightenPluginResponse(request, series=self.my_series)
