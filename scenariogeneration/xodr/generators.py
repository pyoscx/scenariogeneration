"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

"""
This module provides a collection of ready-to-use functions to generate
standard road snippets, including:

- Simple straight roads.
- Spiral-Arc-Spiral type of turns.
- Simple roads with different geometries and lanes.
- Simple junction roads, limited to 3/4-way crossings with 90-degree
  turns (3-way crossings can also be 120 degrees).
- Creation of junctions based on connecting roads and incoming/outgoing
  roads.

"""
from typing import List, Optional, Union
from warnings import warn

import numpy as np
import pyclothoids as pcloth

from .enumerations import (
    ContactPoint,
    ElementType,
    JunctionType,
    MarkRule,
    ObjectType,
    RoadMarkType,
)
from .exceptions import (
    GeneralIssueInputArguments,
    NotSameAmountOfLanesError,
    RemovedFunctionality,
)
from .geometry import AdjustablePlanview, Arc, Line, PlanView, Spiral
from .lane import Lane, Lanes, LaneSection, RoadLine, RoadMark
from .lane_def import (
    LaneDef,
    create_lanes_merge_split,
    std_roadmark_broken,
    std_roadmark_broken_broken,
    std_roadmark_broken_long_line,
    std_roadmark_broken_solid,
    std_roadmark_broken_tight,
    std_roadmark_solid,
    std_roadmark_solid_broken,
    std_roadmark_solid_solid,
)
from .links import Connection, Junction, LaneLinker, _get_related_lanesection
from .opendrive import Road

STD_START_CLOTH = 1 / 1000000000


def standard_lane(
    offset: int = 3, rm: RoadMark = std_roadmark_broken()
) -> Lane:
    """Create a simple lane with an offset and a roadmark.

    Parameters
    ----------
    offset : int, optional
        Width of the lane. Default is 3.
    rm : RoadMark, optional
        Road mark used for the standard lane. Default is RoadMark(solid).

    Returns
    -------
    Lane
        The created lane.
    """
    lc = Lane(a=offset)
    if rm is not None:
        lc.add_roadmark(rm)
    return lc


def create_road(
    geometry: Union[
        Line,
        Spiral,
        "ParamPoly3",
        Arc,
        List[Union[Line, Spiral, "ParamPoly3", Arc]],
        AdjustablePlanview,
    ],
    id: int,
    left_lanes: Union[List[LaneDef], int] = 1,
    right_lanes: Union[List[LaneDef], int] = 1,
    road_type: int = -1,
    center_road_mark: RoadMark = std_roadmark_solid(),
    lane_width: float = 3,
    lane_width_end: Optional[float] = None,
) -> Road:
    """Create a road with one lane section and different numbers of lanes.

    Lane marks will be of type broken, except for the outer lane, which
    will be solid. The `lane_width_end` parameter can only be used when
    inputs for `left_lanes` and `right_lanes` are integers.

    Parameters
    ----------
    geometry : Line, Spiral, ParamPoly3, Arc, list of (Line, Spiral,
               ParamPoly3, Arc), or AdjustablePlanview
        Geometries to build the road.
    id : int
        ID of the new road.
    left_lanes : list of LaneDef or int, optional
        A list of the splits/merges that are wanted on the left side of
        the road. If an integer, it specifies a constant number of
        lanes. Default is 1.
    right_lanes : list of LaneDef or int, optional
        A list of the splits/merges that are wanted on the right side of
        the road. If an integer, it specifies a constant number of
        lanes. Default is 1.
    road_type : int, optional
        Type of road. Use -1 for a normal road, or another value for a
        connecting road. Default is -1.
    center_road_mark : RoadMark, optional
        Road mark for the center line. Default is RoadMark(solid).
    lane_width : float, optional
        The width of all lanes. Default is 3.
    lane_width_end : float, optional
        The end width of all lanes. Can only be used when `left_lanes`
        and `right_lanes` are integers.

    Returns
    -------
    Road
        A straight road.
    """

    if isinstance(left_lanes, LaneDef):
        left_lanes = [left_lanes]
    if isinstance(right_lanes, LaneDef):
        right_lanes = [right_lanes]

    pv = PlanView()
    raw_length = 0
    if isinstance(geometry, list):
        for g in geometry:
            pv.add_geometry(g)
            raw_length += g.length
    elif isinstance(geometry, AdjustablePlanview):
        pv = geometry
        pv.left_lane_defs = left_lanes
        pv.right_lane_defs = right_lanes
        pv.center_road_mark = center_road_mark
        pv.lane_width = lane_width
        pv.lane_width_end = lane_width_end
        # create a dummy length
        raw_length = 0

        if isinstance(left_lanes, list) and any(
            isinstance(x, LaneDef) for x in left_lanes
        ):
            raw_length = max(raw_length, max([x.s_end for x in left_lanes]))
        if isinstance(right_lanes, list) and any(
            isinstance(x, LaneDef) for x in right_lanes
        ):
            raw_length = max(raw_length, max([x.s_end for x in right_lanes]))
        if raw_length == 0:
            raw_length = 100  # just a dummy value
    else:
        pv.add_geometry(geometry)
        raw_length += geometry.length

    if (lane_width_end is not None) and (
        (type(left_lanes) != int) or (type(right_lanes) != int)
    ):
        raise RuntimeError(
            "lane_width_end can only be used when left_lanes and right_lanes are int"
        )
    if (
        right_lanes is not None
        and left_lanes is not None
        or center_road_mark is not None
    ):
        lanes = create_lanes_merge_split(
            right_lanes,
            left_lanes,
            raw_length,
            center_road_mark,
            lane_width,
            lane_width_end=lane_width_end,
        )
    else:
        lanes = Lanes()

    road = Road(id, pv, lanes, road_type=road_type)

    return road


