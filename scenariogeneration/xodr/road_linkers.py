from scenariogeneration.xodr.opendrive import Road, ElementType, AdjustablePlanview, UndefinedRoadNetwork, PlanView, Spiral, LaneDef, create_lanes_merge_split#Lane
import numpy as np
from typing import Optional
import pyclothoids as pcloth

def wrap_pi(angle):
    return angle % (2 * np.pi)

class _OffsetCalculator:
    def __init__(self, main_road, neighbor_road,negative_offset_lanes, possitive_offset_lanes,lanesection,negative_sign,offset_key):
        #The algorithm works only when then main road is not a junction road, hence a swap is done
        self.main_is_junction = main_road.road_type != -1

        self.main_road = main_road
        self.neighbor_road = neighbor_road
        self.negative_offset_lanes = negative_offset_lanes
        self.possitive_offset_lanes = possitive_offset_lanes
        self._lanesection = lanesection
        self.negative_sign = negative_sign
        self.offset_key = offset_key

    def _calc_offset_width(self,lanes: list["Lane"], subtract:bool):
        offset_sign = 1
        s = 0

        if subtract:
            offset_sign = -1
        if self._lanesection == -1:
            if self.main_is_junction:
                s = self.neighbor_road.planview.get_total_length()
            else:
                s = self.main_road.planview.get_total_length()

        offset_width = 0
        for lane in lanes:
            offset_width = offset_width - offset_sign*(
                        lane.widths[self._lanesection].a
                        + lane.widths[self._lanesection].b
                        * s
                        + lane.widths[self._lanesection].c
                        * s**2
                        + lane.widths[self._lanesection].d
                        * s**3
                    )
        return offset_width

    def calc_lane_offset_for_main(self):
        return -self.calc_lane_offset_for_neighbor()

    def _converted_offset_key(self):
        # if self.negative_sign:
            return self.offset_key
        # if self.offset_key == "lane_offset_pred":
        #     return "lane_offset_suc"
        # return "lane_offset_pred"

    def calc_lane_offset_for_neighbor(self):
        if self.main_is_junction:
            offset = getattr(self.main_road,self._converted_offset_key())[str(self.neighbor_road.id)]
            if offset < 0:
                lanes = getattr(self.neighbor_road.lanes.lanesections[self._lanesection],self.negative_offset_lanes)
                sgn = self.negative_sign
            else:
                lanes = getattr(self.neighbor_road.lanes.lanesections[self._lanesection],self.possitive_offset_lanes)
                sgn = not self.negative_sign
        else:
            offset = getattr(self.neighbor_road,self.offset_key)[str(self.main_road.id)]
            if offset < 0:
                lanes = getattr(self.main_road.lanes.lanesections[self._lanesection],self.negative_offset_lanes)
                sgn = not self.negative_sign
            else:
                lanes = getattr(self.main_road.lanes.lanesections[self._lanesection],self.possitive_offset_lanes)
                sgn = self.negative_sign
        return self._calc_offset_width(lanes[0:abs(offset)],sgn)

class CalcOffsetSucSuc(_OffsetCalculator):
    def __init__(self,main_road, neighbor_road):
        #  super().__init__(main_road, neighbor_road,"leftlanes","rightlanes",-1,True,"lane_offset_suc")
        super().__init__(main_road, neighbor_road,"leftlanes","rightlanes",-1,False,"lane_offset_suc")
class CalcOffsetSucPre(_OffsetCalculator):
    def __init__(self,main_road, neighbor_road):
        #  super().__init__(main_road, neighbor_road,"rightlanes","leftlanes",-1,False,"lane_offset_pred")
        super().__init__(main_road, neighbor_road,"rightlanes","leftlanes",-1,True,"lane_offset_pred")
class CalcOffsetPrePre(_OffsetCalculator):
    def __init__(self,main_road, neighbor_road):
        #  super().__init__(main_road, neighbor_road,"leftlanes","rightlanes",0,True,"lane_offset_pred")
        super().__init__(main_road, neighbor_road,"leftlanes","rightlanes",0,False,"lane_offset_pred")
