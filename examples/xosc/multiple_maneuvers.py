"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    An example setting up multiple vehicles triggering on eachother and running in parallel

    Some features used:

    - AbsoluteLaneChangeAction

    - TimeHeadwayCondition

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

        ## create entities

        egoname = "Ego"
        redname = "Target1"
        yelname = "Target2"

        entities = xosc.Entities()
        entities.add_scenario_object(
            egoname, xosc.CatalogReference("VehicleCatalog", "car_white")
        )
        entities.add_scenario_object(
            redname, xosc.CatalogReference("VehicleCatalog", "car_red")
        )
        entities.add_scenario_object(
            yelname, xosc.CatalogReference("VehicleCatalog", "car_yellow")
        )

        ### create init

        init = xosc.Init()
        step_time = xosc.TransitionDynamics(
            xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
        )

        init.add_init_action(egoname, xosc.AbsoluteSpeedAction(30, step_time))
        init.add_init_action(
            egoname, xosc.TeleportAction(xosc.LanePosition(25, 0, -3, 0))
        )
        init.add_init_action(redname, xosc.AbsoluteSpeedAction(40, step_time))
        init.add_init_action(
            redname, xosc.TeleportAction(xosc.LanePosition(15, 0, -2, 0))
        )
        init.add_init_action(yelname, xosc.AbsoluteSpeedAction(30, step_time))
        init.add_init_action(
            yelname, xosc.TeleportAction(xosc.LanePosition(35, 0, -4, 0))
        )

        ### create an event for the red car

        r_trigcond = xosc.TimeHeadwayCondition(redname, 0.1, xosc.Rule.greaterThan)
        r_trigger = xosc.EntityTrigger(
            "redtrigger", 0.2, xosc.ConditionEdge.rising, r_trigcond, egoname
        )
        r_event = xosc.Event("first_lane_change", xosc.Priority.overwrite)
        r_event.add_trigger(r_trigger)
        r_event.add_action(
            "lane_change_red",
            xosc.AbsoluteLaneChangeAction(
                -4,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.sinusoidal, xosc.DynamicsDimension.time, 4
                ),
            ),
        )

        ## create the act for the red car
        r_man = xosc.Maneuver("red_maneuver")
        r_man.add_event(r_event)

        r_mangr = xosc.ManeuverGroup("mangroup_red")
        r_mangr.add_actor(redname)
        r_mangr.add_maneuver(r_man)

        act = xosc.Act(
            "red_act",
            xosc.ValueTrigger(
                "starttrigger",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(0, xosc.Rule.greaterThan),
            ),
        )
        act.add_maneuver_group(r_mangr)

        ## create an event for the yellow car

        y_trigcond = xosc.TimeHeadwayCondition(redname, 0.5, xosc.Rule.greaterThan)
        y_trigger = xosc.EntityTrigger(
            "yellow_trigger", 0, xosc.ConditionEdge.rising, y_trigcond, yelname
        )

        y_event = xosc.Event("yellow_lanechange", xosc.Priority.overwrite)
        y_event.add_trigger(y_trigger)

        y_event.add_action(
            "lane_change_yellow",
            xosc.AbsoluteLaneChangeAction(
                -3,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.sinusoidal, xosc.DynamicsDimension.time, 2
                ),
            ),
        )

        ## create the act for the yellow car
        y_man = xosc.Maneuver("yellow_maneuver")
        y_man.add_event(y_event)

        y_mangr = xosc.ManeuverGroup("yellow_mangroup")
        y_mangr.add_actor(yelname)
        y_mangr.add_maneuver(y_man)
        y_starttrigger = xosc.ValueTrigger(
            "starttrigger",
            0,
            xosc.ConditionEdge.rising,
            xosc.SimulationTimeCondition(0, xosc.Rule.greaterThan),
        )
        # y_act = xosc.Act('my_act',y_starttrigger)
        act.add_maneuver_group(y_mangr)

        ## create the story

        story = xosc.Story("mystory")
        story.add_act(act)
        # story.add_act(y_act)

        ## create the storyboard
        sb = xosc.StoryBoard(
            init,
            xosc.ValueTrigger(
                "stop_simulation",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(10, xosc.Rule.greaterThan),
                "stop",
            ),
        )
        sb.add_story(story)

        ## create the scenario
        sce = xosc.Scenario(
            "adaptspeed_example",
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
