
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
        self.name = "Hello Graph",
        self.has_other_graph = True,
        self.series_names = self.my_series.keys(),
        self.x_axis_label = "x-axis",
        self.y_axis_label = "y-axis",

    # process_request is called continuously when a plugin is enabled.
    # Otherwise it is called when the "Process" button is clicked.
    def process_request(self, request):
        
        # request.settings contains wavelengths and wavenumbers
        # if you would like the x-axis to represent pixels use
        # range(len(request.processed_reading.get_processed()))
        # 
        # Make sure your x-axis label is representative of the
        # quantity you use here
        x_values = self.getAxis()

        # This is where we copy data from the spectroscope !
        y_values = request.processed_reading.get_processed()

        self.plot(
            x=x_values, 
            y=y_values,
            title="Copy of Graph !",
            color="teal"
        )