class CalcOffsetPreSuc(_OffsetCalculator):
    def __init__(self,main_road, neighbor_road):
        #  super().__init__(main_road, neighbor_road,"rightlanes","leftlanes",0,False,"lane_offset_suc")
         super().__init__(main_road, neighbor_road,"rightlanes","leftlanes",0,True,"lane_offset_suc")



class _OneConnectionAdjuster:
    """Base class for adjusting based on a predecessor"""
    def __init__(self, main_road:Road,neighbor:Road):
        self.main_road = main_road
        self.neighbor = neighbor
        self.neighbor_point = None
        self.main_point = None
        self.main_from_end = None
        self.neighbor_from_end = None
        self.main_dir_change = None
        self.neighbor_dir_change = None
        self._offset_calc = None

    # def adjust_main_from_neighbor(self):
    #     x, y, h = getattr(self.neighbor.planview,self.neighbor_point)()

    #     offset_width = abs(self._offset_calc.calc_lane_offset_for_main())
    #     h = wrap_pi(h -self.main_dir_change)
    #     x = offset_width * np.sin(h) + x
    #     y = -offset_width * np.cos(h) + y

    #     self.main_road.planview.set_start_point(x, y, h)
    #     self.main_road.planview.adjust_geometries(self.main_from_end)

    # def adjust_neighbor(self):
    #     x, y, h = getattr(self.main_road.planview,self.main_point)()

    #     offset_width = abs(self._offset_calc.calc_lane_offset_for_neighbor())
    #     h = wrap_pi(h-self.neighbor_dir_change)
    #     x = offset_width * np.sin(h) + x
    #     y = -offset_width * np.cos(h) + y

    #     self.neighbor.planview.set_start_point(x, y, h)
    #     self.neighbor.planview.adjust_geometries(self.neighbor_from_end)

class _AdjustableData:
    """Base class to keep data for an AdjustablePlanview to be able to create them,
    Only handles one connection

    Parameters
    ----------
    main_road:Road
        the AdjustablePlanview
    neighbor_road:Road
        another road connected to it
    """
    def __init__(self, main_road:Road, neighbor_road:Road):
        self.main_road = main_road
        self.neighbor_road = neighbor_road
        self._x = None
        self._y = None
        self._h = None
        self._left_lanes = None
        self._right_lanes = None
        self._center_roadmark = None
    def _setup(self):
        ...
    @property
    def x(self) -> float:

        if self._x is None:
            self._setup()
        return self._x
    @property
    def y(self) -> float:
        if self._y is None:
            self._setup()
        return self._y
    @property
    def h(self) -> float:
        if self._h is None:
            self._setup()
        return self._h
    @property
    def left_lanes(self) -> list[float]:
        if self._left_lanes is None:
            self._setup()
        return self._left_lanes
    @property
    def right_lanes(self) -> list[float]:
        if self._right_lanes is None:
            self._setup()
        return self._right_lanes
    @property
    def center_roadmark(self):
        if self._center_roadmark is None:
            self._setup()
        return self._center_roadmark
    @staticmethod
    def _recalculate_xy(
            lane_offset: int,
            road: Road,
            lanesection: int,
            x: float,
            y: float,
            h: float,
            common_direct_signs: int = 1,
        ) -> tuple[float, float]:
            """Recalculate x and y if an offset (in junctions) is present.

            Parameters
            ----------
            lane_offset : int
                Lane offset of the road.
            road : Road
                The connected road.
            lanesection : int
                The lane section index.
            x : float
                The reference line x-coordinate of the connected road.
            y : float
                The reference line y-coordinate of the connected road.
            h : float
                The heading of the connected road.
            common_direct_signs : int, optional
                Direction sign multiplier. Default is 1.

            Returns
            -------
            tuple[float, float]
                The recalculated x and y coordinates.
            """
            dist = 0
            start_offset = 0
            if lanesection == -1:
                dist = road.planview.get_total_length()
            if np.sign(lane_offset) == -1:
                angle_addition = -common_direct_signs * np.pi / 2
                for lane_iter in range((np.sign(lane_offset) * lane_offset)):
                    start_offset += (
                        road.lanes.lanesections[lanesection]
                        .rightlanes[lane_iter]
                        .get_width(dist)
                    )
            else:
                angle_addition = common_direct_signs * np.pi / 2
                for lane_iter in range((np.sign(lane_offset) * lane_offset)):
                    start_offset += (
                        road.lanes.lanesections[lanesection]
                        .leftlanes[lane_iter]
                        .get_width(dist)
                    )
            new_x = x + start_offset * np.cos(h + angle_addition)
            new_y = y + start_offset * np.sin(h + angle_addition)
            return new_x, new_y

    def _get_s_start(self, lane_section) -> float:

        s_start = 0
        if lane_section == -1:
            s_start = self.neighbor_road.planview.get_total_length()
        return s_start
    def _get_s_end(self, lane_section) -> float:
        s_end = 0
        if lane_section == -1:
            s_end = self.neighbor_road.planview.get_total_length()
        return s_end

    def _set_center_roadmark(self, lane_section):
        self._center_roadmark = (
                    self.neighbor_road
                    .lanes.lanesections[lane_section]
                    .centerlane.roadmark[0]
                )



