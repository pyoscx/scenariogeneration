"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    Example showing how one vehicle triggers based on the acceleration of another vehicle, then changes its speed.


    Some features used:

    - AccelerationCondition

    - StandStillCondition

    - RelativeRoadPosition

    - AbsoluteSpeedAction


"""
import os
from scenariogeneration import xosc, prettyprint, ScenarioGenerator

class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        self.open_scenario_version = 2
    def scenario(self,**kwargs):
        ### create catalogs
        catalog = xosc.Catalog()
        catalog.add_catalog("VehicleCatalog", "../xosc/Catalogs/Vehicles")

        ### create road
        road = xosc.RoadNetwork(
            roadfile="../xodr/e6mini.xodr", scenegraph="../models/e6mini.osgb"
        )


        ### create parameters
        paramdec = xosc.ParameterDeclarations()

        ### create vehicles

        bb = xosc.BoundingBox(2, 5, 1.8, 2.0, 0, 0.9)
        fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
        ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
        white_veh = xosc.Vehicle("car_white", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10)

        white_veh.add_property_file("../models/car_white.osgb")
        white_veh.add_property("model_id", "0")


        bb = xosc.BoundingBox(1.8, 4.5, 1.5, 1.3, 0, 0.8)
        fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
        ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
        red_veh = xosc.Vehicle("car_red", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10)

        red_veh.add_property_file("../models/car_red.osgb")
        red_veh.add_property("model_id", "2")

        ## create entities

        egoname = "Ego"
        targetname = "Target"

        entities = xosc.Entities()
        entities.add_scenario_object(egoname, white_veh)
        entities.add_scenario_object(targetname, red_veh)


        ### create init

        init = xosc.Init()
        step_time = xosc.TransitionDynamics(
            xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
        )

        egospeed = xosc.AbsoluteSpeedAction(3, step_time)
        egostart = xosc.TeleportAction(xosc.LanePosition(25, 0, -3, 0))

        targetspeed = xosc.AbsoluteSpeedAction(15, step_time)
        targetstart = xosc.TeleportAction(xosc.RelativeRoadPosition(30, 0, egoname))

        init.add_init_action(egoname, egospeed)
        init.add_init_action(egoname, egostart)
        init.add_init_action(targetname, targetspeed)
        init.add_init_action(targetname, targetstart)


        ### create an event for target

        trigcond = xosc.AccelerationCondition(2.9, xosc.Rule.greaterThan)

        trigger = xosc.EntityTrigger(
            "mytesttrigger", 0.2, xosc.ConditionEdge.none, trigcond, egoname
        )

        event = xosc.Event("myfirstevent", xosc.Priority.overwrite)
        event.add_trigger(trigger)

        sin_time = xosc.TransitionDynamics(
            xosc.DynamicsShapes.linear, xosc.DynamicsDimension.time, 3.9
        )
        action = xosc.AbsoluteSpeedAction(0, sin_time)
        event.add_action("newspeed", action)

        ## create the maneuver
        man = xosc.Maneuver("my_maneuver")
        man.add_event(event)

        mangr = xosc.ManeuverGroup("mangroup")
        mangr.add_actor(targetname)
        mangr.add_maneuver(man)


        ### create an event for the ego


        start_trig = xosc.ValueTrigger(
            "ego_acc",
            0,
            xosc.ConditionEdge.none,
            xosc.SimulationTimeCondition(0.5, xosc.Rule.greaterThan),
        )
        start_action = xosc.AbsoluteSpeedAction(
            30,
            xosc.TransitionDynamics(
                xosc.DynamicsShapes.sinusoidal, xosc.DynamicsDimension.rate, 3
            ),
        )

        ego_start_event = xosc.Event("startevent", xosc.Priority.overwrite)
        ego_start_event.add_trigger(start_trig)
        ego_start_event.add_action("start_action", start_action)


        trigcond = xosc.StandStillCondition(0.5)
        standstill_trigger = xosc.EntityTrigger(
            "standstill trigger", 0.1, xosc.ConditionEdge.none, trigcond, targetname
        )
        stop_action = xosc.AbsoluteSpeedAction(
            0,
            xosc.TransitionDynamics(
                xosc.DynamicsShapes.linear, xosc.DynamicsDimension.rate, 10
            ),
        )

        ego_event = xosc.Event("stopevent", xosc.Priority.overwrite)
        ego_event.add_trigger(standstill_trigger)
        ego_event.add_action("stop_action", stop_action)

        ego_man = xosc.Maneuver("ego_maneuver")
        ego_man.add_event(ego_start_event)
        ego_man.add_event(ego_event)

        ego_mangr = xosc.ManeuverGroup("mangroup")
        ego_mangr.add_actor(egoname)
        ego_mangr.add_maneuver(ego_man)

        starttrigger = xosc.ValueTrigger(
            "starttrigger",
            0,
            xosc.ConditionEdge.rising,
            xosc.SimulationTimeCondition(0, xosc.Rule.greaterThan),
        )
        act = xosc.Act("my_act", starttrigger)
        act.add_maneuver_group(mangr)
        act.add_maneuver_group(ego_mangr)


        ## create the storyboard
        sb = xosc.StoryBoard(
            init,
            xosc.ValueTrigger(
                "stop_simulation",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(15, xosc.Rule.greaterThan),
                "stop",
            ),
        )
        sb.add_act(act)

        ## create the scenario
        sce = xosc.Scenario(
            "adapt_speed_example",
            "Mandolin",
            paramdec,
            entities=entities,
            storyboard=sb,
            roadnetwork=road,
            catalog=catalog,
            osc_minor_version = self.open_scenario_version,
        )
        return sce

if __name__ == '__main__':
    sce = Scenario()
    # Print the resulting xml
    prettyprint(sce.get_element())

    # write the OpenSCENARIO file as xosc using current script name
    sce.generate(".")

    # uncomment the following lines to display the scenario using esmini
    # from scenariogeneration import esmini
    # esmini(sce,os.path.join('esmini'))
