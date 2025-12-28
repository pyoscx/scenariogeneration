import scenariogeneration.xodr as xodr

from scenariogeneration.xodr.road_linkers import (
    BaseAdjusterFactory,
    RoadBuilder,
    CalcOffsetSucSuc,
    CalcOffsetPrePre,
    CalcOffsetSucPre,
    CalcOffsetPreSuc,
    AdjustablePreAsPreData,
    AdjustableSucAsPreData,
    AdjustablePreAsSucData,
    AdjustableSucAsSucData,
)

import pytest
import numpy as np


class TestPrePre:
    """<-pre-|-main->|-suc->"""

    @pytest.fixture
    def roads(self):
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.Line(10), 1)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.start)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
        suc.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
        return pre, main, suc

    @pytest.fixture
    def junction_roads(self):
        pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
        main = xodr.create_road(
            xodr.Line(10), 1, road_type=100, right_lanes=0, left_lanes=1
        )
        suc = xodr.create_road(xodr.Line(10), 2, left_lanes=2, right_lanes=2)
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
        return pre, main, suc

    def test_no_set_geom(self, roads):
        pre, main, suc = roads
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 0
        assert not main.is_adjusted("planview")
        assert not pre.is_adjusted("planview")
        assert not suc.is_adjusted("planview")

    def test_pre_set(self, roads):
        pre, main, suc = roads
        pre.planview.set_start_point(0, 0, -np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (0, 0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, 0, 0)
        )

    def test_suc_set(self, roads):
        pre, main, suc = roads
        suc.planview.set_start_point(20, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2
        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, 0, np.pi)
        )

    def test_main_set(self, roads):
        pre, main, suc = roads
        main.planview.set_start_point(10, 0, 0)
        main.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (30, 0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (20, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, 0, np.pi)
        )

    def test_only_pre(self, roads):
        pre, main, _ = roads
        pre.planview.set_start_point(0, 0, -np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (0, 0, 0)
        )

    def test_junction_offset_pre_set(self, junction_roads):
        pre, main, suc = junction_roads
        pre.planview.set_start_point(10, 0, np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 3, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 3, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (20, 0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (30, 0, 0)
        )

    def test_junction_offset_suc_set(self, junction_roads):
        pre, main, suc = junction_roads
        suc.planview.set_start_point(20, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 3, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 3, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, 0, np.pi)
        )


class TestPreSuc:
    """<-pre-|-main->|<-suc-"""

    @pytest.fixture
    def roads(self):
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.Line(10), 1)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.start)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
        suc.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
        return pre, main, suc
    @pytest.fixture
    def junction_roads(self):
        pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
        main = xodr.create_road(
            xodr.Line(10), 1, road_type=100, right_lanes=0, left_lanes=1
        )
        suc = xodr.create_road(xodr.Line(10), 2, left_lanes=2, right_lanes=2)
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
        return pre, main, suc

    def test_no_set_geom(self, roads):
        pre, main, suc = roads
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 0
        assert not main.is_adjusted("planview")
        assert not pre.is_adjusted("planview")
        assert not suc.is_adjusted("planview")

    def test_pre_set(self, roads):
        pre, main, suc = roads
        pre.planview.set_start_point(0, 0, -np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (0, 0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (20, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (10, 0, np.pi)
        )

    def test_suc_set(self, roads):
        pre, main, suc = roads
        suc.planview.set_start_point(30, 0, -np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2
        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, 0, np.pi)
        )

    def test_main_set(self, roads):
        pre, main, suc = roads
        main.planview.set_start_point(10, 0, 0)
        main.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (30, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, 0, np.pi)
        )

    def test_junction_offset_pre_set(self, junction_roads):
        pre, main, suc = junction_roads
        pre.planview.set_start_point(10, 0, np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 3, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 3, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (30, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, 0, np.pi)
        )

    def test_junction_offset_suc_set(self, junction_roads):
        pre, main, suc = junction_roads
        suc.planview.set_start_point(30, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 3, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 3, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, 0, np.pi)
        )


