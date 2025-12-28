from scenariogeneration import xodr, esmini, prettyprint
import numpy as np
from scenariogeneration.xodr.road_linkers import RoadBuilder

odr = xodr.OpenDrive("my road")
## Three roads in a row
if False:
    pre = xodr.create_road(xodr.Line(10), 0)
    main = xodr.create_road(xodr.Line(10), 1)
    suc = xodr.create_road(xodr.Line(10), 2)
    suc.planview.set_start_point(20, 0, 0)
    suc.planview.adjust_geometries()
    pre.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
    suc.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
    main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.start)
    main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)

    odr.add_road(pre)
    odr.add_road(main)
    odr.add_road(suc)
## simple junction
if False:
    pre = xodr.create_road(xodr.Line(10), 0)
    suc = xodr.create_road(xodr.Line(10), 2)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_incoming_road_cartesian_geometry(pre, 0, 0, 0, "successor")
    jc.add_incoming_road_cartesian_geometry(suc, 10, 0, np.pi, "predecessor")
    jc.add_connection(pre.id, suc.id)
    odr.add_road(pre)
    odr.add_road(suc)
    odr.add_junction_creator(jc)
### way junction
if False:
    roads: list[xodr.Road] = []
    numintersections = 4
    nlanes = 2

    # setup junction creator
    junction_creator = xodr.CommonJunctionCreator(100, "my junction")

    # create some roads
    for i in range(numintersections):
        roads.append(
            xodr.create_road(
                [xodr.Line(100)],
                i,
                center_road_mark=xodr.std_roadmark_broken(),
                left_lanes=nlanes,
                right_lanes=nlanes,
            )
        )

        # add road to junciton
        junction_creator.add_incoming_road_circular_geometry(
            roads[i], 40, i * 2 * np.pi / numintersections, "successor"
        )

        # add connection to all previous roads
        for j in range(i):
            junction_creator.add_connection(j, i)

    for r in roads:
        odr.add_road(r)
    odr.add_junction_creator(junction_creator)

    # some tests
    roads[0].planview.set_start_point(0, 0, 0)
    roads[0].planview.adjust_geometries()
    road_builder = RoadBuilder(odr.roads)
    roads_adjusted = 1

    factories = road_builder.create_road_adjusters()
    adjusters = [x.create_road_adjuster() for x in factories]
    while roads_adjusted < len(odr.roads):
        for r in adjusters:
            roads_adjusted += r.adjust_roads()

# simple junction offset test
if False:
    pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
    suc = xodr.create_road(xodr.Line(10), 2, left_lanes=2, right_lanes=2)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_incoming_road_cartesian_geometry(pre, 0, 0, 0, "successor")
    jc.add_incoming_road_cartesian_geometry(suc, 10, 0, np.pi, "successor")
    jc.add_connection(pre.id, suc.id, 2, -2)
    odr.add_road(pre)
    odr.add_road(suc)
    odr.add_junction_creator(jc)


# simple junction offset test
if False:
    junc_right_lane = xodr.create_road(
        xodr.Line(15),
        0,
        road_type=100,
        right_lanes=xodr.LaneDef(0, 15, 1, 1, None, [1.25], [1.75]),
        left_lanes=0,
    )
    junc_left_lane = xodr.create_road(
        xodr.Line(10),
        1,
        road_type=100,
        right_lanes=0,
        left_lanes=xodr.LaneDef(0, 10, 1, 1, None, [2.3], [1.6]),
    )
    main = xodr.create_road(
        xodr.Line(20),
        2,
        left_lanes=xodr.LaneDef(0, 20, 2, 2, None, [1.5, 2.5], [2, 3]),
        right_lanes=xodr.LaneDef(0, 20, 2, 2, None, [3.5, 4.5], [4, 5]),
    )
    junc_right_lane.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=-1
    )
    junc_left_lane.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=1
    )
    main.add_successor(xodr.ElementType.junction, 100)
    main.lane_offset_suc["0"] = 1
    main.lane_offset_suc["1"] = -1
    odr.add_road(main)
    odr.add_road(junc_right_lane)
    odr.add_road(junc_left_lane)