class RoadAdjuster:

    def __init__(
        self,
        main_road: Road,
        predecessor: Optional[Road] = None,
        successor: Optional[Road] = None,
    ):
        self.main_road = main_road
        self.predecessor = predecessor
        self.successor = successor

    def adjust_roads(self):
        ...

class AdjustableRoadAdjuster(RoadAdjuster):
    """Can adjust a road with an Adjustable Planview"""
    def __init__(
        self,
        main_road: Road,
        predecessor: Road,
        successor: Road,
        predecessor_data : _AdjustableData,
        successor_data : _AdjustableData,
    ):
        super().__init__(main_road,predecessor,successor)
        self.successor_data = successor_data(main_road,predecessor)
        self.predecessor_data = predecessor_data(main_road,successor)
    def adjust_roads(self) -> int:
        if not (self.predecessor.is_adjusted('planview') and self.successor.is_adjusted('planview')):
            return 0
        clothoids = pcloth.SolveG2(
            self.predecessor_data.x,
            self.predecessor_data.y,
            self.predecessor_data.h,
            1 / 1000000000,
            self.successor_data.x,
            self.successor_data.y,
            self.successor_data.h,
            1 / 1000000000,
        )
        pv = PlanView(self.predecessor_data.x, self.predecessor_data.y, self.predecessor_data.h)

        [
            pv.add_geometry(Spiral(x.KappaStart, x.KappaEnd, length=x.length))
            for x in clothoids
        ]
        pv.adjust_geometries()

        if self.main_road.planview.right_lane_defs is None and self.main_road.planview.left_lane_defs is None:
            if self.main_road.planview.center_road_mark is None:
                center_road_mark = self.predecessor_data.center_roadmark()
            else:
                center_road_mark = self.main_road.planview.center_road_mark
            lanes = create_lanes_merge_split(
                [
                    LaneDef(
                        0,
                        pv.get_total_length(),
                        len(self.predecessor_data.right_lanes),
                        len(self.successor_data.right_lanes),
                        None,
                        self.predecessor_data.right_lanes,
                        self.successor_data.right_lanes,
                    )
                ],
                [
                    LaneDef(
                        0,
                        pv.get_total_length(),
                        len(self.predecessor_data.left_lanes),
                        len(self.successor_data.left_lanes),
                        None,
                        self.predecessor_data.left_lanes,
                        self.successor_data.left_lanes,
                    )
                ],
                pv.get_total_length(),
                center_road_mark,
                None,
                lane_width_end=None,
            )
        else:
            lanes = create_lanes_merge_split(
                self.main_road.planview.right_lane_defs,
                self.main_road.planview.left_lane_defs,
                pv.get_total_length(),
                self.main_road.planview.center_road_mark,
                self.main_road.planview.lane_width,
                lane_width_end=self.main_road.planview.lane_width_end,
            )
        self.main_road.planview = pv
        self.main_road.lanes = lanes
        return 1