class TestSucPre:
    """-pre->|-main->|-suc->"""

    @pytest.fixture
    def roads(self):
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.Line(10), 1)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.end)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
        suc.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
        return pre, main, suc

    @pytest.fixture
    def junction_roads(self):
        pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
        main = xodr.create_road(
            xodr.Line(10), 1, road_type=100, right_lanes=0, left_lanes=1
        )
        suc = xodr.create_road(xodr.Line(10), 2, left_lanes=2, right_lanes=2)
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
        return pre, main, suc
    def test_no_set_geom(self, roads):
        pre, main, suc = roads
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 0
        assert not main.is_adjusted("planview")
        assert not pre.is_adjusted("planview")
        assert not suc.is_adjusted("planview")

    def test_pre_set(self, roads):
        pre, main, suc = roads
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (20, 0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (30, 0, 0)
        )

    def test_suc_set(self, roads):
        pre, main, suc = roads
        suc.planview.set_start_point(20, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2
        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, 0, 0)
        )

    def test_main_set(self, roads):
        pre, main, suc = roads
        main.planview.set_start_point(10, 0, 0)
        main.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (30, 0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (20, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, 0, 0)
        )

    def test_junction_offset_pre_set(self, junction_roads):
        pre, main, suc = junction_roads
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 3, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 3, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (20, 0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (30, 0, 0)
        )

    def test_junction_offset_suc_set(self, junction_roads):
        pre, main, suc = junction_roads
        suc.planview.set_start_point(20, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 3, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 3, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, 0, 0)
        )


class TestSucSuc:
    """-pre->|-main->|<-suc-"""

    @pytest.fixture
    def roads(self):
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.Line(10), 1)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.end)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
        suc.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
        return pre, main, suc

    @pytest.fixture
    def junction_roads(self):
        pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
        main = xodr.create_road(
            xodr.Line(10), 1, road_type=100, right_lanes=0, left_lanes=1
        )
        suc = xodr.create_road(xodr.Line(10), 2, left_lanes=2, right_lanes=2)
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
        return pre, main, suc

    def test_no_set_geom(self, roads):
        pre, main, suc = roads
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 0
        assert not main.is_adjusted("planview")
        assert not pre.is_adjusted("planview")
        assert not suc.is_adjusted("planview")

    def test_pre_set(self, roads):
        pre, main, suc = roads
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (30, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, 0, np.pi)
        )

    def test_suc_set(self, roads):
        pre, main, suc = roads
        suc.planview.set_start_point(20, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2
        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (0, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (-10, 0, 0)
        )
        np.testing.assert_almost_equal(pre.planview.get_end_point(), (0, 0, 0))

    def test_main_set(self, roads):
        pre, main, suc = roads
        main.planview.set_start_point(10, 0, 0)
        main.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (30, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, 0, 0)
        )

    def test_junction_offset_pre_set(self, junction_roads):
        pre, main, suc = junction_roads
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 3, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 3, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (30, 0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, 0, np.pi)
        )

    def test_junction_offset_suc_set(self, junction_roads):
        pre, main, suc = junction_roads
        suc.planview.set_start_point(30, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 2

        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (20, 3, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 3, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, 0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, 0, 0)
        )


