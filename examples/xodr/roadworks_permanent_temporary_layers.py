"""A two-lane roadworks diversion over a permanent motorway layout.

Based on esmini's roadworks_permanent_temporary_layers.xodr:
https://github.com/esmini/esmini/blob/master/resources/xodr/roadworks_permanent_temporary_layers.xodr
"""

from math import pi

from scenariogeneration import ScenarioGenerator, xodr

ROAD_LENGTH = 400
WORK_START, TAPER_IN_END, TAPER_OUT_START, WORK_END = 40, 60, 340, 360
PERMANENT = xodr.LaneLayer.permanent
TEMPORARY = xodr.LaneLayer.temporary


def _permanent_lanes() -> xodr.Lanes:
    lane_layout = (
        (xodr.LaneType.shoulder, 2.0, xodr.RoadMarkType.none),
        (xodr.LaneType.border, 0.75, xodr.RoadMarkType.solid),
        (xodr.LaneType.driving, 3.75, xodr.RoadMarkType.broken),
        (xodr.LaneType.driving, 3.75, xodr.RoadMarkType.solid),
        (xodr.LaneType.border, 0.75, xodr.RoadMarkType.none),
        (xodr.LaneType.stop, 3.0, xodr.RoadMarkType.none),
        (xodr.LaneType.shoulder, 1.5, xodr.RoadMarkType.none),
    )
    lanes = xodr.Lanes(layer=PERMANENT)
    for start in (0, WORK_START, TAPER_IN_END, TAPER_OUT_START, WORK_END):
        section = xodr.LaneSection(start, xodr.Lane(xodr.LaneType.none))
        for lane_index, (lane_type, width, marking) in enumerate(
            lane_layout, 1
        ):
            for side, add_lane in (
                (1, section.add_left_lane),
                (-1, section.add_right_lane),
            ):
                lane = xodr.Lane(lane_type, a=width)
                if marking != xodr.RoadMarkType.none:
                    lane.add_roadmark(
                        xodr.RoadMark(marking, color=xodr.RoadMarkColor.white)
                    )
                lane_id = side * lane_index
                if start > 0:
                    lane.add_link("predecessor", lane_id, layer=PERMANENT)
                if start < WORK_END:
                    lane.add_link("successor", lane_id, layer=PERMANENT)
                if start in (0, WORK_START) and lane_id in (-3, -4):
                    lane.add_link("successor", lane_id + 2, layer=TEMPORARY)
                add_lane(lane)
        lanes.add_lanesection(section)
    return lanes


def _taper(
    start: float, end: float, length: float
) -> tuple[float, float, float, float]:
    """Return a cubic transition with zero slope at both ends."""
    delta = end - start
    return start, 0.0, 3 * delta / length**2, -2 * delta / length**3


def _temporary_lanes() -> xodr.Lanes:
    lanes = xodr.Lanes(layer=TEMPORARY)
    for start, offset_start, offset_end, width_start, width_end, length in (
        (WORK_START, -2.8, -4.35, 3.75, 3.5, TAPER_IN_END - WORK_START),
        (TAPER_IN_END, -4.35, -4.35, 3.5, 3.5, TAPER_OUT_START - TAPER_IN_END),
        (TAPER_OUT_START, -4.35, -2.8, 3.5, 3.75, WORK_END - TAPER_OUT_START),
    ):
        lanes.add_laneoffset(
            xodr.LaneOffset(start, *_taper(offset_start, offset_end, length))
        )
        center = xodr.Lane(xodr.LaneType.none).add_roadmark(
            _temporary_marking(broken=False)
        )
        section = xodr.LaneSection(start, center, length=length)
        for lane_id in (-1, -2):
            lane = xodr.Lane(
                xodr.LaneType.driving, *_taper(width_start, width_end, length)
            )
            lane.add_roadmark(_temporary_marking(broken=lane_id == -1))
            lane.add_link("predecessor", lane_id, layer=TEMPORARY)
            if start == TAPER_OUT_START:
                lane.add_link("successor", lane_id - 2, layer=PERMANENT)
            else:
                lane.add_link("successor", lane_id, layer=TEMPORARY)
            section.add_right_lane(lane)
        lanes.add_lanesection(section)
    lanes.add_laneoffset(xodr.LaneOffset(WORK_END, -2.8))
    return lanes


def _temporary_marking(broken: bool) -> xodr.RoadMark:
    return xodr.RoadMark(
        xodr.RoadMarkType.broken if broken else xodr.RoadMarkType.solid,
        color=xodr.RoadMarkColor.yellow,
        marking_weight=(
            xodr.RoadMarkWeight.standard
            if broken
            else xodr.RoadMarkWeight.bold
        ),
        height=0.02,
    )


def _add_delineators(road: xodr.Road) -> None:
    positions = (WORK_START, 50, TAPER_IN_END, 350, WORK_END)
    for offsets, heading, repeat_offset, first_id in (
        ((-2.5, -3.25, -4, -3.25, -2.5), 0, -4, 9),
        ((-10.6, -11.15, -12.1, -11.15, -10.6), pi, -11.7, 14),
    ):
        for object_id, (position, offset) in enumerate(
            zip(positions, offsets), first_id
        ):
            delineator = xodr.Object(
                position,
                offset,
                Type=xodr.ObjectType.obstacle,
                subtype="delineator",
                name="road_delineator",
                id=str(object_id),
                hdg=heading,
                temporary=True,
            )
            if position == TAPER_IN_END:
                delineator.repeat(
                    TAPER_OUT_START - TAPER_IN_END,
                    10,
                    tStart=repeat_offset,
                    tEnd=repeat_offset,
                    heightStart=1.275,
                    heightEnd=1.275,
                    widthStart=0.4,
                    widthEnd=0.4,
                    lengthStart=0.6,
                    lengthEnd=0.6,
                )
            road.add_object(delineator)


class Scenario(ScenarioGenerator):
    def road(self, **kwargs):
        planview = xodr.PlanView(-100, 0, 0).add_geometry(
            xodr.Line(ROAD_LENGTH)
        )
        road = xodr.Road(1, planview, _permanent_lanes())
        road.add_temporary_lanes(_temporary_lanes())
        road.add_elevation(0, 0, 0, 0, 0)
        _add_delineators(road)
        network = xodr.OpenDrive(
            "Roadworks with permanent and temporary lanes"
        )
        network.add_road(road)
        network.adjust_roads_and_lanes()
        return network


if __name__ == "__main__":
    Scenario().generate(".")
