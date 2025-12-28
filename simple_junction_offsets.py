from scenariogeneration import xodr, esmini, prettyprint
import numpy as np
from scenariogeneration.xodr.road_linkers import RoadBuilder

start_x = 0.0
start_y = 0.0
start_h = 0.0

## Three roads in a row
def create_odr(pre,suc,main):
    odr = xodr.OpenDrive("my road")
    odr.add_road(pre)
    odr.add_road(suc)
    odr.add_road(main)

    road_builder = RoadBuilder(odr.roads)
    roads_adjusted = 1
    factories = road_builder.create_road_adjusters()
    adjusters = [x.create_road_adjuster() for x in factories]
    while roads_adjusted < len(odr.roads):
        for r in adjusters:
            roads_adjusted += r.adjust_roads()
    return odr


def get_roads_right_conn():
    pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
    main = xodr.create_road(
        xodr.Line(10), 1, road_type=100, right_lanes=1, left_lanes=0
    )
    suc = xodr.create_road(xodr.Line(20), 2, left_lanes=2, right_lanes=2)
    return pre,main,suc

def prepre_suc_set_right_conn():
    pre,main,suc = get_roads_right_conn()

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
    suc.planview.set_start_point(start_x,start_y,start_h)
    suc.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def prepre_pre_set_right_conn():
    pre,main,suc = get_roads_right_conn()
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

    pre.planview.set_start_point(start_x,start_y,start_h)
    pre.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def presuc_suc_set_right_conn():
    pre,main,suc = get_roads_right_conn()
    pre.add_predecessor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.start, lane_offset=-1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=1
    )
    suc.add_successor(xodr.ElementType.junction, 100)
    pre.lane_offset_pred["1"] = 1
    suc.lane_offset_pred["1"] = -1
    suc.planview.set_start_point(start_x,start_y,start_h)
    suc.planview.adjust_geometries()
    return create_odr(pre,suc,main)


def presuc_pre_set_right_conn():
    pre,main,suc = get_roads_right_conn()
    pre.add_predecessor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.start, lane_offset=-1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=1
    )
    suc.add_successor(xodr.ElementType.junction, 100)
    pre.lane_offset_pred["1"] = 1
    suc.lane_offset_pred["1"] = -1
    pre.planview.set_start_point(start_x,start_y,start_h)
    pre.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def sucpre_suc_set_right_conn():
    pre,main,suc = get_roads_right_conn()
    pre.add_successor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.end, lane_offset=-1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start, lane_offset=1
    )
    suc.add_predecessor(xodr.ElementType.junction, 100)
    pre.lane_offset_pred["1"] = 1
    suc.lane_offset_pred["1"] = -1
    suc.planview.set_start_point(start_x,start_y,start_h)
    suc.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def sucpre_pre_set_right_conn():
    pre,main,suc = get_roads_right_conn()
    pre.add_successor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.end, lane_offset=-1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start, lane_offset=1
    )
    suc.add_predecessor(xodr.ElementType.junction, 100)
    pre.lane_offset_pred["1"] = 1
    suc.lane_offset_pred["1"] = -1
    pre.planview.set_start_point(start_x,start_y,start_h)
    pre.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def sucsuc_suc_set_right_conn():
    pre,main,suc = get_roads_right_conn()
    pre.add_successor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.end, lane_offset=1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=-1
    )
    suc.add_successor(xodr.ElementType.junction, 100)
    pre.lane_offset_suc["1"] = -1
    suc.lane_offset_suc["1"] = 1
    suc.planview.set_start_point(start_x,start_y,start_h)
    suc.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def sucsuc_pre_set_right_conn():
    pre,main,suc = get_roads_right_conn()
    pre.add_successor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.end, lane_offset=1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=-1
    )
    suc.add_successor(xodr.ElementType.junction, 100)
    pre.lane_offset_suc["1"] = -1
    suc.lane_offset_suc["1"] = 1
    pre.planview.set_start_point(start_x,start_y,start_h)
    pre.planview.adjust_geometries()
    return create_odr(pre,suc,main)




def get_roads_left_conn():
    pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
    main = xodr.create_road(
        xodr.Line(10), 1, road_type=100, right_lanes=0, left_lanes=1
    )
    suc = xodr.create_road(xodr.Line(20), 2, left_lanes=2, right_lanes=2)
    return pre,main,suc