def create_straight_road(
    road_id: int,
    length: float = 100,
    junction: int = -1,
    n_lanes: int = 1,
    lane_offset: int = 3,
) -> Road:
    """Create a standard straight road with two lanes.

    Parameters
    ----------
    road_id : int
        ID of the road to create.
    length : float, optional
        Length of the road. Default is 100.
    junction : int, optional
        Indicates if the road belongs to a junction. Default is -1.
    n_lanes : int, optional
        Number of lanes. Default is 1.
    lane_offset : int, optional
        Width of the road. Default is 3.

    Returns
    -------
    Road
        A straight road.
    """
    warn(
        "create_straight_road should not be used anymore, please use the create_road function instead",
        DeprecationWarning,
        2,
    )
    # create geometry
    line1 = Line(length)

    # create planviews
    planview1 = PlanView()
    planview1.add_geometry(line1)

    # create lanesections
    lanesec1 = LaneSection(0, standard_lane())
    for i in range(1, n_lanes + 1, 1):
        lanesec1.add_right_lane(standard_lane(lane_offset))
        lanesec1.add_left_lane(standard_lane(lane_offset))

    # create lanes
    lanes1 = Lanes()
    lanes1.add_lanesection(lanesec1)

    # finally create the roads
    return Road(road_id, planview1, lanes1, road_type=junction)


