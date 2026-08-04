"""
This plugin is a front end in Enlighten to the x/y Mapper

It gives buttons to move the mapper in x/y
Fields to define a step width
And an output to show the location in x/y
And a button to set the location to zero

Change Log:
- 08-03-2026    
    - Zero position button and related function removed (currently commented incase there is a use to keep it)
    - X Target and Y Target can no longer be negative
        - Individual steps via the 4 directional buttons will still move negative as needed.
    - The system goes "home" at startup
    - Various debug logs added
    - Framework for micrometer (um) movement added
    - a sleep of 0.5 added to home_mapper
    - the directional controls (forward, back, right and left) funtion using the um scale for fine control
    - Version updated to 1.1
- 08-04-2026    
    - Updated update_display to allow for changes in um and mm

Questions:
- should the "Home Mapper" button be removed?  if we home at startup is there ever a reason to home after?
- currently completes the X-axis movement then the Y-axis movement, can/should we do both simultaneously? 
- Should the directional controls work from the camera perspective?

To Do:
- Remove the commented code sections once confirmed it is liked that way.
- Shortcut keys for the fine tuning directional controls?
"""

import logging
import time

from .MapperFiles import MapperArduino

from EnlightenPlugin import *

log = logging.getLogger(__name__)

class Mapper(EnlightenPluginBase):

    VERSION = "1.1"

    ############################################################################
    # Lifecycle
    ############################################################################

    def get_configuration(self):
        self.name = f"Mapper {self.VERSION}"

        self.field(
            name="X Position (mm)",
            direction="output",
            datatype=float,
            precision=2,
            initial=0.00,
            tooltip="Current X Position of the Mapper",
        )

        self.field(
            name="Y Position (mm)",
            direction="output",
            datatype=float,
            precision=2,
            initial=0.00,
            tooltip="Current Y Position of the Mapper",
        )
        
        #self.field(
            #name="Zero Position",
            #datatype="button",
            #callback=self.zero_position,
            #tooltip="Set both X/Y Position Displays to 0.00"
        #)
        
        self.field(name = "Step Size (um)",
                   direction="input", 
                   datatype=float, 
                   precision=2,
                   initial=1.0, 
                   minimum=0.0,
                   maximum = 1000.0,
                   callback=self.update_variables,
                   tooltip="How far to move the mapper in x/y in a single step")
       
        #self.field(name = "Step Size (um)",
                    #direction = "input",
                    #datatype = "bool",
                    #tooltip = "Use micrometers (um) instead of millimeters (mm)")

        self.field(
            name="Left",
            datatype="button",
            callback=self.step_left,
            tooltip="Move Left by a Single Step"
        )
        self.field(
            name="Right",
            datatype="button",
            callback=self.step_right,
            tooltip="Move Right by a Single Step"
        )
        self.field(
            name="Forward",
            datatype="button",
            callback=self.step_forward,
            tooltip="Move Forward by a Single Step"
        )
        self.field(
            name="Back",
            datatype="button",
            callback=self.step_back,
            tooltip="Move Back by a Single Step"
        )

        self.field(name="X Target (mm)", 
                   direction="input", 
                   datatype=float,
                   precision=2,
                   initial=0.00, 
                   minimum=0.0,
                   maximum=200.0,
                   callback=self.update_variables,
                   tooltip="Where to move the mapper to in X direction")
        
        self.field(name="Y Target (mm)", 
                   direction="input", 
                   datatype=float, 
                   precision=2,
                   initial=0.00, 
                   minimum=0.0,
                   maximum=200.0,
                   callback=self.update_variables,
                   tooltip="Where to move the mapper to in Y direction")

        self.field(
            name="Move to Target",
            datatype="button",
            callback=self.move_to_target,
            tooltip="Move Forward by a Single Step"
        )

        self.field(
            name="Home Mapper",
            datatype="button",
            callback=self.home_mapper,
            tooltip="Finds the Home Position of the Mapper and Defines it as 0/0"
        )


        self.has_other_graph = False
        self.block_enlighten = True

        #
        # Mapper Definitions
        #        
        
        self.mapper = MapperArduino.Mapper()        
        
        self.position_x = 0.0
        self.position_y = 0.0
        self.step_size = 1.0
        self.target_x = 0.0
        self.target_y = 0.0
        
        self.home_mapper()
        
    ############################################################################
    # Mapper Functions
    ############################################################################
        
