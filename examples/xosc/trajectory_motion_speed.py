"""Drive a timed polyline with OpenSCENARIO 1.4 longitudinal speed samples.

Run with `python -m examples.xosc.trajectory_motion_speed [output]`.

esmini 3.12.1 follows the vertex timings, not the Motion speed samples.
The successive segment lengths still give a visible change in speed.
"""

from argparse import ArgumentParser

from scenariogeneration import ScenarioGenerator, xodr, xosc


class Scenario(ScenarioGenerator):
    def road(self, **kwargs):
        road = xodr.create_road(xodr.Line(120), 1, left_lanes=0, right_lanes=1)
        network = xodr.OpenDrive("Motion speed example").add_road(road)
        network.adjust_roads_and_lanes()
        return network

    def scenario(self, **kwargs):
        car = xosc.Vehicle(
            "Car",
            xosc.VehicleCategory.car,
            xosc.BoundingBox(1.8, 4.5, 1.5, 1.3, 0, 0.75),
            xosc.Axle(0.5, 0.65, 1.6, 2.8, 0.35),
            xosc.Axle(0, 0.65, 1.6, 0, 0.35),
            69,
            10,
            10,
        )
        car.add_property("model_id", "0")
        entities = xosc.Entities().add_scenario_object("Car", car)

        times = [0, 2, 4, 6, 8]
        positions = [
            xosc.LanePosition(station, 0, -1, 1)
            for station in (10, 22, 42, 62, 74)
        ]
        motions = [
            xosc.Motion(speed_longitudinal=speed) for speed in (4, 8, 12, 8, 4)
        ]
        trajectory = xosc.Trajectory("SpeedProfile", False).add_shape(
            xosc.Polyline(times, positions, motions=motions)
        )
        follow = xosc.FollowTrajectoryAction(
            trajectory,
            xosc.FollowingMode.position,
            xosc.ReferenceContext.relative,
            1,
            0,
        )

        init = xosc.Init()
        init.add_init_action("Car", xosc.TeleportAction(positions[0]))
        start = xosc.ValueTrigger(
            "StartProfile",
            0,
            xosc.ConditionEdge.none,
            xosc.SimulationTimeCondition(0, xosc.Rule.greaterOrEqual),
        )
        event = xosc.Event("DriveProfile", xosc.Priority.override)
        event.add_trigger(start)
        event.add_action("FollowSpeedProfile", follow)
        maneuver = xosc.Maneuver("MotionManeuver").add_event(event)
        group = (
            xosc.ManeuverGroup("CarManeuvers")
            .add_actor("Car")
            .add_maneuver(maneuver)
        )
        act = xosc.Act("MotionAct").add_maneuver_group(group)
        story = xosc.Story("MotionStory").add_act(act)
        stop = xosc.ValueTrigger(
            "Quit",
            0,
            xosc.ConditionEdge.none,
            xosc.SimulationTimeCondition(8, xosc.Rule.greaterOrEqual),
            "stop",
        )
        storyboard = xosc.StoryBoard(init, stop).add_story(story)
        return xosc.Scenario(
            "Polyline with longitudinal speeds",
            "scenariogeneration",
            xosc.ParameterDeclarations(),
            entities,
            storyboard,
            xosc.RoadNetwork(roadfile=self.road_file),
            xosc.Catalog(),
        )


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", default="generated_motion")
    scenario_paths, _ = Scenario().generate(parser.parse_args().output)
    print(scenario_paths[0])
