import scenariogeneration.xodr as xodr

from scenariogeneration.xodr.road_linkers import (
    BaseAdjusterFactory,
    RoadBuilder,
    # CalcOffsetSucSuc,
    # CalcOffsetPrePre,
    # CalcOffsetSucPre,
    # CalcOffsetPreSuc,
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

    def test_adjustable_suc_suc(self, roads_suc_suc):
        pre, main, suc = roads_suc_suc
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        suc.planview.set_start_point(40, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (30, 0, 0)
        )

    def test_adjustable_suc_pre(self, roads_suc_pre):
        pre, main, suc = roads_suc_pre
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        suc.planview.set_start_point(40, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (40, 0, 0)
        )


    def test_adjustable_pre_suc(self, roads_pre_suc):
        pre, main, suc = roads_pre_suc
        pre.planview.set_start_point(10, 0, np.pi)
        pre.planview.adjust_geometries()
        suc.planview.set_start_point(40, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (30, 0, 0)
        )


    def test_adjustable_pre_pre(self, roads_pre_pre):
        pre, main, suc = roads_pre_pre
        pre.planview.set_start_point(10, 0, np.pi)
        pre.planview.adjust_geometries()
        suc.planview.set_start_point(30, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main, pre, suc)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1
        np.testing.assert_almost_equal(
            main.planview.get_start_point(), (10, 0, 0)
        )
        np.testing.assert_almost_equal(
            main.planview.get_end_point(), (30, 0, 0)
        )

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




class TestAdjustersWithOffsets():
    start_x = 0
    start_y = 0
    start_h = 0
    def create_odr(self,pre,suc,main):
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


    def get_roads_right_conn(self):
        pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
        main = xodr.create_road(
            xodr.Line(10), 1, road_type=100, right_lanes=1, left_lanes=0
        )
        suc = xodr.create_road(xodr.Line(20), 2, left_lanes=2, right_lanes=2)
        return pre,main,suc

    def prepre_suc_set_right_conn(self):
        pre,main,suc = self.get_roads_right_conn()

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
        suc.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        suc.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def prepre_pre_set_right_conn(self):
        pre,main,suc = self.get_roads_right_conn()
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

        pre.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        pre.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def presuc_suc_set_right_conn(self):
        pre,main,suc = self.get_roads_right_conn()
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
        suc.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        suc.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)


    def presuc_pre_set_right_conn(self):
        pre,main,suc = self.get_roads_right_conn()
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
        pre.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        pre.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def sucpre_suc_set_right_conn(self):
        pre,main,suc = self.get_roads_right_conn()
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
        suc.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        suc.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def sucpre_pre_set_right_conn(self):
        pre,main,suc = self.get_roads_right_conn()
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
        pre.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        pre.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def sucsuc_suc_set_right_conn(self):
        pre,main,suc = self.get_roads_right_conn()
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
        suc.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        suc.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def sucsuc_pre_set_right_conn(self):
        pre,main,suc = self.get_roads_right_conn()
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
        pre.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        pre.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)




    def get_roads_left_conn(self):
        pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
        main = xodr.create_road(
            xodr.Line(10), 1, road_type=100, right_lanes=0, left_lanes=1
        )
        suc = xodr.create_road(xodr.Line(20), 2, left_lanes=2, right_lanes=2)
        return pre,main,suc

    def prepre_suc_set_left_conn(self):
        pre,main,suc = self.get_roads_left_conn()

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
        suc.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        suc.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def prepre_pre_set_left_conn(self):
        pre,main,suc = self.get_roads_left_conn()
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

        pre.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        pre.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def presuc_suc_set_left_conn(self):
        pre,main,suc = self.get_roads_left_conn()
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
        suc.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        suc.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)


    def presuc_pre_set_left_conn(self):
        pre,main,suc = self.get_roads_left_conn()
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
        pre.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        pre.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def sucpre_suc_set_left_conn(self):
        pre,main,suc = self.get_roads_left_conn()
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
        suc.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        suc.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def sucpre_pre_set_left_conn(self):
        pre,main,suc = self.get_roads_left_conn()
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
        pre.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        pre.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def sucsuc_suc_set_left_conn(self):
        pre,main,suc = self.get_roads_left_conn()
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
        suc.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        suc.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    def sucsuc_pre_set_left_conn(self):
        pre,main,suc = self.get_roads_left_conn()
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
        pre.planview.set_start_point(self.start_x,self.start_y,self.start_h)
        pre.planview.adjust_geometries()
        return self.create_odr(pre,suc,main)

    @pytest.mark.parametrize("network,expected", [
        (prepre_pre_set_left_conn,[(0.0, 0.0, 0.0),(0.0, -3.0, 3.141592653589793),(-10.0, 0.00, 3.141592653589793)]),
        (sucpre_pre_set_left_conn,[(0.0,0.0,0.0),(10.0,3.0,0.0),(20.0,0.0,0.0)]),
        (presuc_pre_set_left_conn,[(0.0, 0.0, 0.0), (0.0, -3.0, 3.141592653589793), (-30.0, 0.0, 0.0)]),
        (sucsuc_pre_set_left_conn,[(0.0, 0.0, 0.0),(10.0, 3.0, 0.0),(40.0, 0.0, 3.141592653589793)]),
        (prepre_suc_set_left_conn,[(-10.0, 0.0, 3.141592653589793),(-10.0, 3.0, 0.0),(0.0, 0.0, 0.0)]),
        (sucpre_suc_set_left_conn,[(-20.0, 0.0, 0.0),(-10.0, 3, 0.0),(0.0, 0.0, 0.0)]),
        (presuc_suc_set_left_conn,[(30.0, 0.0, 0.0),(30.0, -3.0, 3.141592653589793),(0.0, 0.0, 0.0)]),
        (sucsuc_suc_set_left_conn,[(40.0, 0.0, 3.141592653589793),(30.0, -3.0, 3.141592653589793),(0.0, 0.0, 0.0)]),
        (prepre_pre_set_right_conn,[(0.0, 0.0, 0.0),(0.0, 3.0, 3.141592653589793),(-10.0, 0.00, 3.141592653589793)]),
        (sucpre_pre_set_right_conn,[(0.0,0.0,0.0),(10.0,-3.0,0.0),(20.0,0.0,0.0)]),
        (presuc_pre_set_right_conn,[(0.0, 0.0, 0.0), (0.0, 3.0, 3.141592653589793), (-30.0, 0.0, 0.0)]),
        (sucsuc_pre_set_right_conn,[(0.0, 0.0, 0.0),(10.0, -3.0, 0.0),(40.0, 0.0, 3.141592653589793)]),
        (prepre_suc_set_right_conn,[(-10.0, 0.0, 3.141592653589793),(-10.0, -3.0, 0.0),(0.0, 0.0, 0.0)]),
        (sucpre_suc_set_right_conn,[(-20.0, 0.0, 0.0),(-10.0, -3, 0.0),(0.0, 0.0, 0.0)]),
        (presuc_suc_set_right_conn,[(30.0, 0.0, 0.0),(30.0, 3.0, 3.141592653589793),(0.0, 0.0, 0.0)]),
        (sucsuc_suc_set_right_conn,[(40.0, 0.0, 3.141592653589793),(30.0, 3.0, 3.141592653589793),(0.0, 0.0, 0.0)])
    ])
    def test_junction_connections(self, network, expected):
        odr = network(self)
        final_assert = True
        road_names = ["pre","main","suc"]
        for i in range(3):
            x,y,z = odr.roads[str(i)].planview.get_start_point()

            if not all(np.isclose((x,y,z),expected[i],atol=0.00001)):
                final_assert = False
                print(f"{road_names[i]} is wrong , {y}({expected[i][1]})")
        assert final_assert