class SimpleRoadAdjuster(RoadAdjuster):
    """class for different classes that can adjust an attribute based on its neighbors
    Can adjust roads and connecting roads based on a _PreAdjuster and a _SucAdjuster

    Parameters
    ----------
    domain:str
        what domain to adjust (planview, elevation and so on)
    main_road:Road
        the main road for this adjuster
    predecessor:Optional[Road]
        the predecessor road
    successor:Optional[Road]
        the successor road
    """

    def __init__(
        self,
        domain: str,
        main_road: Road,
        predecessor: Optional[Road] = None,
        successor: Optional[Road] = None,
        predecessor_adjuster : Optional[_OneConnectionAdjuster] = None,
        successor_adjuster : Optional[_OneConnectionAdjuster] = None,
    ):
        super().__init__(main_road,predecessor,successor)
        self.domain = domain
        self.successor_adjuster = None
        self.predecessor_adjuster = None
        if predecessor_adjuster:
            self.predecessor_adjuster = predecessor_adjuster(self.main_road,self.predecessor)
        if successor_adjuster:
            self.successor_adjuster = successor_adjuster(self.main_road,self.successor)

    def adjust_roads(self) -> int:
        """adjust a road and it's neighbors if possible

        Returns
        -------
        int
            the number of roads that were adjusted
        """
        ret_num = 0
        ret_num += self._adjust_with_predecessor()
        ret_num += self._adjust_with_successor()
        return ret_num

    def _adjust_with_predecessor(self):
        ret_num = 0
        if not self.main_road.is_adjusted(self.domain):
            if self.predecessor is not None and self.predecessor.is_adjusted(
                self.domain
            ):
                self.predecessor_adjuster.adjust_main_from_neighbor()
                ret_num += 1
            elif self.successor is not None and self.successor.is_adjusted(
                self.domain
            ):
                self.successor_adjuster.adjust_main_from_neighbor()
                ret_num += 1
        return ret_num

    def _adjust_with_successor(self):
        ret_num = 0
        if self.main_road.is_adjusted(self.domain):
            if (
                self.predecessor is not None
                and not self.predecessor.is_adjusted(self.domain)
            ):
                self.predecessor_adjuster.adjust_neighbor()
                ret_num += 1
            if self.successor is not None and not self.successor.is_adjusted(
                self.domain
            ):
                self.successor_adjuster.adjust_neighbor()
                ret_num += 1
        return ret_num

class RoadSucAsSucAdjuster(_OneConnectionAdjuster):
    def __init__(self,main_road:Road,neighbor:Road):
        super().__init__(main_road,neighbor)
        self.neighbor_point = "get_end_point"
        self.main_point = "get_end_point"
        self.main_from_end = True
        self.neighbor_from_end = True
        self.main_dir_change = 0
        self.neighbor_dir_change = 0
        self._offset_calc = CalcOffsetSucSuc(main_road, neighbor)

    def adjust_main_from_neighbor(self):
        x, y, h = getattr(self.neighbor.planview,self.neighbor_point)()

        offset_width = abs(self._offset_calc.calc_lane_offset_for_main())
        h = wrap_pi(h -self.main_dir_change)
        x = offset_width * np.sin(h) + x
        y = -offset_width * np.cos(h) + y

        self.main_road.planview.set_start_point(x, y, h)
        self.main_road.planview.adjust_geometries(self.main_from_end)

    def adjust_neighbor(self):
        x, y, h = getattr(self.main_road.planview,self.main_point)()

        offset_width = abs(self._offset_calc.calc_lane_offset_for_neighbor())
        h = wrap_pi(h-self.neighbor_dir_change)
        x = offset_width * np.sin(h) + x
        y = -offset_width * np.cos(h) + y

        self.neighbor.planview.set_start_point(x, y, h)
        self.neighbor.planview.adjust_geometries(self.neighbor_from_end)

