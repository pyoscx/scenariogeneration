"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    An example showing how a "and logic" for conditions can be created, the blue car has to pass the white one for it to stop


    Some features used:

    - ConditionGroup

    - TimeToCollisionCondition

    - TimeHeadwayCondition

    - AbsoluteSpeedAction

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
        speedyname = "speedy_gonzales"
        targetname = "Target"
        entities = xosc.Entities()
        entities.add_scenario_object(
            egoname, xosc.CatalogReference("VehicleCatalog", "car_white")
        )
        entities.add_scenario_object(
            speedyname, xosc.CatalogReference("VehicleCatalog", "car_blue")
        )
        entities.add_scenario_object(
            targetname, xosc.CatalogReference("VehicleCatalog", "car_yellow")
        )

        ### create init

        init = xosc.Init()

        init.add_init_action(
            egoname, xosc.TeleportAction(xosc.LanePosition(50, 0, -2, 0))
        )
        init.add_init_action(
            egoname,
            xosc.AbsoluteSpeedAction(
                15,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        init.add_init_action(
            speedyname, xosc.TeleportAction(xosc.LanePosition(10, 0, -3, 0))
        )
        init.add_init_action(
            speedyname,
            xosc.AbsoluteSpeedAction(
                30,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        init.add_init_action(
            targetname, xosc.TeleportAction(xosc.LanePosition(100, 0, -2, 0))
        )
        init.add_init_action(
            targetname,
            xosc.AbsoluteSpeedAction(
                10,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        ### create the action

        event = xosc.Event("speedchange", xosc.Priority.overwrite)
        event.add_action(
            "speedaction",
            xosc.AbsoluteSpeedAction(
                10,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 3
                ),
            ),
        )

        # create two Conditions
        trig_cond1 = xosc.TimeToCollisionCondition(
            2, xosc.Rule.lessThan, entity=targetname
        )
        trig_cond2 = xosc.TimeHeadwayCondition(speedyname, 1, xosc.Rule.greaterThan)

        collision_trigger = xosc.EntityTrigger(
            "trigger", 0, xosc.ConditionEdge.none, trig_cond1, egoname
        )
        headway_trigger = xosc.EntityTrigger(
            "trigger", 0, xosc.ConditionEdge.none, trig_cond2, egoname
        )

        # create and add them to a ConditionGroup (and logic)
        andtrigger = xosc.ConditionGroup()
        andtrigger.add_condition(collision_trigger)
        andtrigger.add_condition(headway_trigger)

        # add trigger to event
        event.add_trigger(andtrigger)

        ## create the storyboard
        man = xosc.Maneuver("mymaneuver")
        man.add_event(event)

        sb = xosc.StoryBoard(
            init,
            xosc.ValueTrigger(
                "stop_simulation",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(20, xosc.Rule.greaterThan),
                "stop",
            ),
        )
        sb.add_maneuver(man, egoname)

        ## create the scenario
        sce = xosc.Scenario(
            "adaptspeed_example",
            "User",
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