def create_cloth_arc_cloth(
    arc_curv: float,
    arc_angle: float,
    cloth_angle: float,
    r_id: int,
    junction: int = 1,
    cloth_start: float = STD_START_CLOTH,
    n_lanes: int = 1,
    lane_offset: int = 3,
):
    """Create a curved road with a Spiral-Arc-Spiral and two lanes.

    Parameters
    ----------
    arc_curv : float
        Curvature of the arc (and max clothoid of clothoids).
    arc_angle : float
        How much of the curve should be the arc.
    cloth_angle : float
        How much of the curve should be the clothoid (will be doubled
        since there are two clothoids).
    r_id : int
        The ID of the road.
    junction : int, optional
        Indicates if the road belongs to a junction. Default is 1.
    cloth_start : float, optional
        Starting curvature of clothoids. Default is 1 / 1000000000.
    n_lanes : int, optional
        Number of lanes. Default is 1.
    lane_offset : int, optional
        Width of the road. Default is 3.

    Returns
    -------
    Road
        A road built up of a Spiral-Arc-Spiral.
    """
    warn(
        "create_cloth_arc_cloth should not be used anymore, please use the create_road (see exampels/xodr/clothoid_generation.py) function instead",
        DeprecationWarning,
        2,
    )
    pv = PlanView()
    # adjust sign if angle is negative
    if cloth_angle < 0 and arc_curv > 0:
        cloth_angle = -cloth_angle
        arc_curv = -arc_curv
        cloth_start = -cloth_start
        arc_angle = -arc_angle

    # create geometries
    spiral1 = Spiral(cloth_start, arc_curv, angle=cloth_angle)
    arc = Arc(arc_curv, angle=arc_angle)
    spiral2 = Spiral(arc_curv, cloth_start, angle=cloth_angle)

    pv.add_geometry(spiral1)
    pv.add_geometry(arc)
    pv.add_geometry(spiral2)

    # create lanes
    lsec = LaneSection(0, standard_lane())
    for i in range(1, n_lanes + 1, 1):
        lsec.add_right_lane(standard_lane(lane_offset))
        lsec.add_left_lane(standard_lane(lane_offset))
    lanes = Lanes()
    lanes.add_lanesection(lsec)

    # create road
    return Road(r_id, pv, lanes, road_type=junction)


def create_3cloths(
    cloth1_start: float,
    cloth1_end: float,
    cloth1_length: float,
    cloth2_start: float,
    cloth2_end: float,
    cloth2_length: float,
    cloth3_start: float,
    cloth3_end: float,
    cloth3_length: float,
    r_id: int,
    junction: int = 1,
    n_lanes: int = 1,
    lane_offset: int = 3,
    road_marks: RoadMark = std_roadmark_broken(),
):
    """Create a curved road with a Spiral-Spiral-Spiral and two lanes.

    Parameters
    ----------
    cloth1_start : float
        Initial curvature of spiral 1.
    cloth1_end : float
        Ending curvature of spiral 1.
    cloth1_length : float
        Total length of spiral 1.
    cloth2_start : float
        Initial curvature of spiral 2.
    cloth2_end : float
        Ending curvature of spiral 2.
    cloth2_length : float
        Total length of spiral 2.
    cloth3_start : float
        Initial curvature of spiral 3.
    cloth3_end : float
        Ending curvature of spiral 3.
    cloth3_length : float
        Total length of spiral 3.
    r_id : int
        The ID of the road.
    junction : int, optional
        Indicates if the road belongs to a junction. Default is 1.
    n_lanes : int, optional
        Number of lanes. Default is 1.
    lane_offset : int, optional
        Width of the road. Default is 3.
    road_marks : RoadMark, optional
        Road mark used for the standard lane. Default is RoadMark(broken).

    Returns
    -------
    Road
        A road built up of a Spiral-Spiral-Spiral.
    """
    warn(
        "create_cloth_arc_cloth should not be used anymore, please use the create_road (see exampels/xodr/clothoid_generation.py) function instead",
        DeprecationWarning,
        2,
    )
    pv = PlanView()

    # create geometries
    spiral1 = Spiral(cloth1_start, cloth1_end, length=cloth1_length)
    spiral2 = Spiral(cloth2_start, cloth2_end, length=cloth2_length)
    spiral3 = Spiral(cloth3_start, cloth3_end, length=cloth3_length)

    pv.add_geometry(spiral1)
    pv.add_geometry(spiral2)
    pv.add_geometry(spiral3)

    # create lanes
    center_lane = Lane()
    if road_marks:
        center_lane.add_roadmark(road_marks)
    lsec = LaneSection(0, center_lane)

    for i in range(1, n_lanes + 1, 1):
        rl = Lane(a=lane_offset)
        ll = Lane(a=lane_offset)
        if road_marks:
            rl.add_roadmark(road_marks)
            ll.add_roadmark(road_marks)
        lsec.add_right_lane(rl)
        lsec.add_left_lane(ll)
    lanes = Lanes()
    lanes.add_lanesection(lsec)

    # create road
    return Road(r_id, pv, lanes, road_type=junction)