class TestDirectAdjusters():
    @pytest.fixture
    def setup_with_right_lane(self):
        pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
        suc = xodr.create_road(xodr.Line(10), 2, left_lanes=0, right_lanes=1)
        return pre,suc

    @pytest.fixture
    def setup_with_left_lane(self):
        pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
        suc = xodr.create_road(xodr.Line(10), 2, left_lanes=1, right_lanes=0)
        return pre,suc


    @pytest.fixture
    def setup_with_both_lane(self):
        pre = xodr.create_road(xodr.Line(10), 0, left_lanes=2, right_lanes=2)
        suc = xodr.create_road(xodr.Line(10), 2, left_lanes=1, right_lanes=1)
        return pre,suc




    def test_no_adjuster(self,setup_with_right_lane):
        pre, suc = setup_with_right_lane
        suc2 = xodr.create_road(xodr.Line(10), 3, left_lanes=1, right_lanes=0)
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        suc2.add_predecessor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = 1
        pre.succ_direct_junction[3] = -1
        suc.pred_direct_junction[0] = -1
        suc.pred_direct_junction[0] = 1
        suc.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=pre, suc=suc)
        adjuster = factory.create_road_adjuster()
        adjuster.successor_adjuster == None
        adjuster.predecessor_adjuster == None

## suc pre
    def test_right_lane_suc_pre_suc_set(self, setup_with_right_lane):
        pre, suc = setup_with_right_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = 1
        suc.pred_direct_junction[0] = -1
        suc.planview.set_start_point(10, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, 3.0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, 3.0, 0)
        )

    def test_right_lane_suc_pre_pre_set(self, setup_with_right_lane):
        pre, suc = setup_with_right_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = 1
        suc.pred_direct_junction[0] = -1
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, -3.0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (10, -3.0, 0)
        )

    def test_left_lane_suc_pre_suc_set(self, setup_with_left_lane):
        pre, suc = setup_with_left_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = -1
        suc.pred_direct_junction[0] = 1
        suc.planview.set_start_point(10, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, -3.0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, -3.0, 0)
        )

    def test_left_lane_suc_pre_pre_set(self, setup_with_left_lane):
        pre, suc = setup_with_left_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = -1
        suc.pred_direct_junction[0] = 1
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, 3.0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (10, 3.0, 0)
        )

    def test_both_lanes_suc_pre_suc_set(self, setup_with_both_lane):
        pre, suc = setup_with_both_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = 0
        suc.pred_direct_junction[0] = 0
        suc.planview.set_start_point(10, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, 0.0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, 0.0, 0)
        )

    def test_both_lanes_suc_pre_pre_set(self, setup_with_both_lane):
        pre, suc = setup_with_both_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = 0
        suc.pred_direct_junction[0] = 0
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, 0.0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (10, 0.0, 0)
        )

