import re
import logging

log = logging.getLogger(__name__)

##
# These are routines that I would have put into PluginBaseClass classes, but I 
# can't trust that users won't accidentally contravene / delete / corrupt them 
# when editting, so I'm putting them here.
#
# Note that these methods in some case CHANGE (normalize) the passed objects.
class PluginValidator:

    ##
    # @param config - an EnlightenPluginConfiguration
    @staticmethod
    def validate_config(config, module_info):
        if config is None:
            return False

        config.graph_type = config.graph_type.lower().strip()

        if config.name is None:
            log.debug("configuration missing name, defaulting from module")
            config.name = module_info.name

        if config.fields is None:
            config.fields = []

        if config.graph_type not in ["line", "xy"]:
            log.error("invalid graph_type for plug-in %s: %s", config.name, config.graph_type)
            return False

        # add an "x_unit" attribute to the EnlightenPluginConfiguration
        config.x_unit = None
        s = config.x_axis_label
        if s is not None:
            if re.search(r'wavelength|nm', s, re.IGNORECASE):
                config.x_unit = "nm"
            elif re.search(r'wavenumber|shift|cm', s, re.IGNORECASE):
                config.x_unit = "cm"
            elif re.search(r'pixel|px', s, re.IGNORECASE):
                config.x_unit = "px"
            if config.x_unit is not None:
                log.debug("assigned x_unit %s", config.x_unit)

        return True

    ##
    # @param field - an EnlightenPluginField
    @staticmethod
    def validate_field(field):
        if field is None:
            return False

        ##
        # Accepts any of these:
        # - datatype="string"
        # - datatype="int"
        # - datatype="float"
        # - datatype="bool"
        # - datatype="str"  -> "string"
        # - datatype=str    -> "string"
        # - datatype=int    -> "int"
        # - datatype=float  -> "float"
        # - datatype=bool   -> "bool"
        def normalize_datatype(t):
            if isinstance(t, str):
                typename = t
            elif isinstance(t, type):
                m = re.match(r"<class '(.*)'>", str(t))
                if m:
                    typename = m.group(1)
            else:
                log.error("unknown EnlightenPluginField datatype: %s", t)
                typename = "unknown"
            typename = typename.lower().strip()
            if typename == "str":
                typename = "string"
            return typename

        try:
            field.datatype = normalize_datatype(field.datatype)
            field.direction = field.direction.lower().strip()

            # check for valid datatypes
            if field.datatype not in ["string", "int", "float", "bool", "button", "pandas", "radio", "combobox"]:
                log.error("invalid EnlightenPluginField %s datatype: %s", field.name, field.datatype)
                return False

            # override direction (some datatypes are one-way)
            if field.datatype in ["button", "combobox"]:
                field.direction = "input"
            elif field.datatype in ["pandas"]:
                field.direction = "output"

            # check for valid directions
            if field.direction not in ["input", "output"]:
                log.error("invalid EnlightenPluginField %s direction: %s", field.name, field.direction)
                return False

            ########################################################################
            # check for required attribute combinations 
            ########################################################################

            # button / callback
            if field.callback is not None and field.datatype != "button":
                log.error("EnlightenPlugInField %s callback ignored for datatype %s", field.name, field.datatype)
            elif field.datatype == "button" and field.callback is None:
                log.error("EnlightenPlugInField %s button missing callback", field.name)
                return False
            elif field.datatype == "combobox" and (field.choices is None or len(field.choices) == 0):
                log.error(f"EnlightenPlugInField {field.name} combobox missing choices")
                return False
        except:
            log.error("error validating EnlightenPluginField", exc_info=1)
            return False

        return True

    ##
    # @param response - an EnlightenPluginResponse
    @staticmethod
    def validate_response(response):
        return response is not None