class RoadSucAsPreAdjuster(_OneConnectionAdjuster):
    def __init__(self,main_road:Road,neighbor:Road):
        super().__init__(main_road,neighbor)
        self.neighbor_point = "get_start_point"
        self.main_point = "get_end_point"
        self.main_from_end = True
        self.neighbor_from_end = False
        self.main_dir_change = np.pi
        self.neighbor_dir_change = 0
        if main_road.road_type == -1:
            self._offset_calc = CalcOffsetSucPre(main_road, neighbor)
        else:
            self._offset_calc = CalcOffsetPreSuc(main_road, neighbor)

    def adjust_main_from_neighbor(self):
        x, y, h = getattr(self.neighbor.planview,self.neighbor_point)()

        offset_width = abs(self._offset_calc.calc_lane_offset_for_main())
        h = wrap_pi(h -self.main_dir_change)
        x = offset_width * np.sin(h) + x
        y = -offset_width * np.cos(h) + y

        self.main_road.planview.set_start_point(x, y, h)
        self.main_road.planview.adjust_geometries(self.main_from_end)

    def adjust_neighbor(self):
        x, y, h = getattr(self.main_road.planview,self.main_point)()

        offset_width = abs(self._offset_calc.calc_lane_offset_for_neighbor())
        h = wrap_pi(h-self.neighbor_dir_change)
        x = offset_width * np.sin(h) + x
        y = -offset_width * np.cos(h) + y

        self.neighbor.planview.set_start_point(x, y, h)
        self.neighbor.planview.adjust_geometries(self.neighbor_from_end)

class RoadPreAsPreAdjuster(_OneConnectionAdjuster):
    def __init__(self,main_road:Road,neighbor:Road):
        super().__init__(main_road,neighbor)
        self.neighbor_point = "get_start_point"
        self.main_point = "get_start_point"
        self.main_from_end = False
        self.neighbor_from_end = False
        self.main_dir_change = np.pi
        self.neighbor_dir_change = np.pi
        self._offset_calc = CalcOffsetPrePre(main_road, neighbor)

    def adjust_main_from_neighbor(self):
        x, y, h = getattr(self.neighbor.planview,self.neighbor_point)()

        offset_width = abs(self._offset_calc.calc_lane_offset_for_main())
        h = wrap_pi(h -self.main_dir_change)
        x = offset_width * np.sin(h) + x
        y = offset_width * np.cos(h) + y

        self.main_road.planview.set_start_point(x, y, h)
        self.main_road.planview.adjust_geometries(self.main_from_end)

    def adjust_neighbor(self):
        x, y, h = getattr(self.main_road.planview,self.main_point)()

        offset_width = abs(self._offset_calc.calc_lane_offset_for_neighbor())
        h = wrap_pi(h-self.neighbor_dir_change)
        x = offset_width * np.sin(h) + x
        y = offset_width * np.cos(h) + y

        self.neighbor.planview.set_start_point(x, y, h)
        self.neighbor.planview.adjust_geometries(self.neighbor_from_end)