def prepre_suc_set_left_conn():
    pre,main,suc = get_roads_left_conn()

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
    suc.planview.set_start_point(start_x,start_y,start_h)
    suc.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def prepre_pre_set_left_conn():
    pre,main,suc = get_roads_left_conn()
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

    pre.planview.set_start_point(start_x,start_y,start_h)
    pre.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def presuc_suc_set_left_conn():
    pre,main,suc = get_roads_left_conn()
    pre.add_predecessor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.start, lane_offset=-1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=1
    )
    suc.add_successor(xodr.ElementType.junction, 100)
    pre.lane_offset_pred["1"] = 1
    suc.lane_offset_pred["1"] = -1
    suc.planview.set_start_point(start_x,start_y,start_h)
    suc.planview.adjust_geometries()
    return create_odr(pre,suc,main)


def presuc_pre_set_left_conn():
    pre,main,suc = get_roads_left_conn()
    pre.add_predecessor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.start, lane_offset=-1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=1
    )
    suc.add_successor(xodr.ElementType.junction, 100)
    pre.lane_offset_pred["1"] = 1
    suc.lane_offset_pred["1"] = -1
    pre.planview.set_start_point(start_x,start_y,start_h)
    pre.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def sucpre_suc_set_left_conn():
    pre,main,suc = get_roads_left_conn()
    pre.add_successor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.end, lane_offset=-1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start, lane_offset=1
    )
    suc.add_predecessor(xodr.ElementType.junction, 100)
    pre.lane_offset_pred["1"] = 1
    suc.lane_offset_pred["1"] = -1
    suc.planview.set_start_point(start_x,start_y,start_h)
    suc.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def sucpre_pre_set_left_conn():
    pre,main,suc = get_roads_left_conn()
    pre.add_successor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.end, lane_offset=-1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start, lane_offset=1
    )
    suc.add_predecessor(xodr.ElementType.junction, 100)
    pre.lane_offset_pred["1"] = 1
    suc.lane_offset_pred["1"] = -1
    pre.planview.set_start_point(start_x,start_y,start_h)
    pre.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def sucsuc_suc_set_left_conn():
    pre,main,suc = get_roads_left_conn()
    pre.add_successor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.end, lane_offset=1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=-1
    )
    suc.add_successor(xodr.ElementType.junction, 100)
    pre.lane_offset_suc["1"] = -1
    suc.lane_offset_suc["1"] = 1
    suc.planview.set_start_point(start_x,start_y,start_h)
    suc.planview.adjust_geometries()
    return create_odr(pre,suc,main)

def sucsuc_pre_set_left_conn():
    pre,main,suc = get_roads_left_conn()
    pre.add_successor(xodr.ElementType.junction, 100)
    main.add_predecessor(
        xodr.ElementType.road, 0, xodr.ContactPoint.end, lane_offset=1
    )
    main.add_successor(
        xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=-1
    )
    suc.add_successor(xodr.ElementType.junction, 100)
    pre.lane_offset_suc["1"] = -1
    suc.lane_offset_suc["1"] = 1
    pre.planview.set_start_point(start_x,start_y,start_h)
    pre.planview.adjust_geometries()
    return create_odr(pre,suc,main)


all_odrs = [
<<<<<<< HEAD
(prepre_pre_set_left_conn,[(0.0, 0.0, 0.0),(0.0, -3.0, 3.141592653589793),(-10.0, 0.00, 3.141592653589793)]),
(sucpre_pre_set_left_conn,[(0.0,0.0,0.0),(10.0,3.0,0.0),(20.0,0.0,0.0)]),
(presuc_pre_set_left_conn,[(0.0, 0.0, 0.0), (0.0, -3.0, 3.141592653589793), (-30.0, 0.0, 0.0)]),
(sucsuc_pre_set_left_conn,[(0.0, 0.0, 0.0),(10.0, 3.0, 0.0),(40.0, 0.0, 3.141592653589793)]),
(prepre_suc_set_left_conn,[(-10.0, 0.0, 3.141592653589793),(-10.0, 3.0, 0.0),(0.0, 0.0, 0.0)]),
(sucpre_suc_set_left_conn,[(-20.0, 0.0, 0.0),(-10.0, 3, 0.0),(0.0, 0.0, 0.0)]),
(presuc_suc_set_left_conn,[(30.0, 0.0, 0.0),(30.0, -3.0, 3.141592653589793),(0.0, 0.0, 0.0)]),
(sucsuc_suc_set_left_conn,[(40.0, 0.0, 3.141592653589793),(30.0, -3.0, 3.141592653589793),(0.0, 0.0, 0.0)])
]
expected_=[








]

