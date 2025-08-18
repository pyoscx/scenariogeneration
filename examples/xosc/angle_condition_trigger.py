# examples/xosc/angle_condition_trigger.py

"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

Example showing how to use AngleCondition as a trigger for an event.

"""
import math

from scenariogeneration.xosc import AngleCondition

from scenariogeneration import xosc, prettyprint, ScenarioGenerator, xodr


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        self.open_scenario_version = 3


    def scenario(self, **kwargs):
        # Catalogs
        catalog = xosc.Catalog()
        catalog.add_catalog("VehicleCatalog", "../xosc/Catalogs/Vehicles")

        # Road
        road = xosc.RoadNetwork(
            roadfile="../xodr/e6mini.xodr", scenegraph="../models/e6mini.osgb"
        )

        # Parameters
        paramdec = xosc.ParameterDeclarations()

        # Entities
        egoname = "Ego"
        targetname = "Target"
        entities = xosc.Entities()
        entities.add_scenario_object(
            egoname, xosc.CatalogReference("VehicleCatalog", "car_white")
        )
        entities.add_scenario_object(
            targetname, xosc.CatalogReference("VehicleCatalog", "car_yellow")
        )

        # Init
        init = xosc.Init()
        init.add_init_action(
            egoname, xosc.TeleportAction(xosc.LanePosition(10, 0, -2, 0))
        )
        init.add_init_action(
            egoname,
            xosc.AbsoluteSpeedAction(
                20,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.linear, xosc.DynamicsDimension.time, 1
                ),
            ),
        )
        init.add_init_action(
            targetname, xosc.TeleportAction(xosc.LanePosition(50, 0, -3, 0))
        )
        init.add_init_action(
            targetname,
            xosc.AbsoluteSpeedAction(
                10,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.linear, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        deg = 60
        rad = math.radians(deg)
        # AngleCondition (trigger when Ego's orientation is 60 degrees with 0.1 tolerance)
        angle_condition = AngleCondition(
            angle=rad,
            angle_tolerance=0.1,
            angle_type=xosc.AngleType.heading,
            coordinate_system=xosc.CoordinateSystem.world,
        )

        # Trigger

        angle_trigger = xosc.EntityTrigger(
            "trigger", 0, xosc.ConditionEdge.none, angle_condition, egoname
        )

        # Event and Maneuver
        event = xosc.Event("angle_event", xosc.Priority.overwrite)
        event.add_trigger(angle_trigger)

        event.add_action(
            "speedup",
            xosc.AbsoluteSpeedAction(
                30,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.linear, xosc.DynamicsDimension.time, 2
                ),
            ),
        )
        man = xosc.Maneuver("angle_maneuver")
        man.add_event(event)
        mangr = xosc.ManeuverGroup("angle_mangroup")
        mangr.add_actor("$owner")
        mangr.add_maneuver(man)

        # Act
        act = xosc.Act("angle_act", angle_trigger)
        act.add_maneuver_group(mangr)

        # Story
        storyparam = xosc.ParameterDeclarations()
        storyparam.add_parameter(
            xosc.Parameter("$owner", xosc.ParameterType.string, egoname)
        )
        story = xosc.Story("angle_story", storyparam)
        story.add_act(act)

        # Storyboard
        sb = xosc.StoryBoard(init)
        sb.add_story(story)

        # Scenario
        sce = xosc.Scenario(
            "AngleCondition_trigger_example",
            "ekelidar",
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
    prettyprint(sce.scenario().get_element())
    sce.generate(".")

    # AngleCondition is not yet supported by esmini, so we cannot run this scenario with esmini.

    # Uncomment to run with esmini
    # from scenariogeneration import esmini
    # import os
    # esmini(sce, os.path.join("../esmini"))