class RoadPreAsSucAdjuster(_OneConnectionAdjuster):
    def __init__(self,main_road:Road,neighbor:Road):
        super().__init__(main_road,neighbor)
        self.neighbor_point = "get_end_point"
        self.main_point = "get_start_point"
        self.main_from_end = False
        self.neighbor_from_end = True
        self.main_dir_change = 0
        self.neighbor_dir_change = np.pi
        # self._offset_calc = CalcOffsetPreSuc(main_road, neighbor)
        if main_road.road_type == -1:
            self._offset_calc = CalcOffsetPreSuc(main_road, neighbor)
        else:
            self._offset_calc = CalcOffsetSucPre(main_road, neighbor)

    def adjust_main_from_neighbor(self):
        x, y, h = getattr(self.neighbor.planview,self.neighbor_point)()

        offset_width = abs(self._offset_calc.calc_lane_offset_for_main())
        h = wrap_pi(h -self.main_dir_change)
        x = offset_width * np.sin(h) + x
        y = offset_width * np.cos(h) + y

        self.main_road.planview.set_start_point(x, y, h)
        self.main_road.planview.adjust_geometries(self.main_from_end)

    def adjust_neighbor(self):
        x, y, h = getattr(self.main_road.planview,self.main_point)()

        offset_width = abs(self._offset_calc.calc_lane_offset_for_neighbor())
        h = wrap_pi(h-self.neighbor_dir_change)
        x = offset_width * np.sin(h) + x
        y = offset_width * np.cos(h) + y

        self.neighbor.planview.set_start_point(x, y, h)
        self.neighbor.planview.adjust_geometries(self.neighbor_from_end)

class AdjustablePreAsSucData(_AdjustableData):
    def _setup(self):
        self._x, self._y, self._h = self.neighbor_road.planview.get_end_point()
        start_lane_section = -1
        # add recalculate here
        self._left_lanes = [
                    ll.get_width(self._get_s_start(start_lane_section))
                    for ll in self.neighbor_road
                    .lanes.lanesections[start_lane_section]
                    .leftlanes
                ]
        self._right_lanes = [
            rl.get_width(self._get_s_start(start_lane_section))
            for rl in self.neighbor_road
            .lanes.lanesections[start_lane_section]
            .rightlanes
        ]
        self._set_center_roadmark(start_lane_section)

class AdjustablePreAsPreData(_AdjustableData):
    def _setup(self):
        self._x, self._y, self._h = self.neighbor_road.planview.get_start_point()
        start_lane_section = 0
        self._h = self._h - np.pi

        # add recalculate here

        self._right_lanes = [
            ll.get_width(self._get_s_start(start_lane_section))
            for ll in self.neighbor_road
            .lanes.lanesections[start_lane_section]
            .leftlanes
        ]
        self._left_lanes = [
            rl.get_width(self._get_s_start(start_lane_section))
            for rl in self.neighbor_road
            .lanes.lanesections[start_lane_section]
            .rightlanes
        ]
        self._set_center_roadmark(start_lane_section)

class AdjustableSucAsSucData(_AdjustableData):
    def _setup(self):
        self._x, self._y, self._h = self.neighbor_road.planview.get_end_point()
        end_lane_section = -1
        self._h = self._h - np.pi

        # add recalculate here
        self._right_lanes = [
            ll.get_width(self._get_s_end(end_lane_section))
            for ll in self.neighbor_road
            .lanes.lanesections[end_lane_section]
            .leftlanes
        ]
        self._left_lanes = [
            rl.get_width(self._get_s_end(end_lane_section))
            for rl in self.neighbor_road
            .lanes.lanesections[end_lane_section]
            .rightlanes
                ]
        self._set_center_roadmark(end_lane_section)
class AdjustableSucAsPreData(_AdjustableData):
    def _setup(self):
        self._x, self._y, self._h = self.neighbor_road.planview.get_start_point()
        end_lane_section = 0

        # add recalculate here
        self._left_lanes = [
            ll.get_width(self._get_s_end(end_lane_section))
            for ll in self.neighbor_road
            .lanes.lanesections[end_lane_section]
            .leftlanes
        ]
        self._right_lanes = [
            rl.get_width(self._get_s_end(end_lane_section))
            for rl in self.neighbor_road
            .lanes.lanesections[end_lane_section]
            .rightlanes
        ]
        self._set_center_roadmark(end_lane_section)