class TestAdjustablePlanView:


    @pytest.fixture
    def roads_suc_pre(self):
        """-pre->|-adjustable->|-suc->"""
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.AdjustablePlanview(), 1)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.end)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
        suc.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
        return pre, main, suc

    @pytest.fixture
    def roads_pre_pre(self):
        """<-pre-|-adjustable->|-suc->"""
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.AdjustablePlanview(), 1)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.start)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
        suc.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
        return pre, main, suc


    @pytest.fixture
    def roads_pre_suc(self):
        """<-pre-|-adjustable->|<-suc-"""
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.AdjustablePlanview(), 1)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.start)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
        suc.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
        return pre, main, suc

    @pytest.fixture
    def roads_suc_suc(self):
        """-pre->|-adjustable->|<-suc-"""
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.AdjustablePlanview(), 1)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.end)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
        suc.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
        return pre, main, suc



    @pytest.mark.parametrize("roads", [
        'roads_suc_suc',
        'roads_pre_suc',
        'roads_suc_pre',
        'roads_pre_pre',
    ])
    def test_adjustable_planview_not_both_set(self, request, roads):
        pre, main, suc = request.getfixturevalue(roads)
        suc.planview.set_start_point(10, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 0

    @pytest.mark.parametrize("roads,expected_pre_type,expected_suc_type", [
        ('roads_suc_suc',AdjustablePreAsSucData,AdjustableSucAsSucData),
        ('roads_pre_suc',AdjustablePreAsPreData,AdjustableSucAsSucData),
        ('roads_suc_pre',AdjustablePreAsSucData,AdjustableSucAsPreData),
        ('roads_pre_pre',AdjustablePreAsPreData,AdjustableSucAsPreData),
    ])
    def test_adjustable_planview_both_set(self, request, roads,expected_pre_type,expected_suc_type):
        pre, main, suc = request.getfixturevalue(roads)
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        suc.planview.set_start_point(40, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1
        assert not isinstance(main.planview, xodr.AdjustablePlanview)
        assert isinstance(adjuster.predecessor_data,expected_pre_type)
        assert isinstance(adjuster.successor_data,expected_suc_type)


class TestBuilder:
    def test_create_road_adjuster_normal_roads(self):
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.Line(10), 1)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.start)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
        suc.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

        builder = RoadBuilder({"0": pre, "1": main, "2": suc})
        roadfactories = builder.create_road_adjusters()
        assert roadfactories[0].main.id == pre.id
        assert roadfactories[0].pre.id == main.id

        assert roadfactories[1].pre.id == pre.id
        assert roadfactories[1].main.id == main.id
        assert roadfactories[1].suc.id == suc.id

        assert roadfactories[2].main.id == suc.id
        assert roadfactories[2].pre.id == main.id

    def test_create_road_adjuster_junction(self):
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.Line(10), 1, road_type=100)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_predecessor(xodr.ElementType.junction, 100)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.start)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
        suc.add_predecessor(xodr.ElementType.junction, 100)

        builder = RoadBuilder({"0": pre, "1": main, "2": suc})
        roadfactories = builder.create_road_adjusters()
        assert roadfactories[0].pre.id == pre.id
        assert roadfactories[0].main.id == main.id
        assert roadfactories[0].suc.id == suc.id

    def test_create_road_adjuster_adjustable_planview(self):
        pre = xodr.create_road(xodr.Line(10), 0)
        main = xodr.create_road(xodr.AdjustablePlanview(), 1)
        suc = xodr.create_road(xodr.Line(10), 2)
        pre.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
        main.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.start)
        main.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
        suc.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

        builder = RoadBuilder({"0": pre, "1": main, "2": suc})
        roadfactories = builder.create_road_adjusters()
        assert roadfactories[0].main.id == pre.id
        assert roadfactories[0].pre.id == main.id

        assert roadfactories[1].pre.id == pre.id
        assert roadfactories[1].main.id == main.id
        assert roadfactories[1].suc.id == suc.id

        assert roadfactories[2].main.id == suc.id
        assert roadfactories[2].pre.id == main.id