# simple junction offset test
if False:
    junc_right_lane = xodr.create_road(
        xodr.Line(15),
        0,
        road_type=100,
        right_lanes=xodr.LaneDef(0, 15, 1, 1, None, [1.25], [1.75]),
        left_lanes=0,
    )
    junc_left_lane = xodr.create_road(
        xodr.Line(10),
        1,
        road_type=100,
        right_lanes=0,
        left_lanes=xodr.LaneDef(0, 10, 1, 1, None, [2.3], [2.6]),
    )
    main = xodr.create_road(
        xodr.Line(20),
        2,
        left_lanes=xodr.LaneDef(0, 20, 2, 2, None, [1.5, 2.5], [2, 3]),
        right_lanes=xodr.LaneDef(0, 20, 2, 2, None, [3.5, 4.5], [4, 5]),
    )
    junc_right_lane.add_predecessor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=-1
    )
    junc_left_lane.add_predecessor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=1
    )
    main.add_successor(xodr.ElementType.junction, 100)
    main.lane_offset_suc["0"] = 1
    main.lane_offset_suc["1"] = -1
    odr.add_road(main)
    odr.add_road(junc_right_lane)
    odr.add_road(junc_left_lane)

# simple junction offset test
if 0:
    junc_right_lane = xodr.create_road(
        xodr.Line(15),
        0,
        road_type=100,
        right_lanes=xodr.LaneDef(0, 15, 1, 1, None, [1.25], [1.75]),
        left_lanes=0,
    )
    junc_left_lane = xodr.create_road(
        xodr.Line(10),
        1,
        road_type=100,
        right_lanes=0,
        left_lanes=xodr.LaneDef(0, 10, 1, 1, None, [2.3], [2.6]),
    )
    main = xodr.create_road(
        xodr.Line(20),
        2,
        left_lanes=xodr.LaneDef(0, 20, 2, 2, None, [1.5, 2.5], [2, 3]),
        right_lanes=xodr.LaneDef(0, 20, 2, 2, None, [3.5, 4.5], [4, 5]),
    )
    junc_right_lane.add_predecessor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start, lane_offset=-1
    )
    junc_left_lane.add_predecessor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start, lane_offset=1
    )
    main.add_predecessor(xodr.ElementType.junction, 100)
    main.lane_offset_suc["0"] = 1
    main.lane_offset_suc["1"] = -1
    odr.add_road(junc_right_lane)
    odr.add_road(junc_left_lane)
    odr.add_road(main)
# simple junction offset test
if 0:
    junc_right_lane = xodr.create_road(
        xodr.Line(15),
        0,
        road_type=100,
        right_lanes=xodr.LaneDef(0, 15, 1, 1, None, [1.25], [1.75]),
        left_lanes=0,
    )
    junc_left_lane = xodr.create_road(
        xodr.Line(10),
        1,
        road_type=100,
        right_lanes=0,
        left_lanes=xodr.LaneDef(0, 10, 1, 1, None, [2.3], [2.6]),
    )
    main = xodr.create_road(
        xodr.Line(20),
        2,
        left_lanes=xodr.LaneDef(0, 20, 2, 2, None, [1.5, 2.5], [2, 3]),
        right_lanes=xodr.LaneDef(0, 20, 2, 2, None, [3.5, 4.5], [4, 5]),
    )
    junc_right_lane.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start, lane_offset=-1
    )
    junc_left_lane.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start, lane_offset=1
    )
    main.add_predecessor(xodr.ElementType.junction, 100)
    main.lane_offset_suc["0"] = -1
    main.lane_offset_suc["1"] = 1

    odr.add_road(junc_right_lane)
    odr.add_road(junc_left_lane)
    odr.add_road(main)