class BaseAdjusterFactory:
    def __init__(self, main: Road, pre: Optional[Road] = None, suc: Optional[Road] = None):
        self.main = main
        self.pre = pre
        self.suc = suc


    def _create_for_adjustable_planview(self) -> RoadAdjuster:

        if self.pre is None and self.suc is None:
            raise UndefinedRoadNetwork(
                    "An AdjustablePlanview needs both a predecessor and a successor."
                )
        if (
            self.pre.predecessor
            and str(self.pre.predecessor.element_id) == str(self.main.id)):
            pre_adjuster = AdjustablePreAsPreData
        elif (self.pre.successor
            and str(self.pre.successor.element_id) == str(self.main.id)):
            pre_adjuster = AdjustablePreAsSucData

        if (self.suc.predecessor
            and str(self.suc.predecessor.element_id) == str(self.main.id)
        ):
            suc_adjuster = AdjustableSucAsPreData
        elif (self.suc.successor and str(self.suc.successor.element_id) == str(self.main.id)):
            suc_adjuster = AdjustableSucAsSucData
        return AdjustableRoadAdjuster(self.main,self.pre,self.suc,pre_adjuster,suc_adjuster)

    def _create_for_connecting_road(self) -> RoadAdjuster:
        if (
            self.pre and self.pre.predecessor
            and str(self.pre.predecessor.element_id) == str(self.main.road_type)):
            pre_adjuster = RoadPreAsPreAdjuster
        elif (self.pre and self.pre.successor
            and str(self.pre.successor.element_id) == str(self.main.road_type)):
            pre_adjuster = RoadPreAsSucAdjuster

        if (self.suc and self.suc.predecessor
            and str(self.suc.predecessor.element_id) == str(self.main.road_type)
        ):
            suc_adjuster = RoadSucAsPreAdjuster
        elif (self.suc and self.suc.successor and str(self.suc.successor.element_id) == str(self.main.road_type)):
            suc_adjuster = RoadSucAsSucAdjuster
        if not (suc_adjuster is not None and pre_adjuster is not None):
            raise UndefinedRoadNetwork(f"Cannot determine both predecessor and successor for connecting road {self.main.id}")
        return SimpleRoadAdjuster('planview',self.main, self.pre, self.suc,pre_adjuster,suc_adjuster)

    def create_road_adjuster(self) -> RoadAdjuster:
        pre_adjuster = None
        suc_adjuster = None
        if isinstance(self.main.planview, AdjustablePlanview):
            return self._create_for_adjustable_planview()
        if self.main.road_type != -1:
            return self._create_for_connecting_road()
        if (
            self.pre and self.pre.predecessor
            and str(self.pre.predecessor.element_id) == str(self.main.id)):
            pre_adjuster = RoadPreAsPreAdjuster
        elif (self.pre and self.pre.successor
            and str(self.pre.successor.element_id) == str(self.main.id)):
            pre_adjuster = RoadPreAsSucAdjuster

        if (self.suc and self.suc.predecessor
            and str(self.suc.predecessor.element_id) == str(self.main.id)
        ):
            suc_adjuster = RoadSucAsPreAdjuster
        elif (self.suc and self.suc.successor and str(self.suc.successor.element_id) == str(self.main.id)):
            suc_adjuster = RoadSucAsSucAdjuster

        return SimpleRoadAdjuster('planview',self.main, self.pre, self.suc,pre_adjuster,suc_adjuster)


class RoadBuilder:
    def __init__(self,roads: dict[str,Road]):
        self.roads = roads

    def create_road_adjusters(self) -> list[BaseAdjusterFactory]:
        road_adjusters = []
        for r_id, road in self.roads.items():
            pre = None
            suc = None
            if road.successor and road.successor.element_type == ElementType.road:
                suc = self.roads[str(road.successor.element_id)]
            if road.predecessor and road.predecessor.element_type == ElementType.road:
                pre = self.roads[str(road.predecessor.element_id)]
            if pre or suc:
                road_adjusters.append(BaseAdjusterFactory(road,pre,suc))

        return road_adjusters



