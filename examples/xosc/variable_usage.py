"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

  An example creates a variable and change it, triggering an entity
  based on the variable

  Some features used:

  - VariableCondition

  - VariableDeclarations

  - RelativeLaneChangeAction

  - VariableSetAction
"""

import os

from scenariogeneration import ScenarioGenerator, prettyprint, xosc


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
        variabledec = xosc.VariableDeclarations()
        variabledec.add_variable(
            xosc.Variable("myvar", xosc.ParameterType.integer, 0)
        )
        ## create entities

        egoname = "Ego"

        entities = xosc.Entities()
        entities.add_scenario_object(
            egoname, xosc.CatalogReference("VehicleCatalog", "car_white")
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

        var_event = xosc.Event("change_variable_event", xosc.Priority.override)
        var_event.add_action(
            "change variable", xosc.VariableSetAction("myvar", 1)
        )
        var_event.add_trigger(
            xosc.ValueTrigger(
                "timetrigger",
                0,
                xosc.ConditionEdge.none,
                xosc.SimulationTimeCondition(2, xosc.Rule.greaterThan),
            )
        )
        var_man = xosc.Maneuver("change_variable")
        var_man.add_event(var_event)

        var_mangr = xosc.ManeuverGroup("mangroup")
        var_mangr.add_maneuver(var_man)

        ego_event = xosc.Event("ego_event", xosc.Priority.override)
        ego_event.add_action(
            "ego action",
            xosc.RelativeLaneChangeAction(
                -1,
                egoname,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.sinusoidal,
                    xosc.DynamicsDimension.time,
                    3,
                ),
            ),
        )
        ego_event.add_trigger(
            xosc.ValueTrigger(
                "timetrigger",
                1,
                xosc.ConditionEdge.none,
                xosc.VariableCondition("myvar", 1, xosc.Rule.equalTo),
            )
        )
        ego_man = xosc.Maneuver("ego_maneuver")
        ego_man.add_event(ego_event)
        ego_mangr = xosc.ManeuverGroup("ego_mangroup")
        ego_mangr.add_actor(egoname)
        ego_mangr.add_maneuver(ego_man)

        act = xosc.Act("act1")
        act.add_maneuver_group(var_mangr)
        act.add_maneuver_group(ego_mangr)
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
        sb.add_act(act)

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
            variable_declaration=variabledec,
        )

        return sce


if __name__ == "__main__":
    sce = Scenario()
    # Print the resulting xml
    prettyprint(sce.scenario().get_element())

    # write the OpenSCENARIO file as xosc using current script name
    sce.generate(".")

    # uncomment the following lines to display the scenario using esmini
    from scenariogeneration import esmini

    esmini(sce, os.path.join("../esmini"))
