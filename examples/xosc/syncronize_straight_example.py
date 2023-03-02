"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    Example of a synchronizing two vehicles at one point

    Some features used:


    - AbsoluteSynchronizeAction


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
        targetname = "Target"

        entities = xosc.Entities()
        entities.add_scenario_object(
            egoname, xosc.CatalogReference("VehicleCatalog", "car_red")
        )
        entities.add_scenario_object(
            targetname, xosc.CatalogReference("VehicleCatalog", "car_blue")
        )

        ### create init

        init = xosc.Init()

        init.add_init_action(
            egoname, xosc.TeleportAction(xosc.LanePosition(50, 0, -2, 0))
        )
        init.add_init_action(
            egoname,
            xosc.AbsoluteSpeedAction(
                10,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        init.add_init_action(
            targetname, xosc.TeleportAction(xosc.LanePosition(30, 0, -3, 0))
        )
        init.add_init_action(
            targetname,
            xosc.AbsoluteSpeedAction(
                20,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        ## target action

        tar_action = xosc.SynchronizeAction(
            egoname,
            xosc.LanePosition(200, 0, -1, 0),
            xosc.LanePosition(200, 0, -2, 0),
            target_tolerance_master=1,
            target_tolerance=1,
            final_speed=xosc.RelativeSpeedToMaster(
                10, xosc.SpeedTargetValueType.delta, xosc.TargetTimeSteadyState(10)
            ),
        )

        tar_event = xosc.Event("target_event", xosc.Priority.overwrite)
        tar_event.add_trigger(
            xosc.ValueTrigger(
                "ego_start",
                0,
                xosc.ConditionEdge.none,
                xosc.SimulationTimeCondition(3, xosc.Rule.greaterThan),
            )
        )
        tar_event.add_action("tar_action", tar_action)

        tar_man = xosc.Maneuver("target_man")
        tar_man.add_event(tar_event)

        tar_man_gr = xosc.ManeuverGroup("target_man_gr")
        tar_man_gr.add_maneuver(tar_man)
        tar_man_gr.add_actor(targetname)

        ## act
        act = xosc.Act(
            "myact",
            xosc.ValueTrigger(
                "start",
                0,
                xosc.ConditionEdge.none,
                xosc.SimulationTimeCondition(0, xosc.Rule.greaterThan),
            ),
        )

        act.add_maneuver_group(tar_man_gr)
        ## create the storyboard
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
        sb.add_act(act)

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