=======
# (prepre_pre_set_left_conn,[(0.0, 0.0, 0.0),(0.0, -3.0, 3.141592653589793),(-10.0, 0.00, 3.141592653589793)]),
# (sucpre_pre_set_left_conn,[(0.0,0.0,0.0),(10.0,3.0,0.0),(20.0,0.0,0.0)]),
# (presuc_pre_set_left_conn,[(0.0, 0.0, 0.0), (0.0, -3.0, 3.141592653589793), (-30.0, 0.0, 0.0)]),
# (sucsuc_pre_set_left_conn,[(0.0, 0.0, 0.0),(10.0, 3.0, 0.0),(40.0, 0.0, 3.141592653589793)]),
# (prepre_suc_set_left_conn,[(-10.0, 0.0, 3.141592653589793),(-10.0, 3.0, 0.0),(0.0, 0.0, 0.0)]),
# (sucpre_suc_set_left_conn,[(-20.0, 0.0, 0.0),(-10.0, 3, 0.0),(0.0, 0.0, 0.0)]),
# (presuc_suc_set_left_conn,[(30.0, 0.0, 0.0),(30.0, -3.0, 3.141592653589793),(0.0, 0.0, 0.0)]),
# (sucsuc_suc_set_left_conn,[(40.0, 0.0, 3.141592653589793),(30.0, -3.0, 3.141592653589793),(0.0, 0.0, 0.0)]),
(prepre_pre_set_right_conn,[(0.0, 0.0, 0.0),(0.0, 3.0, 3.141592653589793),(-10.0, 0.00, 3.141592653589793)]),
(sucpre_pre_set_right_conn,[(0.0,0.0,0.0),(10.0,-3.0,0.0),(20.0,0.0,0.0)]),
(presuc_pre_set_right_conn,[(0.0, 0.0, 0.0), (0.0, 3.0, 3.141592653589793), (-30.0, 0.0, 0.0)]),
(sucsuc_pre_set_right_conn,[(0.0, 0.0, 0.0),(10.0, -3.0, 0.0),(40.0, 0.0, 3.141592653589793)]),
(prepre_suc_set_right_conn,[(-10.0, 0.0, 3.141592653589793),(-10.0, -3.0, 0.0),(0.0, 0.0, 0.0)]),
(sucpre_suc_set_right_conn,[(-20.0, 0.0, 0.0),(-10.0, -3, 0.0),(0.0, 0.0, 0.0)]),
(presuc_suc_set_right_conn,[(30.0, 0.0, 0.0),(30.0, 3.0, 3.141592653589793),(0.0, 0.0, 0.0)]),
(sucsuc_suc_set_right_conn,[(40.0, 0.0, 3.141592653589793),(30.0, 3.0, 3.141592653589793),(0.0, 0.0, 0.0)])

]


>>>>>>> 65a87f8 (refactor: change patching algorithm to be more readable)
road_names = ["pre","main","suc"]
for fnc, expected in all_odrs:
    print("")
    print(f"### Case: {fnc.__name__}###")
    odr = fnc()
    # for i in range(3):
    #     odr.roads[str(i)].planview.set_start_point(expected[i][0],expected[i][1],expected[i][2])
    #     odr.roads[str(i)].planview.adjust_geometries()

    # odr = all_odrs[0]
<<<<<<< HEAD
    odr.adjust_roads_and_lanes()

    for i in range(3):
        x,y,z = odr.roads[str(i)].planview.get_start_point()
=======
    # odr.adjust_roads_and_lanes()

    for i in range(3):
        x,y,z = odr.roads[str(i)].planview.get_start_point()
        # print(f"{road_names[i]} , {y}({expected[i][1]})")
>>>>>>> 65a87f8 (refactor: change patching algorithm to be more readable)
        if not all(np.isclose((x,y,z),expected[i],atol=0.00001)):
            print(f"{road_names[i]} is wrong , {y}({expected[i][1]})")
            # {x}({expected[i][0]}) , {z}({expected[i][2]})
    odr.write_xml("dummy.xodr")

<<<<<<< HEAD
    # esmini(odr, "../esmini-demo",car_density=4)
=======
    esmini(odr, "../esmini-demo",car_density=4)
>>>>>>> 65a87f8 (refactor: change patching algorithm to be more readable)
