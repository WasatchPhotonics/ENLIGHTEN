from EnlightenPlugin import *

class hello_graph(EnlightenPluginBase):

    # get_configuration is called once early on.
    def get_configuration(self):
        self.name = "Hello Graph",
        self.has_other_graph = True,
        self.series_names = self.my_series.keys(),
        self.x_axis_label = "x-axis",
        self.y_axis_label = "y-axis",

    # process_request is called continuously when a plugin is enabled.
    # Otherwise it is called when the "Process" button is clicked.
    def process_request(self, request):
        x_values = self.get_axis()

        # This is where we copy data from the spectroscope !
        y_values = request.processed_reading.get_processed()

        self.plot(
            x=x_values, 
            y=y_values,
            title="Copy of Graph !",
            color="teal"
        )