def get_lanes_offset(
    road1: Road, road2: Road, contactpoint: ContactPoint
) -> tuple[int, int]:
    """Return the number of lanes and their offset.

    Assumes that the number of left lanes equals the number of right
    lanes and that the offset is constant.

    Parameters
    ----------
    road1 : Road
        The first road.
    road2 : Road
        The second road.
    contactpoint : ContactPoint
        The contact point indicating the connection type.

    Returns
    -------
    tuple[int, int]
        A tuple containing:
        - n_lanes (int): The number of lanes.
        - lane_offset (int): The offset of the lanes.

    Raises
    ------
    NotSameAmountOfLanesError
        If the incoming and outgoing roads do not have the same number of left lanes.
    """

    # now we always look at lanesection[0] to take the number of lanes
    # TO DO - understand if the roads are connect through end or start and then take the relative lane section
    if contactpoint == ContactPoint.end:
        n_lanesection = 0
    else:
        n_lanesection = -1
    if len(road1.lanes.lanesections[n_lanesection].leftlanes) == len(
        road2.lanes.lanesections[0].leftlanes
    ) and len(road1.lanes.lanesections[n_lanesection].rightlanes) == len(
        road2.lanes.lanesections[0].rightlanes
    ):
        n_lanes = len(road1.lanes.lanesections[n_lanesection].leftlanes)
        lane_offset = (
            road1.lanes.lanesections[n_lanesection].leftlanes[0].widths[0].a
        )
    else:
        raise NotSameAmountOfLanesError(
            "Incoming road ",
            road1.id,
            " and outcoming road ",
            road2.id,
            "do not have the same number of left lanes.",
        )

    return n_lanes, lane_offset


def create_junction_roads_standalone(
    angles: List[float],
    r: float,
    junction: int = 1,
    spiral_part: float = 1 / 3,
    arc_part: float = 1 / 3,
    startnum: int = 100,
    n_lanes: int = 1,
    lane_width: float = 3,
) -> List[Road]:
    """Create all needed roads for simple junctions.

    The curved parts of the junction are created as a spiral-arc-spiral
    combination. Supported junctions include:
    - 3-way crossings (either a T-junction or 120-degree junction).
    - 4-way crossings (all 90-degree turns).

    Note
    ----
    This function does not generate any links or add any successors/
    predecessors to the roads. These must be added manually. If you
    have the connecting roads, use `create_junction_roads` instead.

    Parameters
    ----------
    angles : list of float
        The angles from where the roads should be coming in (see
        description for what is supported). Angles should be defined in
        mathematically positive order, beginning with the first incoming
        road.
    r : float
        The radius of the arcs in the junction (determines the size of
        the junction).
    junction : int, optional
        The ID of the junction. Default is 1.
    spiral_part : float, optional
        The part of the curve that should be spirals (two of these).
        `spiral_part * 2 + arc_part = angle of the turn`. Default is
        1/3.
    arc_part : float, optional
        The part of the curve that should be an arc.
        `spiral_part * 2 + arc_part = angle of the turn`. Default is
        1/3.
    startnum : int, optional
        Start number of the roads in the junction (will increase by 1
        for each road). Default is 100.
    n_lanes : int, optional
        The number of lanes in the junction. Default is 1.
    lane_width : float, optional
        The lane width of the lanes in the junction. Default is 3.

    Returns
    -------
    list of Road
        A list of all roads in a junction without connections added.
    """
    warn(
        "create_junction_roads_standalone should not be used anymore, please use the CommonJunctionCreator function instead",
        DeprecationWarning,
        2,
    )
    angle = np.pi / 2
    angle_cloth = angle * spiral_part
    spiral_length = 2 * abs(angle_cloth * r)

    cloth = pcloth.Clothoid.StandardParams(
        0,
        0,
        0,
        STD_START_CLOTH,
        (1 / r - STD_START_CLOTH) / spiral_length,
        spiral_length,
    )

    X0 = cloth.XEnd - r * np.sin(angle_cloth)
    Y0 = cloth.YEnd - r * (1 - np.cos(angle_cloth))
    linelength = 2 * (X0 + r + Y0)

    junction_roads = []

    for i in range(len(angles) - 1):
        for j in range(1 + i, len(angles)):
            # check angle needed for junction
            an = np.sign(angles[j] - angles[i] - np.pi)
            an1 = angles[j] - angles[i] - np.pi
            angle_arc = an1 * arc_part

            angle_cloth = an1 * spiral_part

            # adjust angle if multiple of pi
            if an1 > np.pi:
                an1 = -(2 * np.pi - an1)

            # create road, either straight or curved
            if an == 0:
                tmp_junc = create_straight_road(
                    startnum,
                    length=linelength,
                    junction=junction,
                    n_lanes=n_lanes,
                    lane_offset=lane_width,
                )
            else:
                tmp_junc = create_cloth_arc_cloth(
                    1 / r,
                    angle_arc,
                    angle_cloth,
                    startnum,
                    junction,
                    n_lanes=n_lanes,
                    lane_offset=lane_width,
                )

            # add predecessor and successor
            startnum += 1
            junction_roads.append(tmp_junc)

    return junction_roads