## pre suc
    def test_right_lane_pre_suc_suc_set(self, setup_with_right_lane):
        pre, suc = setup_with_right_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = 1
        suc.succ_direct_junction[0] = -1
        suc.planview.set_start_point(20, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, 3.0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 3.0, np.pi)
        )

    def test_right_lane_pre_suc_pre_set(self, setup_with_right_lane):
        pre, suc = setup_with_right_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = 1
        suc.succ_direct_junction[0] = -1
        pre.planview.set_start_point(0, 0, np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (0, -3.0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (10, -3.0, np.pi)
        )

    def test_left_lane_pre_suc_suc_set(self, setup_with_left_lane):
        pre, suc = setup_with_left_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = -1
        suc.succ_direct_junction[0] = 1
        suc.planview.set_start_point(20, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, -3.0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, -3.0, np.pi)
        )

    def test_left_lane_pre_suc_pre_set(self, setup_with_left_lane):
        pre, suc = setup_with_left_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = -1
        suc.succ_direct_junction[0] = 1
        pre.planview.set_start_point(0, 0, np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (0, 3.0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (10, 3.0, np.pi)
        )

    def test_both_lanes_pre_suc_suc_set(self, setup_with_right_lane):
        pre, suc = setup_with_right_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = 1
        suc.succ_direct_junction[0] = -1
        suc.planview.set_start_point(20, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, 3.0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 3.0, np.pi)
        )

    def test_both_lanes_pre_suc_suc_set(self, setup_with_both_lane):
        pre, suc = setup_with_both_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = 0
        suc.succ_direct_junction[0] = 0
        suc.planview.set_start_point(20, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, 0.0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 0.0, np.pi)
        )


    def test_both_lanes_pre_suc_pre_set(self, setup_with_both_lane):
        pre, suc = setup_with_both_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = 0
        suc.succ_direct_junction[0] = 0
        pre.planview.set_start_point(0, 0, np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (0, 0.0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (10, 0.0, np.pi)
        )

    ## suc suc
    def test_right_lane_suc_suc_suc_set(self, setup_with_right_lane):
        pre, suc = setup_with_right_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = -1
        suc.succ_direct_junction[0] = 1
        suc.planview.set_start_point(20, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, 3.0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, 3.0, 0)
        )

    def test_right_lane_suc_suc_pre_set(self, setup_with_right_lane):
        pre, suc = setup_with_right_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = -1
        suc.succ_direct_junction[0] = 1
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (10, -3.0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (20, -3.0, np.pi)
        )

    def test_left_lane_suc_suc_suc_set(self, setup_with_left_lane):
        pre, suc = setup_with_left_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = 1
        suc.succ_direct_junction[0] = -1
        suc.planview.set_start_point(20, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, -3.0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, -3.0, 0)
        )

    def test_left_lane_suc_suc_pre_set(self, setup_with_left_lane):
        pre, suc = setup_with_left_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = 1
        suc.succ_direct_junction[0] = -1
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (10, 3.0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (20, 3.0, np.pi)
        )

    def test_both_lanes_suc_suc_suc_set(self, setup_with_both_lane):
        pre, suc = setup_with_both_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = 0
        suc.succ_direct_junction[0] = 0
        suc.planview.set_start_point(20, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (10, 0.0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (0, 0.0, 0)
        )

    def test_both_lanes_suc_suc_pre_set(self, setup_with_both_lane):
        pre, suc = setup_with_both_lane
        pre.add_successor(xodr.ElementType.junction, 200)
        suc.add_successor(xodr.ElementType.junction, 200)
        pre.succ_direct_junction[2] = 0
        suc.succ_direct_junction[0] = 0
        pre.planview.set_start_point(0, 0, 0)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, suc=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (10, 0.0, np.pi)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (20, 0.0, np.pi)
        )

