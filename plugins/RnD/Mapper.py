"""
This plugin is a front end in Enlighten to the x/y Mapper

It gives buttons to move the mapper in x/y
Fields to define a step width
And an output to show the location in x/y
And a button to set the location to zero

"""

from .MapperFiles import MapperArduino


from EnlightenPlugin import *

class Mapper(EnlightenPluginBase):

    VERSION = "1.0"

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
        
        self.field(
            name="Zero Position",
            datatype="button",
            callback=self.zero_position,
            tooltip="Set both X/Y Position Displays to 0.00"
        )

        self.field(name="Step Size (mm)", 
                   direction="input", 
                   datatype=float, 
                   precision=2,
                   initial=1.0, 
                   minimum=-100.0,
                   maximum=100.0,
                   callback=self.update_variables,
                   tooltip="How far to move the mapper in x/y in a single step")

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
                   minimum=-200.0,
                   maximum=200.0,
                   callback=self.update_variables,
                   tooltip="Where to move the mapper to in X direction")
        
        self.field(name="Y Target (mm)", 
                   direction="input", 
                   datatype=float, 
                   precision=2,
                   initial=0.00, 
                   minimum=-200.0,
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
        

    ############################################################################
    # Mapper Functions
    ############################################################################
        

    def zero_position(self):
        # tell mapper
        self.mapper.x.set_position(0)
        self.mapper.y.set_position(0)
        # update internal variables
        self.position_x = 0.0
        self.position_y = 0.0
        self.update_display()


    def step_forward(self):
        # tell mapper
        self.mapper.y.move_relative_mm(self.step_size)
        # update internal variables
        self.position_y += self.step_size
        self.update_display()
        
   
    def step_back(self):
        # tell mapper
        self.mapper.y.move_relative_mm(-self.step_size)
        # update internal variables
        self.position_y -= self.step_size
        self.update_display()

   
    def step_left(self):
        # tell mapper
        self.mapper.x.move_relative_mm(self.step_size)
        # update internal variables
        self.position_x += self.step_size
        self.update_display()

   
    def step_right(self):
        # tell mapper
        self.mapper.x.move_relative_mm(-self.step_size)
        # update internal variables
        self.position_x -= self.step_size
        self.update_display()


    def move_to_target(self):
        # tell mapper
        self.mapper.x.move_absolute_mm(self.target_x)
        # we might need to wait for the mapper to arrive before sending the next command...?
        self.mapper.y.move_absolute_mm(self.target_y)
        # update internal variables
        self.position_x = self.target_x
        self.position_y = self.target_y
        self.update_display()


    def home_mapper(self):
        # tell mapper
        self.mapper.x.find_home_position()  # this blocks, so we do not need to wait
        self.mapper.y.find_home_position()
        # update internal variables
        self.position_x = 0.0
        self.position_y = 0.0
        self.update_display()
        

    def update_display(self):
        # update position displays
        self.get_widget_from_name("X Position (mm)").setText(f"{self.position_x}")
        self.get_widget_from_name("Y Position (mm)").setText(f"{self.position_y}")


    ############################################################################
    # Plugin Activity
    ############################################################################
        

    def update_variables(self):
        # update all input variables
        self.step_size = self.get_widget_from_name("Step Size (mm)").value()
        self.target_x = self.get_widget_from_name("X Target (mm)").value()
        self.target_y = self.get_widget_from_name("Y Target (mm)").value()
        


    def disconnect(self):
        self.mapper.disconnect()
        super().disconnect()
        