class TestOffsetCalcs:
    @pytest.fixture
    def junc_as_succ_main_as_succ(self):
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
            xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=-1
        )
        junc_left_lane.add_successor(
            xodr.ElementType.road, 2, xodr.ContactPoint.end, lane_offset=1
        )
        main.add_successor(xodr.ElementType.junction, 100)
        main.lane_offset_suc["0"] = 1
        main.lane_offset_suc["1"] = -1
        return main, junc_left_lane, junc_right_lane

    def test_suc_suc_left(self, junc_as_succ_main_as_succ):
        main, junc_left_lane, _ = junc_as_succ_main_as_succ
        offset_calculator = CalcOffsetSucSuc(main, junc_left_lane)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), -4.0
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), 4.0
        )

    def test_suc_suc_right(self, junc_as_succ_main_as_succ):
        main, _, junc_right_lane = junc_as_succ_main_as_succ
        offset_calculator = CalcOffsetSucSuc(main, junc_right_lane)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), 2.0
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), -2.0
        )


    def test_suc_suc_left_junc_main(self, junc_as_succ_main_as_succ):
        main, junc_left_lane, _ = junc_as_succ_main_as_succ
        offset_calculator = CalcOffsetSucSuc(junc_left_lane,main)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), 4.0
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), -4.0
        )

    def test_suc_suc_right_junc_main(self, junc_as_succ_main_as_succ):
        main, _, junc_right_lane = junc_as_succ_main_as_succ
        offset_calculator = CalcOffsetSucSuc(junc_right_lane,main)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), -2.0
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), 2.0
        )


    @pytest.fixture
    def junc_as_pre_main_as_succ(self):
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
        return main, junc_left_lane, junc_right_lane

    def test_suc_pre_left(self, junc_as_pre_main_as_succ):
        main, junc_left_lane, _ = junc_as_pre_main_as_succ
        offset_calculator = CalcOffsetSucPre(main, junc_left_lane)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), 2.0
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), -2.0
        )

    def test_suc_pre_right(self, junc_as_pre_main_as_succ):
        main, _, junc_right_lane = junc_as_pre_main_as_succ
        offset_calculator = CalcOffsetSucPre(main, junc_right_lane)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), -4.0
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), 4.0
        )

    def test_suc_pre_left_junc_main(self, junc_as_pre_main_as_succ):
        main, junc_left_lane, _ = junc_as_pre_main_as_succ
        offset_calculator = CalcOffsetSucPre(junc_left_lane,main)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), -2.0
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), 2.0
        )

    def test_suc_pre_right_junc_main(self, junc_as_pre_main_as_succ):
        main, _, junc_right_lane = junc_as_pre_main_as_succ
        offset_calculator = CalcOffsetSucPre( junc_right_lane,main)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), 4.0
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), -4.0
        )

    @pytest.fixture
    def junc_as_pre_main_as_pre(self):
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
        main.lane_offset_pred["0"] = 1
        main.lane_offset_pred["1"] = -1
        return main, junc_left_lane, junc_right_lane

    def test_pre_pre_left(self, junc_as_pre_main_as_pre):
        main, junc_left_lane, _ = junc_as_pre_main_as_pre
        offset_calculator = CalcOffsetPrePre(main, junc_left_lane)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), -3.5
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), 3.5
        )

    def test_pre_pre_right(self, junc_as_pre_main_as_pre):
        main, _, junc_right_lane = junc_as_pre_main_as_pre
        offset_calculator = CalcOffsetPrePre(main, junc_right_lane)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), 1.5
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), -1.5
        )


    def test_pre_pre_left_junc_main(self, junc_as_pre_main_as_pre):
        main, junc_left_lane, _ = junc_as_pre_main_as_pre
        offset_calculator = CalcOffsetPrePre( junc_left_lane,main)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), 3.5
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), -3.5
        )

    def test_pre_pre_right_junc_main(self, junc_as_pre_main_as_pre):
        main, _, junc_right_lane = junc_as_pre_main_as_pre
        offset_calculator = CalcOffsetPrePre(junc_right_lane,main)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), -1.5
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), 1.5
        )
    @pytest.fixture
    def junc_as_suc_main_as_pre(self):
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
        main.lane_offset_pred["0"] = 1
        main.lane_offset_pred["1"] = -1
        return main, junc_left_lane, junc_right_lane

    def test_pre_suc_left(self, junc_as_suc_main_as_pre):
        main, junc_left_lane, _ = junc_as_suc_main_as_pre
        offset_calculator = CalcOffsetPreSuc(main, junc_left_lane)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), 1.5
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), -1.5
        )

    def test_pre_suc_right(self, junc_as_suc_main_as_pre):
        main, _, junc_right_lane = junc_as_suc_main_as_pre
        offset_calculator = CalcOffsetPreSuc(main, junc_right_lane)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), -3.5
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), 3.5
        )

    def test_pre_suc_left_junc_main(self, junc_as_suc_main_as_pre):
        main, junc_left_lane, _ = junc_as_suc_main_as_pre
        offset_calculator = CalcOffsetPreSuc(junc_left_lane,main)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), -1.5
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), 1.5
        )

    def test_pre_suc_right_junc_main(self, junc_as_suc_main_as_pre):
        main, _, junc_right_lane = junc_as_suc_main_as_pre
        offset_calculator = CalcOffsetPreSuc(junc_right_lane,main)

        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_neighbor(), 3.5
        )
        np.testing.assert_almost_equal(
            offset_calculator.calc_lane_offset_for_main(), -3.5
        )