# full crossing all(?) combinations
if 1:
    numintersections = 4
    nlanes = 3
    conn = ["successor", "predecessor", "successor", "predecessor"]
    # setup junction creator
    junction_creator = xodr.CommonJunctionCreator(100, "my junction")
    roads: list[xodr.Road] = []
    # create some roads
    for i in range(numintersections):
        roads.append(
            xodr.create_road(
                [xodr.Line(100)],
                i,
                center_road_mark=xodr.std_roadmark_broken(),
                left_lanes=nlanes,
                right_lanes=nlanes,
            )
        )

        # add road to junciton
        junction_creator.add_incoming_road_circular_geometry(
            roads[i], 40, i * 2 * np.pi / numintersections, conn[i]
        )

    # junction_creator.add_connection(0,3)

    # junction_creator.add_connection(1,3)

    # junction_creator.add_connection(1,2)
    # junction_creator.add_connection(2,3)

    # junction_creator.add_connection(0,1)
    # junction_creator.add_connection(0,2)

    junction_creator.add_connection(0, 3, [3], [3])
    junction_creator.add_connection(0, 3, [2], [2])
    junction_creator.add_connection(0, 3, [-3], [-3])
    junction_creator.add_connection(0, 3, [-2], [-2])

    junction_creator.add_connection(0, 2, [3], [-3])
    junction_creator.add_connection(2, 0, [2], [-2])
    junction_creator.add_connection(0, 2, [-3], [3])
    junction_creator.add_connection(2, 0, [-2], [2])

    junction_creator.add_connection(0, 1, [3], [3])
    junction_creator.add_connection(0, 1, [2], [2])
    junction_creator.add_connection(0, 1, [-3], [-3])
    junction_creator.add_connection(0, 1, [-2], [-2])

    junction_creator.add_connection(1, 3, [3], [-3])
    junction_creator.add_connection(3, 1, [2], [-2])
    junction_creator.add_connection(1, 3, [-3], [3])
    junction_creator.add_connection(3, 1, [-2], [2])

    # junction_creator.add_connection(1,3,[3],[4])

    # junction_creator.add_connection(0,2,[-1,1],[1,-3])
    # junction_creator.add_connection(0,2,[-1,1],[1,-3])

    # junction_creator.add_connection(1,2,[1,2,-1,-2],[-1,-2,2,3])

    for r in roads:
        odr.add_road(r)
    odr.add_junction_creator(junction_creator)

    roads[0].planview.set_start_point(0, 0, 0)
    roads[0].planview.adjust_geometries()
    road_builder = RoadBuilder(odr.roads)
    roads_adjusted = 1

    factories = road_builder.create_road_adjusters()
    adjusters = [x.create_road_adjuster() for x in factories]
    while roads_adjusted < len(odr.roads):
        for r in adjusters:
            roads_adjusted += r.adjust_roads()


if 0:
    pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
    # main = xodr.create_road(
    #     xodr.Line(20), 1, road_type=100, right_lanes=0, left_lanes=1
    # )
    suc = xodr.create_road(xodr.Line(15), 2, left_lanes=2, right_lanes=2)
    jc = xodr.CommonJunctionCreator(1000,"myjunc")
    jc.add_incoming_road_cartesian_geometry(pre,0,0,0,"successor")
    jc.add_incoming_road_cartesian_geometry(suc,20,0,np.pi,"predecessor")
    jc.add_connection(0,2,-2,-2)
    odr.add_junction_creator(jc)
    odr.add_road(pre)
    odr.add_road(suc)

    roads = [pre,suc] + jc.junction_roads
    roads[0].planview.set_start_point(0, 0, 0)
    roads[0].planview.adjust_geometries()
    road_builder = RoadBuilder(odr.roads)
    roads_adjusted = 1
    factories = road_builder.create_road_adjusters()
    adjusters = [x.create_road_adjuster() for x in factories]
    while roads_adjusted < len(odr.roads):
        for r in adjusters:
            roads_adjusted += r.adjust_roads()
if 0:
    pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
    main = xodr.create_road(
        xodr.Line(20), 1, road_type=100, right_lanes=0, left_lanes=1
    )
    suc = xodr.create_road(xodr.Line(15), 2, left_lanes=2, right_lanes=2)
    pre.add_predecessor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.start, lane_offset=1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start, lane_offset=-1
    )
    suc.add_predecessor(xodr.ElementType.junction, 100)
    pre.lane_offset_pred["1"] = -1
    suc.lane_offset_pred["1"] = 1
    odr.add_road(suc)
    odr.add_road(main)

    odr.add_road(pre)

    suc.planview.set_start_point(0, 0, 0)
    suc.planview.adjust_geometries()
    road_builder = RoadBuilder(odr.roads)
    roads_adjusted = 1
    factories = road_builder.create_road_adjusters()
    adjusters = [x.create_road_adjuster() for x in factories]
    while roads_adjusted < len(odr.roads):
        for r in adjusters:
            roads_adjusted += r.adjust_roads()

odr.adjust_roads_and_lanes()
odr.write_xml("dummy.xodr")

esmini(odr, "../esmini-demo",car_density=4)
