"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    An example how to add a sumo controller to an object


    Some features used:

    - Controller

    - Properties

"""

import os
from scenariogeneration import xosc, prettyprint, ScenarioGenerator


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        self.open_scenario_version = 2

    def scenario(self, **kwargs):
        ### create catalogs
        catalog = xosc.Catalog()
        catalog.add_catalog("VehicleCatalog", "../xosc/Catalogs/Vehicles")

        ### create road
        road = xosc.RoadNetwork(
            roadfile="../xodr/e6mini.xodr", scenegraph="../models/e6mini.osgb"
        )

        ### create parameters
        paramdec = xosc.ParameterDeclarations()

        paramdec.add_parameter(
            xosc.Parameter("$HostVehicle", xosc.ParameterType.string, "car_white")
        )
        paramdec.add_parameter(
            xosc.Parameter("$TargetVehicle", xosc.ParameterType.string, "car_red")
        )

        ### create vehicles

        bb = xosc.BoundingBox(2, 5, 1.8, 2.0, 0, 0.9)
        fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
        ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
        white_veh = xosc.Vehicle(
            "car_white", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10
        )

        white_veh.add_property_file("../models/car_white.osgb")
        white_veh.add_property("model_id", "0")

        bb = xosc.BoundingBox(1.8, 4.5, 1.5, 1.3, 0, 0.8)
        fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
        ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
        red_veh = xosc.Vehicle(
            "car_red", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10
        )

        red_veh.add_property_file("../models/car_red.osgb")
        red_veh.add_property("model_id", "2")

        ## create entities

        egoname = "Ego"
        targetname = "Target"
        prop = xosc.Properties()
        prop.add_property(name="esminiController", value="SumoController")
        prop.add_file("../sumo_inputs/e6mini.sumocfg")
        cont = xosc.Controller("mycontroler", prop)
        # cont.dump_to_catalog('Controller.xosc','Controller','controllers','Mandolin')

        entities = xosc.Entities()
        entities.add_scenario_object(egoname, white_veh)
        entities.add_scenario_object(targetname, red_veh, cont)

        ### create init

        init = xosc.Init()
        step_time = xosc.TransitionDynamics(
            xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
        )

        egospeed = xosc.AbsoluteSpeedAction(10, step_time)
        egostart = xosc.TeleportAction(xosc.LanePosition(25, 0, -3, 0))

        init.add_init_action(egoname, egospeed)
        init.add_init_action(egoname, egostart)

        ## create the story
        storyparam = xosc.ParameterDeclarations()
        storyparam.add_parameter(
            xosc.Parameter("$owner", xosc.ParameterType.string, targetname)
        )
        story = xosc.Story("mystory", storyparam)

        ## create the storyboard
        sb = xosc.StoryBoard(init)

        ## create the scenario
        sce = xosc.Scenario(
            "adapt_speed_example",
            "Mandolin",
            paramdec,
            entities=entities,
            storyboard=sb,
            roadnetwork=road,
            catalog=catalog,
            osc_minor_version=self.open_scenario_version,
        )
        return sce


if __name__ == "__main__":
    sce = Scenario()
    # Print the resulting xml
    prettyprint(sce.scenario().get_element())

    # write the OpenSCENARIO file as xosc using current script name
    sce.generate(".")

    # uncomment the following lines to display the scenario using esmini
    # from scenariogeneration import esmini
    # esmini(sce,os.path.join('esmini'))