def create_junction_roads_from_arc(
    roads: List[Road],
    angles: List[float],
    r: float = 0,
    junction: int = 1,
    arc_part: float = 1 / 3,
    startnum: int = 100,
) -> List[Road]:
    """Create all needed roads for simple junctions.

    The curved parts of the junction are created as a spiral-arc-spiral
    combination. Supported junctions include:
    - 3-way crossings (either a T-junction or 120-degree junction).
    - 4-way crossings (all 90-degree turns).

    Parameters
    ----------
    roads : list of Road
        All roads that should go into the junction.
    angles : list of float
        The angles from where the roads should be coming in (see
        description for what is supported). Angles should be defined in
        mathematically positive order, beginning with the first incoming
        road [0, +2π].
    r : float
        The radius of the arcs in the junction (determines the size of
        the junction).
    junction : int, optional
        The ID of the junction. Default is 1.
    arc_part : float, optional
        The part of the curve that should be an arc:
        `spiral_part * 2 + arc_part = angle of the turn`. Default is 1/3.
    startnum : int, optional
        Start number of the roads in the junction (will increase by 1
        for each road). Default is 100.

    Returns
    -------
    list of Road
        A list of all roads needed for all traffic connecting the roads.
    """
    warn(
        "create_junction_roads_from_arc should not be used anymore, please use the CommonJunctionCreator function instead",
        DeprecationWarning,
        2,
    )
    # arc_part = 1 - 2*spiral_part
    spiral_part = (1 - arc_part) / 2

    angle = np.pi / 2
    angle_cloth = angle * spiral_part
    spiral_length = 2 * abs(angle_cloth * r)

    cloth = pcloth.Clothoid.StandardParams(
        0,
        0,
        0,
        STD_START_CLOTH,
        (1 / r - STD_START_CLOTH) / spiral_length,
        spiral_length,
    )

    X0 = cloth.XEnd - r * np.sin(angle_cloth)
    Y0 = cloth.YEnd - r * (1 - np.cos(angle_cloth))

    linelength = 2 * (X0 + r + Y0)

    junction_roads = []

    # loop over the roads to get all possible combinations of connecting roads
    for i in range(len(roads) - 1):
        # for now the first road is place as base,
        if i == 0:
            cp = ContactPoint.end
            roads[i].add_successor(ElementType.junction, junction)
        else:
            cp = ContactPoint.start
            roads[i].add_predecessor(ElementType.junction, junction)

        for j in range(1 + i, len(roads)):
            # check angle needed for junction [-pi, +pi]
            an1 = angles[j] - angles[i] - np.pi
            # adjust angle if multiple of pi
            if an1 > np.pi:
                an1 = -(2 * np.pi - an1)

            angle_arc = an1 * arc_part
            angle_cloth = an1 * spiral_part

            sig = np.sign(an1)

            # create road, either straight or curved
            n_lanes, lanes_offset = get_lanes_offset(roads[i], roads[j], cp)
            if sig == 0:
                # create straight road
                tmp_junc = create_straight_road(
                    startnum,
                    length=linelength,
                    junction=junction,
                    n_lanes=n_lanes,
                    lane_offset=lanes_offset,
                )
            else:
                # create the cloth-arc-cloth road given the radius fo the arc
                tmp_junc = create_cloth_arc_cloth(
                    1 / r,
                    angle_arc,
                    angle_cloth,
                    startnum,
                    junction,
                    n_lanes=n_lanes,
                    lane_offset=lanes_offset,
                )

            # add predecessor and successor
            tmp_junc.add_predecessor(ElementType.road, roads[i].id, cp)
            tmp_junc.add_successor(
                ElementType.road, roads[j].id, ContactPoint.start
            )
            startnum += 1
            junction_roads.append(tmp_junc)

    # add junction to the last road aswell since it's not part of the loop
    roads[-1].add_predecessor(ElementType.junction, junction)

    return junction_roads