## pre pre
    def test_right_lane_pre_pre_suc_set(self, setup_with_right_lane):
        pre, suc = setup_with_right_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = -1
        suc.pred_direct_junction[0] = 1
        suc.planview.set_start_point(10, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, 3.0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 3.0, np.pi)
        )

    def test_right_lane_pre_pre_pre_set(self, setup_with_right_lane):
        pre, suc = setup_with_right_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = -1
        suc.pred_direct_junction[0] = 1
        pre.planview.set_start_point(10, 0, np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, -3.0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (10, -3.0, 0)
        )

    def test_left_lane_pre_pre_suc_set(self, setup_with_left_lane):
        pre, suc = setup_with_left_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = 1
        suc.pred_direct_junction[0] = -1
        suc.planview.set_start_point(10, 0, 0)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (0, -3.0, np.pi)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, -3.0, np.pi)
        )

    def test_left_lane_pre_pre_pre_set(self, setup_with_left_lane):
        pre, suc = setup_with_left_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = 1
        suc.pred_direct_junction[0] = -1
        pre.planview.set_start_point(10, 0, np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (20, 3.0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (10, 3.0, 0)
        )

    def test_both_lanes_pre_pre_suc_set(self, setup_with_both_lane):
        pre, suc = setup_with_both_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = 0
        suc.pred_direct_junction[0] = 0
        suc.planview.set_start_point(10, 0, np.pi)
        suc.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            pre.planview.get_end_point(), (20, 0.0, 0)
        )
        np.testing.assert_almost_equal(
            pre.planview.get_start_point(), (10, 0.0, 0)
        )

    def test_both_lanes_pre_pre_pre_set(self, setup_with_both_lane):
        pre, suc = setup_with_both_lane
        pre.add_predecessor(xodr.ElementType.junction, 200)
        suc.add_predecessor(xodr.ElementType.junction, 200)
        pre.pred_direct_junction[2] = 0
        suc.pred_direct_junction[0] = 0
        pre.planview.set_start_point(0, 0, np.pi)
        pre.planview.adjust_geometries()
        factory = BaseAdjusterFactory(main=suc, pre=pre)
        adjuster = factory.create_road_adjuster()
        assert adjuster.adjust_roads() == 1

        np.testing.assert_almost_equal(
            suc.planview.get_end_point(), (10, 0.0, 0)
        )
        np.testing.assert_almost_equal(
            suc.planview.get_start_point(), (0, 0.0, 0)
        )
