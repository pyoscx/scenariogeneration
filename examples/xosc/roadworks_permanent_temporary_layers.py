"""Exercise a temporary lane layer with two cars at 50 km/h.

Run from the repository root with
`python -m examples.xosc.roadworks_permanent_temporary_layers`.

Based on esmini's reference scenario:
https://github.com/esmini/esmini/blob/master/resources/xosc/roadworks_permanent_temporary_layers.xosc
"""

from argparse import ArgumentParser
from pathlib import Path

from examples.xodr.roadworks_permanent_temporary_layers import (
    Scenario as RoadworksRoad,
)
from scenariogeneration import xosc


class Scenario(RoadworksRoad):
    def scenario(self, **kwargs):
        entities = xosc.Entities()
        init = xosc.Init()
        speed_dynamics = xosc.TransitionDynamics(
            xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 0
        )
        for name, lane_id, position, layer, model_id in (
            ("Car1", -4, 10, None, 0),
            ("Car2", -3, 25, xosc.LaneLayerType.permanent, 2),
        ):
            vehicle = xosc.Vehicle(
                name,
                xosc.VehicleCategory.car,
                xosc.BoundingBox(1.8, 4.5, 1.5, 1.3, 0, 0.75),
                xosc.Axle(0.5, 0.65, 1.6, 2.8, 0.35),
                xosc.Axle(0, 0.65, 1.6, 0, 0.35),
                69,
                10,
                10,
            )
            vehicle.add_property("model_id", str(model_id))
            entities.add_scenario_object(name, vehicle)
            init.add_init_action(
                name,
                xosc.TeleportAction(
                    xosc.LanePosition(position, 0, lane_id, 1, layer=layer)
                ),
            )
            init.add_init_action(
                name, xosc.AbsoluteSpeedAction(50 / 3.6, speed_dynamics)
            )

        distance = xosc.DistanceCondition(
            5,
            xosc.Rule.lessOrEqual,
            xosc.LanePosition(
                85, 0, -3, 1, layer=xosc.LaneLayerType.permanent
            ),
            freespace=False,
            distance_type=xosc.RelativeDistanceType.euclidianDistance,
            coordinate_system=xosc.CoordinateSystem.entity,
        )
        event = xosc.Event("LaneChangeEvent", xosc.Priority.override)
        event.add_trigger(
            xosc.EntityTrigger(
                "NearWorkZone", 0, xosc.ConditionEdge.none, distance, "Car2"
            )
        )
        event.add_action(
            "EnterTemporaryLane",
            xosc.AbsoluteLaneChangeAction(
                -1,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.cubic, xosc.DynamicsDimension.time, 2
                ),
                layer=xosc.LaneLayerType.temporary,
            ),
        )
        maneuver = xosc.Maneuver("LaneChangeManeuver").add_event(event)
        group = (
            xosc.ManeuverGroup("Car2Maneuvers")
            .add_actor("Car2")
            .add_maneuver(maneuver)
        )
        act = xosc.Act("LaneChangeAct").add_maneuver_group(group)
        story = xosc.Story("LaneChangeStory").add_act(act)
        stop = xosc.ValueTrigger(
            "Quit",
            0,
            xosc.ConditionEdge.none,
            xosc.SimulationTimeCondition(10, xosc.Rule.greaterOrEqual),
            "stop",
        )
        storyboard = xosc.StoryBoard(init, stop).add_story(story)
        return xosc.Scenario(
            "Roadworks with permanent and temporary lanes",
            "scenariogeneration",
            xosc.ParameterDeclarations(),
            entities,
            storyboard,
            xosc.RoadNetwork(roadfile=self.road_file),
            xosc.Catalog(),
            osc_minor_version=4,
        )


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", default="generated_roadworks")
    scenario_path, road_path = Scenario().generate(parser.parse_args().output)
    print(scenario_path[0])
    print((Path(scenario_path[0]).parent / road_path[0]).resolve())