def create_junction_roads(
    roads: List[Road],
    angles: List[float],
    R: Union[float, List[float]],
    junction: int = 1,
    arc_part: float = 1 / 3,
    startnum: int = 100,
    inner_road_marks: Optional[RoadMark] = None,
    outer_road_marks: RoadMark = std_roadmark_solid(),
) -> List[Road]:
    """Create all needed roads for some simple junctions.

    The curved parts of the junction are created as a spiral-arc-spiral
    combination. `R` is the radius of the whole junction, meaning the
    distance between the center of the junction and any external road
    attached to the junction. Supports all angles and numbers of roads.

    Parameters
    ----------
    roads : list of Road
        All roads that should go into the junction.
    angles : list of float
        The angles from where the roads should be coming in (see
        description for what is supported). Angles should be defined in
        mathematically positive order, beginning with the first incoming
        road [0, +2π].
    R : list of float
        The radius of the whole junction, meaning the distance between
        roads and the center of the junction. If only one value is
        specified, then all roads will have the same distance.
    junction : int, optional
        The ID of the junction. Default is 1.
    spiral_part : float, optional
        The part of the curve that should be spirals (two of these).
        `spiral_part * 2 + arc_part = angle of the turn`. Default is 1/3.
    startnum : int, optional
        Start number of the roads in the junction (will increase by 1
        for each road). Default is 100.
    inner_road_marks : RoadMark, optional
        The RoadMark that all lanes inside the junction will have
        (outer will be solid). Default is None.
    outer_road_marks : RoadMark, optional
        The RoadMark that will be on the edge of the connecting roads
        (limits the junction). Default is std_roadmark_solid().

    Returns
    -------
    list of Road
        A list of all roads needed for all traffic connecting the roads.
    """
    warn(
        "create_junction_roads_from_arc should not be used anymore, please use the CommonJunctionCreator function instead",
        DeprecationWarning,
        2,
    )
    if len(roads) is not len(angles):
        raise GeneralIssueInputArguments(
            "roads and angles do not have the same size."
        )

    if len(R) == 1:
        R = R * np.ones(len(roads))
    elif len(R) > 1 and len(R) is not len(roads):
        raise GeneralIssueInputArguments(
            "roads and R do not have the same size."
        )

    # linelength = 2*R
    junction_roads = []

    # loop over the roads to get all possible combinations of connecting roads
    for i in range(len(roads) - 1):
        # for now the first road is place as base,
        if i == 0:
            cp = ContactPoint.end
            roads[i].add_successor(ElementType.junction, junction)
        else:
            cp = ContactPoint.start
            roads[i].add_predecessor(ElementType.junction, junction)

        for j in range(1 + i, len(roads)):
            # check angle needed for junction [-pi, +pi]
            an1 = angles[j] - angles[i] - np.pi
            # adjust angle if multiple of pi
            if an1 > np.pi:
                an1 = -(2 * np.pi - an1)

            sig = np.sign(an1)

            # create road, either straight or curved
            n_lanes, lanes_offset = get_lanes_offset(roads[i], roads[j], cp)
            if sig == 0:
                # create straight road
                linelength = R[i] + R[j]
                tmp_junc = create_straight_road(
                    startnum,
                    length=linelength,
                    junction=junction,
                    n_lanes=n_lanes,
                    lane_offset=lanes_offset,
                )
                if inner_road_marks:
                    for l in tmp_junc.lanes.lanesections[0].leftlanes:
                        l.roadmark[0] = inner_road_marks
                    for r in tmp_junc.lanes.lanesections[0].rightlanes:
                        r.roadmark[0] = inner_road_marks
                    tmp_junc.lanes.lanesections[0].centerlane.roadmark[
                        0
                    ] = inner_road_marks
                if len(roads) == 3:
                    # not sure all will be needed since angles have to be in increasing order, but it "should work"
                    k = [x for x in [0, 1, 2] if x != j and x != i][0]
                    if (angles[i] > angles[j]) and (
                        (angles[k] > angles[j]) or (angles[k] < angles[i])
                    ):
                        tmp_junc.lanes.lanesections[0].rightlanes[-1].roadmark[
                            0
                        ] = outer_road_marks
                    elif (angles[i] < angles[j]) and (
                        (angles[k] > angles[j]) or (angles[k] < angles[i])
                    ):
                        tmp_junc.lanes.lanesections[0].rightlanes[-1].roadmark[
                            0
                        ] = outer_road_marks
                    elif (angles[i] < angles[j]) and (
                        (angles[k] < angles[j]) or (angles[k] > angles[i])
                    ):
                        tmp_junc.lanes.lanesections[0].leftlanes[-1].roadmark[
                            0
                        ] = outer_road_marks
                    else:
                        tmp_junc.lanes.lanesections[0].rightlanes[-1].roadmark[
                            0
                        ] = outer_road_marks
            else:
                clothoids = pcloth.SolveG2(
                    -R[i],
                    0,
                    0,
                    STD_START_CLOTH,
                    R[j] * np.cos(an1),
                    R[j] * np.sin(an1),
                    an1,
                    STD_START_CLOTH,
                )
                tmp_junc = create_3cloths(
                    clothoids[0].KappaStart,
                    clothoids[0].KappaEnd,
                    clothoids[0].length,
                    clothoids[1].KappaStart,
                    clothoids[1].KappaEnd,
                    clothoids[1].length,
                    clothoids[2].KappaStart,
                    clothoids[2].KappaEnd,
                    clothoids[2].length,
                    startnum,
                    junction,
                    n_lanes=n_lanes,
                    lane_offset=lanes_offset,
                    road_marks=inner_road_marks,
                )

                if tmp_junc.planview._raw_geometries[1].curvstart > 0:
                    tmp_junc.lanes.lanesections[0].leftlanes[-1].add_roadmark(
                        outer_road_marks
                    )
                if tmp_junc.planview._raw_geometries[1].curvstart < 0:
                    tmp_junc.lanes.lanesections[0].rightlanes[-1].add_roadmark(
                        outer_road_marks
                    )
            # add predecessor and successor
            tmp_junc.add_predecessor(ElementType.road, roads[i].id, cp)
            tmp_junc.add_successor(
                ElementType.road, roads[j].id, ContactPoint.start
            )
            startnum += 1
            junction_roads.append(tmp_junc)

    # add junction to the last road aswell since it's not part of the loop
    roads[-1].add_predecessor(ElementType.junction, junction)

    return junction_roads


