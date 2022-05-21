"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example of how to create a vehicle catalog
    The properties are added in order to work with esmini 1.5-1.7


    Some features used:

    - Vehicle

    - BoundingBox

    - Axle

"""
import os
from scenariogeneration import xosc, prettyprint


# create a vehicle
bb = xosc.BoundingBox(2, 5, 1.8, 2.0, 0, 0.9)
fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
white_veh = xosc.Vehicle("car_pink", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10)

white_veh.add_property_file("../models/car_white.osgb")
white_veh.add_property("control", "internal")
white_veh.add_property("model_id", "0")

# dump it and create a new catalog file
white_veh.dump_to_catalog(
    "my_vehicles.xosc", "VehicleCatalog", "My vehicle catalog", "Mandolin"
)

# create a new vehicle
bb = xosc.BoundingBox(2, 5.1, 1.9, 2.0, 0, 0.9)
fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
red_veh = xosc.Vehicle("car_pink", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10)

red_veh.add_property_file("../models/car_red.osgb")
red_veh.add_property("control", "internal")
red_veh.add_property("model_id", "0")

# add it to the newly created catalog
red_veh.append_to_catalog("my_vehicles.xosc")
