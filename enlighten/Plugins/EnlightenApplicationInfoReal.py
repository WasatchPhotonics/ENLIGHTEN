from EnlightenPlugin import EnlightenApplicationInfo

##
# We don't necessarily want to pass (and pickle) whole Graph and SaveOptions 
# objects to plugins (at this time), so just provide controlled callbacks that 
# give them what they need.
#
# Also provides a mechanism to pass the results of satisified 
# EnlightenPluginDependency objects from EnlightenPluginConfiguration to the
# plugin's connect() method.
class EnlightenApplicationInfoReal(EnlightenApplicationInfo):

    def __init__(self, 
            graph_scope, 
            reference_is_dark_corrected,
            save_options,
            kia_feature,
            plugin_settings,
            measurement_factory,
            measurements_clipboard,
            read_measurements,# present for legacy reasons
            horiz_roi,
            plugin_fields,
            dependencies = {}):

        self.get_x_axis_unit_callback = graph_scope.get_x_axis_unit
        self.reference_is_dark_corrected = reference_is_dark_corrected
        self.save_options = save_options
        self.save_options_directory_callback = save_options.get_directory
        self.save_today_path = save_options.generate_today_dir
        self.plugin_settings = plugin_settings
        self.measurements_clipboard = measurements_clipboard
        self.measurement_factory = measurement_factory
        self.kia_feature = kia_feature
        self.dependencies = dependencies
        self.read_measurements = read_measurements
        self.horiz_roi = horiz_roi 
        self.plugin_fields = plugin_fields

    def get_x_axis_unit(self):
        return self.get_x_axis_unit_callback()

    def get_save_path(self):
        return self.save_options_directory_callback()

    def get_dependency(self, name):
        return self.dependencies.get(name, None)

    def get_reference_is_dark_corrected(self):
        return self.reference_is_dark_corrected()

    def get_save_options(self):
        return self.save_options

    def get_plugin_fields(self):
        return self.plugin_fields