# This updates the current position values to 0,0.  Moving +30 on X will move 30 based on this new 0 position
    #def zero_position(self):
        # tell mapper
        #self.mapper.x.set_position(0)
        #self.mapper.y.set_position(0)
        # update internal variables
        #self.position_x = 0.0
        #self.position_y = 0.0
        #self.update_display()

# Moving positive on the Y-axis based on the current value of step_size
    def step_forward(self):
        #if self.get_widget_from_name("Step Size (um)").isChecked():
            #self.mapper.y.move_relative_um(self.step_size)
            # update internal variables
            #self.position_y += self.step_size
            #self.update_display()
        #else:
            #self.mapper.y.move_relative_mm(self.step_size)
            #self.position_y += self.step_size
            #self.update_display()
            
        self.mapper.y.move_relative_um(self.step_size)
        # update internal variables
        self.position_y += (self.step_size / 1000)
        self.update_display()
        
# Moving negative on the Y-axis based on the current value of step_size
    def step_back(self):
        #if self.get_widget_from_name("Step Size (um)").isChecked():
            #self.mapper.y.move_relative_um(-self.step_size)
            # update internal variables
            #self.position_y -= self.step_size
            #self.update_display()
        #else:
            #self.mapper.y.move_relative_mm(-self.step_size)
            #self.position_y -= self.step_size
            #self.update_display()
            
        self.mapper.y.move_relative_um(-self.step_size)
        # update internal variables
        self.position_y -= (self.step_size / 1000)
        self.update_display()

# Moving positive on the X-axis based on the current value of step_size 
    def step_left(self):
        #if self.get_widget_from_name("Step Size (um)").isChecked():
            #self.mapper.x.move_relative_um(-self.step_size)
            # update internal variables
            #self.position_x -= self.step_size
            #self.update_display()
        #else:
            #self.mapper.x.move_relative_mm(-self.step_size)
            #self.position_x -= self.step_size
            #self.update_display()
            
        self.mapper.x.move_relative_um(-self.step_size)
        # update internal variables
        self.position_x -= (self.step_size / 1000)
        self.update_display()

# Moving negative on the X-axis based on the current value of step_size   
    def step_right(self):
        #if self.get_widget_from_name("Step Size (um)").isChecked():
            #self.mapper.x.move_relative_um(self.step_size)
            # update internal variables
            #self.position_x += self.step_size
            #self.update_display()
        #else:
            #self.mapper.x.move_relative_mm(self.step_size)
            #self.position_x += self.step_size
            #self.update_display()
            
        self.mapper.x.move_relative_um(self.step_size)
        # update internal variables
        self.position_x += (self.step_size / 1000)
        self.update_display()

# Moves to the specific position, based on 0,0 mapping position and user inputs
    def move_to_target(self):
        log.debug(f"Moving X-axis to {self.target_x} millimeters (mm)")
        self.mapper.x.move_absolute_mm(self.target_x)
        log.debug(f"Moving Y-axis to {self.target_y} millimeters (mm)")
        self.mapper.y.move_absolute_mm(self.target_y)
            
        self.position_x = self.target_x
        self.position_y = self.target_y
        self.update_display()

# Moves the stage to the true home, 0,0, of the rails/stepper motors and updates the position
    def home_mapper(self):
        # tell mapper
        self.mapper.x.find_home_position()  # this blocks, so we do not need to wait
        # previous statement doesn't seem to be true 100% of the time
        # occassionally the X-axis will home and the Y-axis will start but not complete
        # the wait seems to fix this issue
        time.sleep(0.1) 
        self.mapper.y.find_home_position()
        # update internal variables
        self.position_x = 0.0
        self.position_y = 0.0
        self.update_display()
        

    def update_display(self):
        # update position displays
        widget = self.get_widget_from_name("X Position (mm)")
        
        if widget is not None:        
            self.get_widget_from_name("X Position (mm)").setText(f"{self.position_x}")
            log.debug(f"Current X-axis position: {self.position_x}")
            self.get_widget_from_name("Y Position (mm)").setText(f"{self.position_y}")
            log.debug(f"Current Y-axis position: {self.position_y}")


    ############################################################################
    # Plugin Activity
    ############################################################################
        

    def update_variables(self):
        # update all input variables
        self.step_size = self.get_widget_from_name("Step Size (um)").value()
        self.target_x = self.get_widget_from_name("X Target (mm)").value()
        self.target_y = self.get_widget_from_name("Y Target (mm)").value()
        


    def disconnect(self):
        self.mapper.disconnect()
        super().disconnect()
        
    