def _create_junction_links(
    connection: Connection,
    nlanes: int,
    r_or_l: int,
    sign: int,
    from_offset: int = 0,
    to_offset: int = 0,
) -> None:
    """Helper function to create junction links.

    Parameters
    ----------
    connection : Connection
        The connection to fill.
    nlanes : int
        Number of lanes.
    r_or_l : {1, -1}
        Indicates if the lane should start from -1 or 1.
    sign : {1, -1}
        Indicates if the sign should change.
    from_offset : int, optional
        Offset at the beginning of the road. Default is 0.
    to_offset : int, optional
        Offset at the end of the road. Default is 0.

    Returns
    -------
    None
    """
    for i in range(1, nlanes + 1, 1):
        connection.add_lanelink(
            r_or_l * i + from_offset, r_or_l * sign * i + to_offset
        )


def create_junction(
    junction_roads: List[Road],
    id: int,
    roads: List[Road],
    name: str = "my junction",
) -> Junction:
    """Create a junction structure for a set of roads.

    Parameters
    ----------
    junction_roads : list of Road
        All connecting roads in the junction.
    id : int
        The ID of the junction.
    roads : list of Road
        All incoming roads to the junction.
    name : str, optional
        Name of the junction. Default is "my junction".

    Returns
    -------
    Junction
        The junction structure ready to use.
    """
    junc = Junction(name, id)

    for jr in junction_roads:
        # handle succesor lanes
        conne1 = Connection(jr.successor.element_id, jr.id, ContactPoint.end)
        _, sign, _ = _get_related_lanesection(
            jr, get_road_by_id(roads, jr.successor.element_id)
        )

        _create_junction_links(
            conne1,
            len(jr.lanes.lanesections[-1].rightlanes),
            -1,
            sign,
            to_offset=jr.lane_offset_suc[str(jr.successor.element_id)],
        )
        _create_junction_links(
            conne1,
            len(jr.lanes.lanesections[-1].leftlanes),
            1,
            sign,
            to_offset=jr.lane_offset_suc[str(jr.successor.element_id)],
        )
        junc.add_connection(conne1)

        # handle predecessor lanes
        conne2 = Connection(
            jr.predecessor.element_id, jr.id, ContactPoint.start
        )
        _, sign, _ = _get_related_lanesection(
            jr, get_road_by_id(roads, jr.predecessor.element_id)
        )
        _create_junction_links(
            conne2,
            len(jr.lanes.lanesections[0].rightlanes),
            -1,
            sign,
            from_offset=jr.lane_offset_pred[str(jr.predecessor.element_id)],
        )
        _create_junction_links(
            conne2,
            len(jr.lanes.lanesections[0].leftlanes),
            1,
            sign,
            from_offset=jr.lane_offset_pred[str(jr.predecessor.element_id)],
        )
        junc.add_connection(conne2)
    return junc


def create_direct_junction(
    roads: List[Road], id: int, name: str = "my direct junction"
) -> Junction:
    """Create the junction structure for a set of roads, for a direct junction.

    Parameters
    ----------
    roads : list of Road
        All roads that are building up the direct junction.
    id : int
        The ID of the junction.
    name : str, optional
        Name of the junction. Default is "my direct junction".

    Returns
    -------
    Junction
        The junction structure ready to use.

    Raises
    ------
    RemovedFunctionality
        If the function is called, as it has been deprecated.
    """
    raise RemovedFunctionality(
        "The create_direct_junction has been removed, due to its very limited functionality, please try the xodr.DirectJunctionCreator instead."
    )


def get_road_by_id(roads: List[Road], id: int) -> Road:
    """Return a road based on the road ID.

    Parameters
    ----------
    roads : list of Road
        A list of roads to search through.
    id : int
        The ID of the road to retrieve.

    Returns
    -------
    Road
        The road with the specified ID.
    """
    for r in roads:
        if r.id == id:
            return r
